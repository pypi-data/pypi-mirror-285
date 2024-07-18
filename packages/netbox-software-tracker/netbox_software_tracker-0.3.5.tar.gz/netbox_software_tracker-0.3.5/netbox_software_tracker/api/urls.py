from netbox.api.routers import NetBoxRouter

from . import views

app_name = "software_tracker"

router = NetBoxRouter()
router.register("golden-image", views.GoldenImageViewSet)
router.register("software-image", views.SoftwareImageViewSet)

urlpatterns = router.urls
