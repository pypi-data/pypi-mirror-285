from dcim.models import Device, InventoryItem, Location, Site
from django import forms
from django.utils.translation import gettext as _
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from utilities.forms.fields import (
    CommentField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet
from utilities.forms.widgets.datetime import DatePicker

from inventory_monitor.models import Component, Contract


class ComponentForm(NetBoxModelForm):
    fieldsets = (
        FieldSet(
            "serial",
            "serial_actual",
            "partnumber",
            "asset_number",
            "project",
            "price",
            "vendor",
            "quantity",
            name=_("Component"),
        ),
        FieldSet(
            "order_contract",
            "device",
            "site",
            "location",
            "inventory_item",
            name=_("Linked"),
        ),
        FieldSet("warranty_start", "warranty_end", name=_("Dates")),
        FieldSet("tags", name=_("Misc")),
    )
    comments = CommentField(label="Comments")
    serial = forms.CharField(
        required=True,
        label="Serial",
        widget=forms.TextInput(attrs={"placeholder": "Serial"}),
    )
    serial_actual = forms.CharField(
        required=True,
        label="Serial Actual",
        widget=forms.TextInput(attrs={"placeholder": "Serial Actual"}),
    )
    partnumber = forms.CharField(
        required=False,
        label="Part Number",
    )
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label="Device",
    )
    inventory_item = DynamicModelChoiceField(
        queryset=InventoryItem.objects.all(),
        required=False,
        label="Inventory Item",
    )
    asset_number = forms.CharField(
        required=False,
        label="Inventory / AN",
    )
    project = forms.CharField(
        required=False,
        label="Project",
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label="Site",
    )
    location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        label="Location",
    )
    vendor = forms.CharField(
        required=False,
        label="Vendor",
    )
    quantity = forms.IntegerField(required=True, label="Items", initial=1, min_value=1)
    price = forms.DecimalField(
        required=True,
        label="Price",
        initial=0,
        min_value=0,
        decimal_places=2,
    )
    order_contract = DynamicModelChoiceField(
        queryset=Contract.objects.all(),
        required=False,
        label="Order Contract",
    )
    warranty_start = forms.DateField(
        required=False, label=("Warranty Start"), widget=DatePicker()
    )
    warranty_end = forms.DateField(
        required=False,
        label=("Warranty End"),
        widget=DatePicker(),
    )

    class Meta:
        model = Component
        fields = (
            "serial",
            "serial_actual",
            "partnumber",
            "device",
            "asset_number",
            "site",
            "location",
            "inventory_item",
            "project",
            "vendor",
            "quantity",
            "price",
            "order_contract",
            "warranty_start",
            "warranty_end",
            "comments",
            "tags",
        )


class ComponentFilterForm(NetBoxModelFilterSetForm):
    model = Component

    fieldsets = (
        FieldSet("q", "filter_id", "tag", name=_("Misc")),
        FieldSet(
            "order_contract",
            "site",
            "location",
            "device",
            "inventory_item",
            name=_("Linked"),
        ),
        FieldSet(
            "warranty_start",
            "warranty_start__gte",
            "warranty_start__lte",
            "warranty_end",
            "warranty_end__gte",
            "warranty_end__lte",
            name=_("Dates"),
        ),
        FieldSet(
            "serial",
            "serial_actual",
            "partnumber",
            "asset_number",
            "project",
            "vendor",
            name=_("Component"),
        ),
        FieldSet("quantity", "quantity__gte", "quantity__lte", name=_("Items")),
        FieldSet("price", "price__gte", "price__lte", name=_("Price")),
    )

    serial = forms.CharField(required=False)
    tag = TagFilterField(model)
    serial_actual = forms.CharField(required=False)
    partnumber = forms.CharField(required=False)
    device = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(), required=False, label=_("Device")
    )
    inventory_item = DynamicModelMultipleChoiceField(
        queryset=InventoryItem.objects.all(), required=False, label=_("Inventory Item")
    )
    site = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(), required=False, label=_("Site")
    )
    location = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(), required=False, label=_("Location")
    )
    quantity = forms.IntegerField(required=False, label="Items")
    quantity__gte = forms.IntegerField(required=False, label=("Items: From"))
    quantity__lte = forms.IntegerField(required=False, label=("Items: Till"))
    asset_number = forms.CharField(
        required=False,
        label="Asset Number",
    )
    project = forms.CharField(
        required=False,
        label="Project",
    )
    vendor = forms.CharField(
        required=False,
        label="Vendor",
    )
    price = forms.DecimalField(required=False)
    price__gte = forms.DecimalField(
        required=False,
        label=("Price: From"),
    )
    price__lte = forms.DecimalField(
        required=False,
        label=("Price: Till"),
    )
    order_contract = DynamicModelMultipleChoiceField(
        queryset=Contract.objects.all(), required=False, label=_("Order Contract")
    )
    warranty_start = forms.DateField(
        required=False, label=("Warranty Start"), widget=DatePicker()
    )
    warranty_start__gte = forms.DateField(
        required=False, label=("Warranty Start: From"), widget=DatePicker()
    )
    warranty_start__lte = forms.DateField(
        required=False, label=("Warranty Start: Till"), widget=DatePicker()
    )
    warranty_end = forms.DateField(
        required=False, label=("Warranty End"), widget=DatePicker()
    )
    warranty_end__gte = forms.DateField(
        required=False, label=("Warranty End: From"), widget=DatePicker()
    )
    warranty_end__lte = forms.DateField(
        required=False, label=("Warranty End: Till"), widget=DatePicker()
    )
