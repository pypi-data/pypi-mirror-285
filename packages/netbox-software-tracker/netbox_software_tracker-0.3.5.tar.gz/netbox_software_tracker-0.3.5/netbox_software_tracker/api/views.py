from netbox.api.viewsets import NetBoxModelViewSet

from .. import models
from ..filtersets import SoftwareImageFilterSet
from .serializers import GoldenImageSerializer, SoftwareImageSerializer


class GoldenImageViewSet(NetBoxModelViewSet):
    queryset = models.GoldenImage.objects.all()
    serializer_class = GoldenImageSerializer


class SoftwareImageViewSet(NetBoxModelViewSet):
    queryset = models.SoftwareImage.objects.all()
    serializer_class = SoftwareImageSerializer
    filterset_class = SoftwareImageFilterSet