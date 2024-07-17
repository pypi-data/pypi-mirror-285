from django.shortcuts import render
from django.views.generic import View
from netbox.views import generic

from inventory_monitor import filtersets, forms, models, tables


class ComponentServiceView(generic.ObjectView):
    queryset = models.ComponentService.objects.all()


class ComponentServiceListView(generic.ObjectListView):
    queryset = models.ComponentService.objects.all()
    filterset = filtersets.ComponentServiceFilterSet
    filterset_form = forms.ComponentServiceFilterForm
    table = tables.ComponentServiceTable


class ComponentServiceEditView(generic.ObjectEditView):
    queryset = models.ComponentService.objects.all()
    form = forms.ComponentServiceForm


class ComponentServiceDeleteView(generic.ObjectDeleteView):
    queryset = models.ComponentService.objects.all()


class ProbeDiffView(View):
    def post(self, request):
        # load from, to and device_id from request
        date_from = request.POST.get("date_from")
        date_to = request.POST.get("date_to")
        device_id = request.POST.get("device")

        probes_added = models.Probe.objects.filter(
            device_id=device_id,
            creation_time__gte=date_from,
            creation_time__lte=date_to,
        )
        probes_removed = models.Probe.objects.filter(
            device_id=device_id, time__gte=date_from, time__lte=date_to
        )

        form = forms.ProbeDiffForm(
            initial={
                "date_from": date_from,
                "date_to": date_to,
                "device": device_id,
            }
        )

        return render(
            request,
            "./inventory_monitor/probe_diff.html",
            {
                "probes_added": probes_added,
                "probes_removed": probes_removed,
                "form": form,
            },
        )

    def get(self, request):
        form = forms.ProbeDiffForm()

        return render(
            request,
            "./inventory_monitor/probe_diff.html",
            {
                "form": form,
            },
        )
