from netbox.api.viewsets import NetBoxModelViewSet

from inventory_monitor import filtersets, models
from inventory_monitor.api.serializers import (
    ComponentSerializer,
    ComponentServiceSerializer,
    ContractorSerializer,
    ContractSerializer,
    InvoiceSerializer,
    ProbeSerializer,
)


class ProbeViewSet(NetBoxModelViewSet):
    queryset = models.Probe.objects.prefetch_related("tags", "device")
    serializer_class = ProbeSerializer
    filterset_class = filtersets.ProbeFilterSet


class ContractorViewSet(NetBoxModelViewSet):
    queryset = models.Contractor.objects.prefetch_related("tags")
    serializer_class = ContractorSerializer
    filterset_class = filtersets.ContractorFilterSet


class ContractViewSet(NetBoxModelViewSet):
    queryset = models.Contract.objects.prefetch_related("tags", "contractor")
    serializer_class = ContractSerializer
    filterset_class = filtersets.ContractFilterSet


class InvoiceViewSet(NetBoxModelViewSet):
    queryset = models.Invoice.objects.prefetch_related("tags", "contract")
    serializer_class = InvoiceSerializer
    filterset_class = filtersets.InvoiceFilterSet


class ComponentViewSet(NetBoxModelViewSet):
    queryset = models.Component.objects.prefetch_related("tags", "order_contract")
    serializer_class = ComponentSerializer
    filterset_class = filtersets.ComponentFilterSet


class ComponentServiceViewSet(NetBoxModelViewSet):
    queryset = models.ComponentService.objects.prefetch_related("tags", "contract")
    serializer_class = ComponentServiceSerializer
    filterset_class = filtersets.ComponentServiceFilterSet
