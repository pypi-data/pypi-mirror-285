from dcim.models import DeviceType, Manufacturer
from django import forms
from django.template.defaulttags import register
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from utilities.forms.fields import (
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet
from .models import GoldenImage, SoftwareImage


class SoftwareImageForm(NetBoxModelForm):
    version = forms.CharField(
        required=True,
        label="Version",
        help_text="Verbose Software Version, ex: 15.5(3)M10",
    )

    filename = forms.CharField(
        required=True,
    )

    md5sum = forms.CharField(
        required=True,
        label="MD5 Checksum",
        help_text="Expected MD5 Checksum, ex: 0f58a02f3d3f1e1be8f509d2e5b58fb8",
    )

    class Meta:
        model = SoftwareImage
        fields = [
            "version",
            "filename",
            "md5sum",
            "comments",
            "tags",
        ]


class SoftwareImageFilterForm(NetBoxModelFilterSetForm):
    model = SoftwareImage
    fieldsets = (
        FieldSet("q", "tag", "software_version_id"),
    )

    software_version_id = DynamicModelMultipleChoiceField(
        queryset=SoftwareImage.objects.all(),
        required=False,
        label="Software Image",
    )

    tag = TagFilterField(SoftwareImage)


class GoldenImageForm(forms.ModelForm):
    device_type = forms.CharField(
        required=True,
        widget=forms.HiddenInput(),
        label="Device Type",
    )
    software = forms.ModelChoiceField(
        required=True,
        queryset=SoftwareImage.objects.all(),
        label="Image/Version",
    )

    class Meta:
        model = GoldenImage
        fields = ["device_type", "software"]


class GoldenImageFilterForm(NetBoxModelFilterSetForm):
    model = DeviceType
    fieldsets = (
        FieldSet("q", "manufacturer_id", "device_type_id", "software_version_id"),
    )

    manufacturer_id = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        label="Manufacturer",
    )
    device_type_id = DynamicModelMultipleChoiceField(
        queryset=DeviceType.objects.all(),
        required=False,
        label="Device Type",
        query_params={"manufacturer_id": "$manufacturer_id"},
    )
    software_version_id = DynamicModelMultipleChoiceField(
        queryset=SoftwareImage.objects.all(),
        required=False,
        label="Software Image",
    )


@register.inclusion_tag("helpers/utilization_graph.html")
def progress_graph(utilization, warning_threshold=101, danger_threshold=101):
    return {
        "utilization": utilization,
        "warning_threshold": warning_threshold,
        "danger_threshold": danger_threshold,
    }