import django_filters
from django.db.models import Q
from nautobot.apps.filters import BaseFilterSet
from .models import SlurpitLog, SlurpitPlanning, SlurpitSnapshot, SlurpitImportedDevice, SlurpitPrefix, SlurpitInterface, SlurpitIPAddress
from django.utils.translation import gettext as _
from nautobot.extras.filters import CustomFieldModelFilterSetMixin
from nautobot.core.filters import SearchFilter

class LoggingFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )

    class Meta:
        model = SlurpitLog
        fields = [
            'log_time', 'level', 'category', 'message'
        ]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(level__icontains=value) | 
            Q(category__icontains=value) |
            Q(message__icontains=value)
        )

class SlurpitPlanningFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )

    class Meta:
        model = SlurpitPlanning
        fields = ["id", "name", "planning_id"]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value)
        )
    
class SlurpitSnapshotFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )

    class Meta:
        model = SlurpitSnapshot
        fields = ["id", "hostname", "planning_id"]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value)
        )

class SlurpitImportedDeviceFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )

    class Meta:
        model = SlurpitImportedDevice
        fields = ["id", "hostname"]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value)
        )
        
class SlurpitImportedDeviceFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )

    class Meta:
        model = SlurpitImportedDevice
        fields = ["id", "hostname", "device_os", "device_type", "fqdn", "brand", "ipv4"]
    
    def __init__(self, data=None, *args, **kwargs):
        if data is not None:
            # Make a mutable copy of data
            data = data.copy()
            # Remove the 'tab' parameter if it exists
            data.pop('tab', None)
        super().__init__(data, *args, **kwargs)
        
    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(device_os__icontains=value) | 
            Q(hostname__icontains=value) | 
            Q(device_type__icontains=value) | 
            Q(fqdn__icontains=value) | 
            Q(brand__icontains=value) | 
            Q(ipv4__icontains=value)
        )

class SlurpitPrefixFilterSet(django_filters.FilterSet):
    """Filterset mixin to add shared filters across all IPAM objects."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )

    class Meta:
        model = SlurpitPrefix
        fields = ["date_allocated", "id", "prefix_length"]

    def __init__(self, data=None, *args, **kwargs):
        if data is not None:
            # Make a mutable copy of data
            data = data.copy()
            # Remove the 'tab' parameter if it exists
            data.pop('tab', None)
        super().__init__(data, *args, **kwargs)
        

    def search(self, qs, name, value):
        value = value.strip()

        if not value:
            return qs

        return qs.string_search(value)

class SlurpitInterfaceFilterSet(CustomFieldModelFilterSetMixin):
    """Filterset mixin to add shared filters across all IPAM objects."""

    q = SearchFilter(
        filter_predicates={
            "name": "icontains",
            "label": "icontains",
            "description": "icontains",
        },
    )

    class Meta:
        model = SlurpitInterface
        fields = [
            "id",
            "name",
            "type",
            "enabled",
            "mode",
            "description",
            "label",
        ]

    def __init__(self, data=None, *args, **kwargs):
        if data is not None:
            # Make a mutable copy of data
            data = data.copy()
            # Remove the 'tab' parameter if it exists
            data.pop('tab', None)
        super().__init__(data, *args, **kwargs)
        

class SlurpitIPAddressFilterSet(django_filters.FilterSet):
    """Filterset mixin to add shared filters across all IPAM objects."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )

    def search(self, qs, name, value):
        value = value.strip()

        if not value:
            return qs

        return qs.string_search(value)

    class Meta:
        model = SlurpitIPAddress
        fields = ["id", "dns_name", "type", "mask_length"]

    def __init__(self, data=None, *args, **kwargs):
        if data is not None:
            # Make a mutable copy of data
            data = data.copy()
            # Remove the 'tab' parameter if it exists
            data.pop('tab', None)
        super().__init__(data, *args, **kwargs)
