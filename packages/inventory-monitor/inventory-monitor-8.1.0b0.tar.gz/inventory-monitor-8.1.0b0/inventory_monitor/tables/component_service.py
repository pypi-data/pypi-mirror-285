import django_tables2 as tables
from netbox.tables import NetBoxTable

from inventory_monitor.helpers import NumberColumn
from inventory_monitor.models import ComponentService


class ComponentServiceTable(NetBoxTable):
    component = tables.Column(linkify=True)
    contract = tables.Column(linkify=True)
    service_price = NumberColumn(accessor="service_price")

    class Meta(NetBoxTable.Meta):
        model = ComponentService
        fields = (
            "pk",
            "id",
            "service_start",
            "service_end",
            "service_param",
            "service_price",
            "service_category",
            "service_category_vendor",
            "component",
            "contract",
            "comments",
            "actions",
        )
        default_columns = (
            "id",
            "contract",
            "service_start",
            "service_end",
            "service_price",
            "service_category",
            "service_category_vendor",
            "service_param",
            "actions",
        )
