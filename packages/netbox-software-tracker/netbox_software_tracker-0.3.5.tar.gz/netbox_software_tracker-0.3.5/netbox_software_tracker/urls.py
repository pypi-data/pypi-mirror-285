from django.urls import path
from netbox.views.generic import ObjectChangeLogView

from . import views
from .models import GoldenImage, SoftwareImage

urlpatterns = (
    path("software-image/", views.SoftwareImageList.as_view(), name="softwareimage_list"),
    path("software-image/add", views.SoftwareImageAdd.as_view(), name="softwareimage_add"),
    path("software-image/delete", views.SoftwareImageBulkDelete.as_view(), name="softwareimage_bulk_delete"),
    path("software-image/<int:pk>/", views.SoftwareImageView.as_view(), name="softwareimage"),
    path("software-image/<int:pk>/edit", views.SoftwareImageEdit.as_view(), name="softwareimage_edit"),
    path("software-image/<int:pk>/delete", views.SoftwareImageDelete.as_view(), name="softwareimage_delete"),
    path("software-image/<int:pk>/changelog/", ObjectChangeLogView.as_view(), name="softwareimage_changelog", kwargs={
        "model": SoftwareImage
    }),
    path("golden-image/", views.GoldenImageListView.as_view(), name="goldenimage_list"),
    path("golden-image/assign/<int:device_type_pk>", views.GoldenImageAssignView.as_view(), name="goldenimage_add"),
    path("golden-image/<int:pk>/progress", views.GoldenImageProgressListView.as_view(), name="goldenimage_progress"),
    path("golden-image/<int:pk>/", views.GoldenImageView.as_view(), name="goldenimage"),
    path("golden-image/<int:pk>/edit/", views.GoldenImageEditView.as_view(), name="goldenimage_edit"),
    path("golden-image/<int:pk>/delete/", views.GoldenImageDeleteView.as_view(), name="goldenimage_delete"),
    path("golden-image/<int:pk>/changelog/", ObjectChangeLogView.as_view(), name="goldenimage_changelog", kwargs={
        "model": GoldenImage
    }),
)