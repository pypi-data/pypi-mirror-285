from dcim.models import DeviceType
from dcim.tables.devices import DeviceTable
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from netbox.views import generic

from .filtersets import GoldenImageFilterSet, SoftwareImageFilterSet
from .forms import (
    GoldenImageFilterForm,
    GoldenImageForm,
    SoftwareImageFilterForm,
    SoftwareImageForm,
)
from .models import GoldenImage, SoftwareImage
from .tables import GoldenImageListTable, SoftwareImageListTable

PLUGIN_SETTINGS = settings.PLUGINS_CONFIG.get("software_tracker", dict())
CF_NAME_SW_VERSION = PLUGIN_SETTINGS.get("CF_NAME_SW_VERSION", "software_version")


class GoldenImageView(generic.ObjectView):
    queryset = GoldenImage.objects.prefetch_related("tags")


class GoldenImageListView(generic.ObjectListView):
    template_name = "netbox_software_tracker/goldenimage_list.html"
    queryset = DeviceType.objects.prefetch_related("tags")
    table = GoldenImageListTable
    filterset = GoldenImageFilterSet
    filterset_form = GoldenImageFilterForm
    actions = {}


class GoldenImageProgressListView(generic.ObjectListView):
    queryset = GoldenImage.objects.all()
    template_name = "netbox_software_tracker/goldenimage_progress.html"
    table = DeviceTable
    actions = {}

    def get_queryset(self, request):
        instance = GoldenImage.objects.prefetch_related("device_type").get(pk=self.kwargs["pk"])
        query = instance.device_type.instances.exclude(**{f"custom_field_data__{CF_NAME_SW_VERSION}": instance.software.version})

        return query

    def get(self, request, pk: int, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class GoldenImageDeleteView(generic.ObjectDeleteView):
    queryset = GoldenImage.objects

    def get_return_url(self, *args, **kwargs) -> str:
        return reverse("plugins:netbox_software_tracker:goldenimage_list")


class GoldenImageEditView(generic.ObjectEditView):
    queryset = GoldenImage.objects
    form = GoldenImageForm

    def get_return_url(self, *args, **kwargs) -> str:
        return reverse("plugins:netbox_software_tracker:goldenimage_list")


class GoldenImageAssignView(generic.ObjectEditView):
    queryset = GoldenImage.objects
    form = GoldenImageForm

    def get(self, request, device_type_pk: int, *args, **kwargs):
        instance = GoldenImage(device_type=DeviceType.objects.get(pk=device_type_pk))
        form = GoldenImageForm(instance=instance)
        return render(
            request,
            "generic/object_edit.html",
            {
                "object": instance,
                "form": form,
                "return_url": reverse("plugins:netbox_software_tracker:goldenimage_list"),
            },
        )

    def post(self, request, *args, **kwargs):
        device_type = request.POST.get("device_type", None)
        software = request.POST.get("software", None)
        gi = GoldenImage.objects.create(
            device_type=DeviceType.objects.get(pk=device_type), software=SoftwareImage.objects.get(pk=software)
        )
        gi.save()

        messages.success(request, f"Assigned Golden Image for {device_type}: {gi.software}")
        return redirect(reverse("plugins:netbox_software_tracker:goldenimage_list"))


class SoftwareImageView(generic.ObjectView):
    queryset = SoftwareImage.objects.all()


class SoftwareImageList(generic.ObjectListView):
    queryset = SoftwareImage.objects.all()
    table = SoftwareImageListTable
    filterset = SoftwareImageFilterSet
    filterset_form = SoftwareImageFilterForm
    #actions = ("add", "delete", "bulk_delete", "bulk_edit")


class SoftwareImageAdd(generic.ObjectEditView):
    queryset = SoftwareImage.objects.all()
    form = SoftwareImageForm

    def get_return_url(self, *args, **kwargs) -> str:
        return reverse("plugins:netbox_software_tracker:softwareimage_list")


class SoftwareImageEdit(generic.ObjectEditView):
    queryset = SoftwareImage.objects.all()
    form = SoftwareImageForm


class SoftwareImageDelete(generic.ObjectDeleteView):
    queryset = SoftwareImage.objects.all()

    def get_return_url(self, *args, **kwargs) -> str:
        return reverse("plugins:netbox_software_tracker:softwareimage_list")


class SoftwareImageBulkDelete(generic.BulkDeleteView):
    queryset = SoftwareImage.objects.all()
    table = SoftwareImageListTable
