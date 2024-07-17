from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel
from utilities.querysets import RestrictedQuerySet


class ComponentService(NetBoxModel):
    objects = RestrictedQuerySet.as_manager()
    service_start = models.DateField(
        blank=True,
        null=True,
    )
    service_end = models.DateField(
        blank=True,
        null=True,
    )
    service_param = models.CharField(max_length=32, blank=True, null=True)
    service_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        default=0,
    )
    service_category = models.CharField(max_length=255, blank=True, null=True)
    service_category_vendor = models.CharField(max_length=255, blank=True, null=True)
    component = models.ForeignKey(
        to="inventory_monitor.component",
        on_delete=models.PROTECT,
        related_name="services",
        blank=True,
        null=True,
    )
    contract = models.ForeignKey(
        to="inventory_monitor.contract",
        on_delete=models.PROTECT,
        related_name="services",
        blank=True,
        null=True,
    )
    comments = models.TextField(blank=True)

    class Meta:
        ordering = (
            "service_start",
            "service_end",
            "service_param",
            "service_price",
            "service_category",
            "service_category_vendor",
            "component",
            "contract",
        )

    def __str__(self):
        return f"{self.pk}"

    def get_absolute_url(self):
        return reverse("plugins:inventory_monitor:componentservice", args=[self.pk])

    def clean(self):
        super().clean()
