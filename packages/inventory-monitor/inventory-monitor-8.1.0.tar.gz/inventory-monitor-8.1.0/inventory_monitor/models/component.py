from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel
from utilities.querysets import RestrictedQuerySet


class Component(NetBoxModel):
    objects = RestrictedQuerySet.as_manager()
    serial = models.CharField(max_length=255, blank=False, null=False)
    serial_actual = models.CharField(max_length=255, blank=False, null=False)
    partnumber = models.CharField(max_length=64, blank=True, null=True)
    device = models.ForeignKey(
        to="dcim.device",
        on_delete=models.PROTECT,
        related_name="components",
        blank=True,
        null=True,
    )
    # TODO: Asset Number
    asset_number = models.CharField(max_length=255, blank=True, null=True)
    project = models.CharField(max_length=32, blank=True, null=True)
    site = models.ForeignKey(
        to="dcim.site",  # Locality,
        on_delete=models.PROTECT,
        related_name="components",
        blank=True,
        null=True,
    )
    location = models.ForeignKey(
        to="dcim.location",
        on_delete=models.PROTECT,
        related_name="components",
        blank=True,
        null=True,
    )
    inventory_item = models.ForeignKey(
        to="dcim.inventoryitem",
        on_delete=models.PROTECT,
        related_name="components",
        blank=True,
        null=True,
    )
    vendor = models.CharField(max_length=32, blank=True, null=True)
    quantity = models.PositiveIntegerField(
        blank=False,
        null=False,
        default=1,
        validators=[MinValueValidator(0)],
    )
    price = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        default=0,
    )
    order_contract = models.ForeignKey(
        to="inventory_monitor.contract",  # Contractor,
        on_delete=models.PROTECT,
        related_name="components",
        blank=True,
        null=True,
    )
    warranty_start = models.DateField(
        blank=True,
        null=True,
    )
    warranty_end = models.DateField(
        blank=True,
        null=True,
    )
    comments = models.TextField(blank=True)

    class Meta:
        ordering = (
            "serial",
            "serial_actual",
            "partnumber",
            "device",
            "asset_number",
            "project",
            "site",
            "location",
            "inventory_item",
            "vendor",
            "quantity",
            "price",
            "order_contract",
            "warranty_start",
            "warranty_end",
        )

    def __str__(self):
        return f"{self.serial}"

    def get_absolute_url(self):
        return reverse("plugins:inventory_monitor:component", args=[self.pk])

    def clean(self):
        super().clean()
