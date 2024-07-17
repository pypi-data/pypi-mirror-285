import django_tables2 as tables
from netbox.tables import NetBoxTable

from inventory_monitor.models import Contractor


class ContractorTable(NetBoxTable):
    name = tables.Column(linkify=True)
    contracts_count = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = Contractor
        fields = (
            "pk",
            "id",
            "name",
            "company",
            "address",
            "comments",
            "contracts_count",
            "actions",
        )
        default_columns = ("id", "name", "company", "contracts_count")
