import django_filters
from dcim.models import DeviceType, Manufacturer
from django.db.models import Q
from netbox.filtersets import NetBoxModelFilterSet

from .models import SoftwareImage


class SoftwareImageFilterSet(NetBoxModelFilterSet):
    software_version_id = django_filters.ModelMultipleChoiceFilter(
        queryset=SoftwareImage.objects.all(),
        to_field_name="id",
        field_name="id",
    )

    class Meta:
        model = SoftwareImage
        fields = (
            "filename",
            "md5sum",
            "version",
            "comments",
        )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        
        qs_filter = (
            Q(filename__icontains=value)
            | Q(md5sum__icontains=value)
            | Q(version__icontains=value)
            | Q(comments__icontains=value)
        )
        return queryset.filter(qs_filter)


class GoldenImageFilterSet(NetBoxModelFilterSet):
    manufacturer_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Manufacturer.objects.all(),
        to_field_name="id",
        field_name="manufacturer__id",
    )

    device_type_id = django_filters.ModelMultipleChoiceFilter(
        queryset=DeviceType.objects.all(),
        to_field_name="id",
        field_name="id",
    )

    software_version_id = django_filters.ModelMultipleChoiceFilter(
        queryset=SoftwareImage.objects.all(),
        to_field_name="id",
        field_name="golden_image__software__id",
    )

    class Meta:
        model = DeviceType
        fields = (
            "id",
            "golden_image",
            "model",
        )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        
        qs_filter = (
            Q(part_number__icontains=value)
            | Q(model__icontains=value)
            | Q(golden_image__software__version__icontains=value)
            | Q(golden_image__software__filename__icontains=value)
        )
        return queryset.filter(qs_filter)