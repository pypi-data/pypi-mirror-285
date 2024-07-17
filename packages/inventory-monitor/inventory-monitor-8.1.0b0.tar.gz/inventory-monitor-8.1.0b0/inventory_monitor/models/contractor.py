from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel
from utilities.querysets import RestrictedQuerySet


class Contractor(NetBoxModel):
    objects = RestrictedQuerySet.as_manager()
    name = models.CharField(max_length=255, blank=False, null=False)
    company = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    comments = models.TextField(blank=True)

    class Meta:
        ordering = (
            "name",
            "company",
            "address",
            "comments",
        )

    def __str__(self):
        if self.company:
            return f"{self.name}: {self.company}"
        else:
            return f"{self.name}"

    def get_absolute_url(self):
        return reverse("plugins:inventory_monitor:contractor", args=[self.pk])
