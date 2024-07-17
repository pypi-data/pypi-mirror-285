from django.urls import include, path
from . import views
from . import models
from nautobot.dcim.models import Device

urlpatterns = (    
    ## setting ##
    path("settings/",           views.SettingsView.as_view(), name="settings"),
    
    ## onboard device ##
    path('devices/',            views.SlurpitImportedDeviceListView.as_view(), name='slurpitimporteddevice_list'),
    path('devices/onboard',     views.SlurpitImportedDeviceOnboardView.as_view(), name='onboard'),
    path('devices/import',      views.ImportDevices.as_view(), name='import'),

    ## data mapping ##
    path('data_mapping/',       views.DataMappingView.as_view(), name='data_mapping_list'),

    ## reconcile ##
    path('reconcile/',          views.ReconcileView.as_view(), name='reconcile_list'),
    path('reconcile/<uuid:pk>/<str:reconcile_type>', views.ReconcileDetailView.as_view(), name='reconcile_detail'),
    ## logging ##
    path('slurpitlog/',         views.LoggingListView.as_view(), name='slurpitlog_list'),

    path(
        "devices/<uuid:pk>/slurpit_planning/", 
        views.SlurpitPlanningning.as_view(), 
        name="slurpit_planning",
    ),

    ## Planning ##
    path("slurpitplannings/",   views.SlurpitPlanningListView.as_view(), name="slurpitplanning_list"),

    path('slurpitinterface/<uuid:pk>/edit/', views.SlurpitInterfaceEditView.as_view(), name='slurpitinterface_edit'),
    path('slurpitipaddress/<uuid:pk>/edit/', views.SlurpitIPAddressEditView.as_view(), name='slurpitipaddress_edit'),
    path('slurpitprefix/<uuid:pk>/edit/', views.SlurpitPrefixEditView.as_view(), name='slurpitprefix_edit'),
    
    path('slurpitprefix/edit/', views.SlurpitPrefixBulkEditView.as_view(), name='slurpitprefix_bulk_edit'),
    path('slurpitipaddress/edit/', views.SlurpitIPAddressBulkEditView.as_view(), name='slurpitipaddress_bulk_edit'),
    path('slurpitinterface/edit/', views.SlurpitInterfaceBulkEditView.as_view(), name='slurpitinterface_bulk_edit'),

)
