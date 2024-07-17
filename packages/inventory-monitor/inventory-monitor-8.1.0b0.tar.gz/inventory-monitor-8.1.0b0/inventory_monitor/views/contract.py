from core.models import ObjectType
from django.db.models import Count, OuterRef, Subquery, Value
from netbox.views import generic

from inventory_monitor import filtersets, forms, models, tables
from inventory_monitor.helpers import get_object_type_or_none

# Attempt to import NetBoxAttachment and set a flag based on its availability
try:
    from netbox_attachments.models import NetBoxAttachment

    attachments_model_exists = True
except ModuleNotFoundError:
    attachments_model_exists = False


def get_attachments_count_query(model_name):
    if not attachments_model_exists:
        return Value(0)

    object_type = get_object_type_or_none(
        app_label="inventory_monitor", model=model_name
    )

    if not object_type:
        return Value(0)

    try:
        return Subquery(
            NetBoxAttachment.objects.filter(
                object_id=OuterRef("id"), object_type=object_type
            )
            .values("object_id")
            .annotate(attachments_count=Count("*"))
            .values("attachments_count")
        )
    except (ObjectType.DoesNotExist, ValueError):
        return Value(0)


def annotate_queryset_with_counts(queryset):
    queryset = queryset.annotate(
        subcontracts_count=Count("subcontracts", distinct=True),
        invoices_count=Count("invoices", distinct=True),
        attachments_count=get_attachments_count_query("contract"),
    )
    return queryset


class ContractView(generic.ObjectView):
    queryset = annotate_queryset_with_counts(models.Contract.objects.all())

    def get_extra_context(self, request, instance):
        subcontracts = annotate_queryset_with_counts(
            models.Contract.objects.filter(parent=instance)
        )
        invoices = instance.invoices.all().annotate(
            attachments_count=get_attachments_count_query("invoice")
        )

        subcontracts_table = tables.ContractTable(subcontracts)
        subcontracts_table.configure(request)
        invoices_table = tables.InvoiceTable(invoices)
        invoices_table.configure(request)

        return {
            "subcontracts_table": subcontracts_table,
            "invoices_table": invoices_table,
        }


class ContractListView(generic.ObjectListView):
    queryset = annotate_queryset_with_counts(models.Contract.objects.all())
    filterset = filtersets.ContractFilterSet
    filterset_form = forms.ContractFilterForm
    table = tables.ContractTable


class ContractEditView(generic.ObjectEditView):
    queryset = models.Contract.objects.all().annotate(
        subcontracts_count=Count("subcontracts")
    )
    form = forms.ContractForm


class ContractDeleteView(generic.ObjectDeleteView):
    queryset = models.Contract.objects.all()
