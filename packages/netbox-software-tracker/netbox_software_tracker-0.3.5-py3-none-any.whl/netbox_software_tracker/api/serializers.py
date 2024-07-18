from dcim.api.nested_serializers import NestedDeviceTypeSerializer
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers

from .. import models


class SoftwareImageSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_software_tracker-api:softwareimage-detail")
    display = serializers.SerializerMethodField(read_only=True)

    @extend_schema_field(OpenApiTypes.STR)
    def get_display(self, obj):
        return obj.version

    class Meta:
        model = models.SoftwareImage
        fields = [
            "id",
            "url",
            "display",
            "version",
            "md5sum",
            "filename",
            "md5sum",
            "comments"
        ]


class GoldenImageSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_software_tracker-api:goldenimage-detail")

    device_type = NestedDeviceTypeSerializer()
    software = SoftwareImageSerializer()

    class Meta:
        model = models.GoldenImage
        fields = [
            "id",
            "url",
            "device_type",
            "software"
        ]

