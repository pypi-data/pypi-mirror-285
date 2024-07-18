from dcim.models import Device, DeviceType
from django.conf import settings
from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel


PLUGIN_SETTINGS = settings.PLUGINS_CONFIG.get("software_tracker", dict())
CF_NAME_SW_VERSION = PLUGIN_SETTINGS.get("CF_NAME_SW_VERSION", "software_version")


class SoftwareImage(NetBoxModel):
    version = models.CharField(
        max_length=32,
        blank=True,
    )
    md5sum = models.CharField(
        max_length=36,
        blank=True,
    )
    filename = models.CharField(
        max_length=256,
        blank=True,
    )
    comments = models.TextField(
        blank=True,
    )

    class Meta:
        ordering = ["-filename", "-version"]
        verbose_name = "Software Image"

    def __str__(self) -> str:
        return f"{self.version} - {self.filename}"

    def get_absolute_url(self) -> str:
        return reverse("plugins:netbox_software_tracker:softwareimage", kwargs={"pk": self.pk})


class GoldenImage(NetBoxModel):
    device_type = models.OneToOneField(
        to=DeviceType,
        on_delete=models.CASCADE,
        related_name="golden_image",
    )
    software = models.ForeignKey(
        to=SoftwareImage,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["device_type"]
        verbose_name = "Golden Image"

    def __str__(self) -> str:
        return f"{self.device_type.model} - {self.software}"

    def get_absolute_url(self) -> str:
        return reverse("plugins:netbox_software_tracker:goldenimage", kwargs={"pk": self.pk})

    def get_progress(self) -> float:
        total = self.device_type.instances.count()
        if total == 0:
            return 0.0
        upgraded = Device.objects.filter(
            **{f"custom_field_data__{CF_NAME_SW_VERSION}": self.software.version},
            device_type=self.device_type,
        ).count()
        return round(upgraded / total * 100, 2)
