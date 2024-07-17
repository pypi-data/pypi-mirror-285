from nautobot.core.api.routers import OrderedDefaultRouter
from . import views

router = OrderedDefaultRouter()
router.APIRootView = views.SlurpitRootView
router.register("planning", views.SlurpitPlanningViewSet)
router.register("planning-data", views.SlurpitSnapshotViewSet)
router.register("device", views.DeviceViewSet)
router.register("test", views.SlurpitTestAPIView)
router.register("nautobot-device", views.SlurpitDeviceView)
router.register("ipam", views.SlurpitIPAMView)
router.register("interface", views.SlurpitInterfaceView)
router.register("prefix", views.SlurpitPrefixView)

app_name = 'slurpit-api'
urlpatterns = router.urls
