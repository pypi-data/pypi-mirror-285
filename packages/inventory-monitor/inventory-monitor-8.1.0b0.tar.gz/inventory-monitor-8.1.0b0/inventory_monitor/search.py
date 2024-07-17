from netbox.search import SearchIndex, register_search

from inventory_monitor.models import (
    Component,
    ComponentService,
    Contract,
    Contractor,
    Invoice,
    Probe,
)


@register_search
class ContractIndex(SearchIndex):
    model = Contract

    fields = (("name", 100), ("name_internal", 100), ("comments", 5000))


@register_search
class ContractorIndex(SearchIndex):
    model = Contractor

    fields = (("name", 100), ("company", 100), ("address", 5000), ("address", 5000))


@register_search
class InvoiceIndex(SearchIndex):
    model = Invoice
    fields = (
        ("name", 100),
        ("name_internal", 100),
        ("project", 300),
        ("comments", 5000),
    )


@register_search
class ProbeIndex(SearchIndex):
    model = Probe

    fields = (
        ("device_descriptor", 100),
        ("site_descriptor", 100),
        ("location_descriptor", 100),
        ("name", 100),
        ("serial", 100),
        ("description", 5000),
        ("comments", 5000),
    )


@register_search
class ComponentIndex(SearchIndex):
    model = Component

    fields = (
        ("serial", 100),
        ("serial_actual", 100),
        ("partnumber", 100),
        ("comments", 5000),
    )


@register_search
class ComponentServiceIndex(SearchIndex):
    model = ComponentService

    fields = (
        ("service_category", 100),
        ("service_category_vendor", 100),
        ("comments", 5000),
    )
