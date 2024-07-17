from netbox.api.serializers import NetBoxModelSerializer
from dcim.api.serializers import DeviceSerializer, SiteSerializer, LocationSerializer
from rest_framework import serializers

from inventory_monitor.models import (
    Component,
    ComponentService,
    Contract,
    Contractor,
    Invoice,
    Probe,
)


class ProbeSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:inventory_monitor-api:probe-detail"
    )
    device = DeviceSerializer(allow_null=True, nested=True)
    site = SiteSerializer(allow_null=True, nested=True)
    location = LocationSerializer(allow_null=True, nested=True)

    class Meta:
        model = Probe
        fields = [
            "id",
            "url",
            "display",
            "name",
            "time",
            "serial",
            "part",
            "device_descriptor",
            "device",
            "site_descriptor",
            "site",
            "location_descriptor",
            "location",
            "description",
            "category",
            "discovered_data",
            "tags",
            "comments",
            "custom_fields",
            "creation_time",
        ]

    brief_fields = ["id", "url", "display", "name", "serial", "time", "creation_time"]


class ContractorSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:inventory_monitor-api:contractor-detail"
    )

    class Meta:
        model = Contractor
        fields = [
            "id",
            "url",
            "display",
            "name",
            "company",
            "address",
            "tags",
            "comments",
            "custom_fields",
        ]

        brief_fields = ["id", "url", "display", "name", "company", "address"]


class ContractSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:inventory_monitor-api:contract-detail"
    )
    contractor = ContractorSerializer(nested=True)

    class Meta:
        model = Contract
        fields = [
            "id",
            "url",
            "display",
            "name",
            "name_internal",
            "contractor",
            "type",
            "contract_type",
            "price",
            "signed",
            "accepted",
            "invoicing_start",
            "invoicing_end",
            "parent",
            "tags",
            "comments",
            "custom_fields",
        ]
        brief_fields = [
            "id",
            "url",
            "display",
            "name",
            "name_internal",
        ]

    def get_fields(self):
        fields = super(ContractSerializer, self).get_fields()
        fields["parent"] = ContractSerializer(nested=True)
        return fields


class InvoiceSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:inventory_monitor-api:invoice-detail"
    )
    contract = ContractSerializer(nested=True)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "url",
            "display",
            "name",
            "name_internal",
            "project",
            "contract",
            "price",
            "invoicing_start",
            "invoicing_end",
            "tags",
            "comments",
            "custom_fields",
        ]

        brief_fields = ["id", "url", "display", "name", "name_internal"]


class ComponentSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:inventory_monitor-api:component-detail"
    )
    order_contract = ContractSerializer(nested=True)

    class Meta:
        model = Component
        fields = [
            "id",
            "url",
            "display",
            "serial",
            "serial_actual",
            "partnumber",
            "asset_number",
            "project",
            "vendor",
            "quantity",
            "price",
            "warranty_start",
            "warranty_end",
            "order_contract",
            "tags",
            "comments",
            "custom_fields",
        ]

        brief_fields = [
            "id",
            "url",
            "display",
            "serial",
            "serial_actual",
            "partnumber",
            "asset_number",
            "quantity",
            "price",
            "order_contract",
        ]


class ComponentServiceSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:inventory_monitor-api:componentservice-detail"
    )
    contract = ContractSerializer(nested=True)
    component = ComponentSerializer(nested=True)

    class Meta:
        model = ComponentService
        fields = [
            "id",
            "url",
            "display",
            "service_start",
            "service_end",
            "service_param",
            "service_price",
            "service_category",
            "service_category_vendor",
            "component",
            "contract",
            "tags",
            "comments",
            "custom_fields",
        ]

        brief_fields = [
            "id",
            "url",
            "display",
            "service_start",
            "service_end",
            "service_price",
            "component",
            "contract",
        ]
