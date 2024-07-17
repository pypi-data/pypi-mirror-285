import django_tables2 as tables
from netbox.tables import NetBoxTable, columns

from inventory_monitor.helpers import (
    TEMPLATE_SERVICES_CONTRACTS,
    TEMPLATE_SERVICES_END,
    NumberColumn,
)
from inventory_monitor.models import Component


class ComponentTable(NetBoxTable):
    serial = tables.Column(linkify=True)
    device = tables.Column(linkify=True)
    inventory_item = tables.Column(linkify=True)
    site = tables.Column(linkify=True)
    location = tables.Column(linkify=True)
    order_contract = tables.Column(linkify=True)
    price = NumberColumn()
    tags = columns.TagColumn()
    services_to = columns.TemplateColumn(template_code=TEMPLATE_SERVICES_END)
    services_contracts = tables.TemplateColumn(
        template_code=TEMPLATE_SERVICES_CONTRACTS
    )

    class Meta(NetBoxTable.Meta):
        model = Component
        fields = (
            "pk",
            "id",
            "serial",
            "serial_actual",
            "partnumber",
            "device",
            "asset_number",
            "project",
            "location",
            "site",
            "vendor",
            "quantity",
            "price",
            "order_contract",
            "inventory_item",
            "warranty_start",
            "warranty_end",
            "comments",
            "actions",
            "tags",
            "services_count",
            "services_contracts",
            "services_to",
        )

        default_columns = (
            "id",
            "serial",
            "serial_actual",
            "device",
            "asset_number",
            "site",
            "quantity",
            "price",
            "actions",
        )
