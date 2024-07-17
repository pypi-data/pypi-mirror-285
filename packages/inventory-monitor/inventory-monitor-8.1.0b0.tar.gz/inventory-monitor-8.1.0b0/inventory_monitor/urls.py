from django.urls import path
from netbox.views.generic import ObjectChangeLogView

from inventory_monitor import models, views

urlpatterns = (
    # Probes
    path("probes/", views.ProbeListView.as_view(), name="probe_list"),
    path("probes/add/", views.ProbeEditView.as_view(), name="probe_add"),
    path("probes/<int:pk>/", views.ProbeView.as_view(), name="probe"),
    path("probes/<int:pk>/edit/", views.ProbeEditView.as_view(), name="probe_edit"),
    path(
        "probes/<int:pk>/delete/", views.ProbeDeleteView.as_view(), name="probe_delete"
    ),
    path(
        "probes/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="probe_changelog",
        kwargs={"model": models.Probe},
    ),
    path(
        "probes/delete/",
        views.ProbeBulkDeleteView.as_view(),
        name="probe_bulk_delete",
    ),
    # Probe Diff
    path("probe_diff/", views.ProbeDiffView.as_view(), name="probediff"),
    # Contractors
    path("contractors/", views.ContractorListView.as_view(), name="contractor_list"),
    path("contractors/add/", views.ContractorEditView.as_view(), name="contractor_add"),
    path("contractors/<int:pk>/", views.ContractorView.as_view(), name="contractor"),
    path(
        "contractors/<int:pk>/edit/",
        views.ContractorEditView.as_view(),
        name="contractor_edit",
    ),
    path(
        "contractors/<int:pk>/delete/",
        views.ContractorDeleteView.as_view(),
        name="contractor_delete",
    ),
    path(
        "contractors/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="contractor_changelog",
        kwargs={"model": models.Contractor},
    ),
    # Contracts
    path("contracts/", views.ContractListView.as_view(), name="contract_list"),
    path("contracts/add/", views.ContractEditView.as_view(), name="contract_add"),
    path("contracts/<int:pk>/", views.ContractView.as_view(), name="contract"),
    path(
        "contracts/<int:pk>/edit/",
        views.ContractEditView.as_view(),
        name="contract_edit",
    ),
    path(
        "contracts/<int:pk>/delete/",
        views.ContractDeleteView.as_view(),
        name="contract_delete",
    ),
    path(
        "contracts/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="contract_changelog",
        kwargs={"model": models.Contract},
    ),
    # Invoice
    path("invoices/", views.InvoiceListView.as_view(), name="invoice_list"),
    path("invoices/add/", views.InvoiceEditView.as_view(), name="invoice_add"),
    path("invoices/<int:pk>/", views.InvoiceView.as_view(), name="invoice"),
    path(
        "invoices/<int:pk>/edit/", views.InvoiceEditView.as_view(), name="invoice_edit"
    ),
    path(
        "invoices/<int:pk>/delete/",
        views.InvoiceDeleteView.as_view(),
        name="invoice_delete",
    ),
    path(
        "invoices/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="invoice_changelog",
        kwargs={"model": models.Invoice},
    ),
    # Component
    path("components/", views.ComponentListView.as_view(), name="component_list"),
    path("components/add/", views.ComponentEditView.as_view(), name="component_add"),
    path("components/<int:pk>/", views.ComponentView.as_view(), name="component"),
    path(
        "components/<int:pk>/edit/",
        views.ComponentEditView.as_view(),
        name="component_edit",
    ),
    path(
        "components/<int:pk>/delete/",
        views.ComponentDeleteView.as_view(),
        name="component_delete",
    ),
    path(
        "components/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="component_changelog",
        kwargs={"model": models.Component},
    ),
    # ComponentService
    path(
        "component-services/",
        views.ComponentServiceListView.as_view(),
        name="componentservice_list",
    ),
    path(
        "component-services/add/",
        views.ComponentServiceEditView.as_view(),
        name="componentservice_add",
    ),
    path(
        "component-services/<int:pk>/",
        views.ComponentServiceView.as_view(),
        name="componentservice",
    ),
    path(
        "component-services/<int:pk>/edit/",
        views.ComponentServiceEditView.as_view(),
        name="componentservice_edit",
    ),
    path(
        "component-services/<int:pk>/delete/",
        views.ComponentServiceDeleteView.as_view(),
        name="componentservice_delete",
    ),
    path(
        "component-services/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="componentservice_changelog",
        kwargs={"model": models.ComponentService},
    ),
)
