import django_filters
from dcim.models import Device, InventoryItem, Location
from django.db.models import Q
from extras.filters import TagFilter
from netbox.filtersets import NetBoxModelFilterSet

from inventory_monitor.models import Component, Contract


class ComponentFilterSet(NetBoxModelFilterSet):
    """
    Filter set for filtering Component objects in NetBox inventory.

    This filter set provides various filters for searching and filtering Component objects based on different criteria such as serial number, part number, device, location, inventory item, asset number, project, vendor, price, quantity, order contract, warranty start date, and warranty end date.

    Attributes:
        q (django_filters.CharFilter): Filter for searching based on a general query string.
        tag (TagFilter): Filter for filtering based on tags.
        serial (django_filters.CharFilter): Filter for filtering based on the exact serial number.
        serial_actual (django_filters.CharFilter): Filter for filtering based on the exact actual serial number.
        partnumber (django_filters.CharFilter): Filter for filtering based on the exact part number.
        device (django_filters.ModelMultipleChoiceFilter): Filter for filtering based on multiple devices.
        location (django_filters.ModelMultipleChoiceFilter): Filter for filtering based on multiple locations.
        inventory_item (django_filters.ModelMultipleChoiceFilter): Filter for filtering based on multiple inventory items.
        asset_number (django_filters.CharFilter): Filter for filtering based on the asset number.
        project (django_filters.CharFilter): Filter for filtering based on the project.
        vendor (django_filters.CharFilter): Filter for filtering based on the vendor.
        price (django_filters.NumberFilter): Filter for filtering based on the exact price.
        price__gte (django_filters.NumberFilter): Filter for filtering based on the price greater than or equal to a given value.
        price__lte (django_filters.NumberFilter): Filter for filtering based on the price less than or equal to a given value.
        quantity (django_filters.NumberFilter): Filter for filtering based on the exact quantity.
        quantity__gte (django_filters.NumberFilter): Filter for filtering based on the quantity greater than or equal to a given value.
        quantity__lte (django_filters.NumberFilter): Filter for filtering based on the quantity less than or equal to a given value.
        order_contract (django_filters.ModelMultipleChoiceFilter): Filter for filtering based on multiple order contracts.
        warranty_start (django_filters.DateFilter): Filter for filtering based on the warranty start date.
        warranty_start__gte (django_filters.DateFilter): Filter for filtering based on the warranty start date greater than or equal to a given date.
        warranty_start__lte (django_filters.DateFilter): Filter for filtering based on the warranty start date less than or equal to a given date.
        warranty_end (django_filters.DateFilter): Filter for filtering based on the warranty end date.
        warranty_end__gte (django_filters.DateFilter): Filter for filtering based on the warranty end date greater than or equal to a given date.
        warranty_end__lte (django_filters.DateFilter): Filter for filtering based on the warranty end date less than or equal to a given date.
    """

    # Rest of the code...


class ComponentFilterSet(NetBoxModelFilterSet):
    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )
    tag = TagFilter()
    serial = django_filters.CharFilter(lookup_expr="iexact", field_name="serial")
    serial_actual = django_filters.CharFilter(
        lookup_expr="iexact", field_name="serial_actual"
    )
    partnumber = django_filters.CharFilter(
        lookup_expr="iexact", field_name="partnumber"
    )
    device = django_filters.ModelMultipleChoiceFilter(
        required=False,
        field_name="device__id",
        queryset=Device.objects.all(),
        to_field_name="id",
        label="Device (ID)",
    )
    location = django_filters.ModelMultipleChoiceFilter(
        required=False,
        field_name="location__id",
        queryset=Location.objects.all(),
        to_field_name="id",
        label="Device (ID)",
    )
    inventory_item = django_filters.ModelMultipleChoiceFilter(
        required=False,
        field_name="inventory_item__id",
        queryset=InventoryItem.objects.all(),
        to_field_name="id",
        label="Inventory Item (ID)",
    )
    asset_number = django_filters.CharFilter(
        lookup_expr="icontains", field_name="asset_number"
    )
    project = django_filters.CharFilter(lookup_expr="icontains")
    vendor = django_filters.CharFilter(lookup_expr="icontains", field_name="vendor")
    price = django_filters.NumberFilter(
        required=False,
        field_name="price",
        lookup_expr="exact",
    )
    price__gte = django_filters.NumberFilter(
        required=False,
        field_name="price",
        lookup_expr="gte",
    )
    price__lte = django_filters.NumberFilter(
        required=False,
        field_name="price",
        lookup_expr="lte",
    )
    quantity = django_filters.NumberFilter(
        required=False,
        field_name="quantity",
        lookup_expr="exact",
    )
    quantity__gte = django_filters.NumberFilter(
        required=False,
        field_name="quantity",
        lookup_expr="gte",
    )
    quantity__lte = django_filters.NumberFilter(
        required=False,
        field_name="quantity",
        lookup_expr="lte",
    )
    order_contract = django_filters.ModelMultipleChoiceFilter(
        field_name="order_contract__id",
        queryset=Contract.objects.all(),
        to_field_name="id",
        label="Order Contract (ID)",
    )
    warranty_start = django_filters.DateFilter(
        field_name="warranty_start", lookup_expr="contains"
    )
    warranty_start__gte = django_filters.DateFilter(
        field_name="warranty_start", lookup_expr="gte"
    )
    warranty_start__lte = django_filters.DateFilter(
        field_name="warranty_start", lookup_expr="lte"
    )
    warranty_end = django_filters.DateFilter(
        field_name="warranty_end", lookup_expr="contains"
    )
    warranty_end__gte = django_filters.DateFilter(
        field_name="warranty_end", lookup_expr="gte"
    )
    warranty_end__lte = django_filters.DateFilter(
        field_name="warranty_end", lookup_expr="lte"
    )

    class Meta:
        model = Component
        fields = (
            "id",
            "serial",
            "serial_actual",
            "partnumber",
            "asset_number",
            "project",
            "device",
            "site",
            "vendor",
            "price",
            "order_contract",
            "warranty_start",
            "warranty_end",
            "inventory_item",
        )

    def search(self, queryset, name, value):
        serial = Q(serial__icontains=value)
        serial_actual = Q(serial_actual__icontains=value)
        device = Q(device__name__icontains=value)
        project = Q(project__icontains=value)
        site = Q(site__name__icontains=value)
        vendor = Q(vendor__icontains=value)
        order_contract = Q(order_contract__name__icontains=value)
        return queryset.filter(
            serial | serial_actual | project | site | vendor | order_contract | device
        )
