from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from nautobot.dcim.choices import DeviceStatusChoices, DeviceStatusChoices
# from nautobot.ipam.choices import IPRangeStatusChoices
from nautobot.dcim.models import DeviceType, Location, Rack, Device

from nautobot.apps.api import ChoiceField
from nautobot.apps.forms import NautobotBulkEditForm
from nautobot.core.forms import add_blank_choice
from nautobot.core.forms.fields import DynamicModelChoiceField
from nautobot.core.forms.widgets import APISelect

from nautobot.tenancy.models import TenantGroup, Tenant
from nautobot.core.forms import BootstrapMixin, ReturnURLForm, AddressFieldMixin, StaticSelect2, PrefixFieldMixin, DateTimePicker
from .models import SlurpitImportedDevice, SlurpitPlanning, SlurpitSetting, SlurpitIPAddress, SlurpitInterface, SlurpitPrefix
from .management.choices import SlurpitApplianceTypeChoices
from nautobot.extras.models import CustomField, Status,Role
from django.contrib.contenttypes.models import ContentType
# from nautobot.ipam.models import IPRange
from nautobot.extras.models.tags import Tag
from nautobot.tenancy.forms import TenancyForm
from nautobot.ipam.models import Namespace, VRF, IPAddress, RIR, Prefix
from nautobot.ipam.formfields import IPNetworkFormField
from nautobot.extras.forms import NautobotModelForm, StatusModelBulkEditFormMixin, TagsBulkEditFormMixin, RoleModelBulkEditFormMixin, NautobotBulkEditForm
from nautobot.dcim.forms import InterfaceCommonForm, ComponentEditForm, INTERFACE_MODE_HELP_TEXT
from nautobot.ipam import formfields
from nautobot.dcim.models import Interface

from nautobot.ipam.constants import (
    IPADDRESS_MASK_LENGTH_MAX,
    IPADDRESS_MASK_LENGTH_MIN,
    PREFIX_LENGTH_MAX,
    PREFIX_LENGTH_MIN,
)

from nautobot.core.constants import CHARFIELD_MAX_LENGTH
from nautobot.ipam.choices import IPAddressTypeChoices, PrefixTypeChoices

from nautobot.core.forms import form_from_model

class OnboardingForm(NautobotBulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=SlurpitImportedDevice.objects.all(), widget=forms.MultipleHiddenInput())
    
    interface_name = forms.CharField(
        label=_('Management Interface'),
        initial='Management1',
        max_length=200,
        required=True
    )

    device_type = forms.ChoiceField(
        choices=[],
        label=_('Device type'),
        required=True
    )
    location = DynamicModelChoiceField(
        label=_('Location'),
        queryset=Location.objects.all(),
        required=True,
        query_params={
            'site_id': '$site'
        },
        initial_params={
            'racks': '$rack'
        }
    )
    rack = DynamicModelChoiceField(
        label=_('Rack'),
        queryset=Rack.objects.all(),
        required=False,
        query_params={
            'site_id': '$site',
            'location_id': '$location',
        }
    )
    role = DynamicModelChoiceField(
        label=_('Role'),
        queryset=Role.objects.all(),
        required=True,
    )
    position = forms.DecimalField(
        label=_('Position'),
        required=False,
        help_text=_("The lowest-numbered unit occupied by the device"),
        localize=True,
        widget=APISelect(
            api_url='/api/dcim/racks/{{rack}}/elevation/',
            attrs={
                'disabled-indicator': 'device',
                'data-dynamic-params': '[{"fieldName":"face","queryParam":"face"}]'
            },
        )
    )
    # latitude = forms.DecimalField(
    #     label=_('Latitude'),
    #     max_digits=8,
    #     decimal_places=6,
    #     required=False,
    #     help_text=_("GPS coordinate in decimal format (xx.yyyyyy)")
    # )
    # longitude = forms.DecimalField(
    #     label=_('longitude'),
    #     max_digits=9,
    #     decimal_places=6,
    #     required=False,
    #     help_text=_("GPS coordinate in decimal format (xx.yyyyyy)")
    # )
    tenant_group = DynamicModelChoiceField(
        label=_('Tenant group'),
        queryset=TenantGroup.objects.all(),
        required=False,
        null_option='None',
        initial_params={
            'tenants': '$tenant'
        }
    )
    tenant = DynamicModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False,
        query_params={
            'group_id': '$tenant_group'
        }
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    status = ChoiceField(
        label=_('Status'),
        choices=add_blank_choice(DeviceStatusChoices),
        required=False
    )
    class Meta:
        model = SlurpitImportedDevice
        nullable_fields = [
            "description",
            "location",
            "tenant",
            "tenant_group",
            "status",
            # "latitude",
            # "longitude",
            "rack"
        ]
    def __init__(self, *args, **kwargs):
        device_types = kwargs['initial'].pop('device_types', None)
        super().__init__(*args, **kwargs)
        choices = []
        if device_types and len(device_types) > 1:
            choices = [('keep_original', 'Keep Original Type')]
        for dt in DeviceType.objects.all().order_by('id'):
            choices.append((dt.id, dt.model))          
        self.fields['device_type'].choices = choices

class SlurpitPlanningTableForm(BootstrapMixin, forms.Form):
    planning_id = DynamicModelChoiceField(
        queryset=SlurpitPlanning.objects.all(),
        to_field_name='planning_id',
        required=True,
        label=_("Slurpit Plans"),
    )

class SlurpitApplianceTypeForm(BootstrapMixin, forms.Form):
    model =  SlurpitSetting
    appliance_type = forms.ChoiceField(
        label=_('Data synchronization'),
        choices=add_blank_choice(SlurpitApplianceTypeChoices),
        required=False
    )

class SlurpitMappingForm(BootstrapMixin, forms.Form):
    source_field = forms.CharField(
        required=True,
        label=_("Source Field"),
        widget=forms.TextInput(attrs={"class": "form-control"}),
        help_text=_("Slurpit Device's Field"),
    )
    
    target_field = forms.ChoiceField(
        choices=[
        ],
        required=True,
        label=f"Target Field",
    )
    
    
    def __init__(self, *args, **kwargs):
        choice_name = kwargs.pop('choice_name', None) 
        doaction = kwargs.pop('doaction', None) 
        mapping_type = kwargs.pop('mapping_type', None) 
        super(SlurpitMappingForm, self).__init__(*args, **kwargs)
        
        choices = []
        
        if mapping_type == "device":
            for field in Device._meta.get_fields():
                if not field.is_relation or field.one_to_one or (field.many_to_one and field.related_model):
                    choices.append((f'device|{field.name}', f'device | {field.name}'))
        
            # Add custom fields
            device = ContentType.objects.get(app_label='dcim', model='device')
            device_custom_fields = CustomField.objects.filter(content_types=device)

            for custom_field in device_custom_fields:
                choices.append((f'device|cf_{custom_field.key}', f'device | {custom_field.key}'))
        else:
            pass
            # for field in IPRange._meta.get_fields():
            #     if not field.is_relation or field.one_to_one or (field.many_to_one and field.related_model):
            #         choices.append((f'iprange|{field.name}', f'iprange | {field.name}'))
        
        self.fields[f'target_field'].choices = choices

        if doaction != "add":
            self.fields[f'target_field'].label = choice_name
            del self.fields[f'source_field']


class SlurpitDeviceForm(BootstrapMixin, forms.Form):
    mapping_item = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=True,
        label=_("Device"),
    )

class SlurpitDeviceStatusForm(BootstrapMixin, forms.Form):
    management_status = forms.ChoiceField(
        label=_('Status'),
        choices=add_blank_choice(DeviceStatusChoices),
        required=False
    )

class SlurpitIPAddressForm(NautobotModelForm, TenancyForm, AddressFieldMixin, ReturnURLForm):
    namespace = DynamicModelChoiceField(queryset=Namespace.objects.all(), label="Namespace")

    enable_reconcile = forms.BooleanField(
        required=False,
        label=_('Enable to reconcile every incoming IPAM data')
    )

    address = IPNetworkFormField(
        required=False,
        label=_('Address')
    )

    class Meta:
        model = SlurpitIPAddress
        fields = [
            "enable_reconcile",
            "address",
            "namespace",
            "type",
            "status",
            "role",
            "dns_name",
            "description",
            "tenant_group",
            "tenant",
        ]
    
    def clean(self):
        # Pass address to the instance, because this is required to be accessible in the IPAddress.clean method
        self.instance.address = self.cleaned_data.get("address")
        namespace = self.cleaned_data.get("namespace")
        setattr(self.instance, "_namespace", namespace)
        super().clean()

    def __init__(self, *args, **kwargs):
        # Initialize helper selectors
        instance = kwargs.get("instance")
        initial = kwargs.get("initial", {}).copy()
        super().__init__(*args, **kwargs)

class SlurpitInterfaceForm(ComponentEditForm):
    
    enable_reconcile = forms.BooleanField(
        required=False,
        label=_('Enable to reconcile every incoming Interface data')
    )

    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        label="VRF",
        required=False,
        query_params={
            "device": "$device",
        },
    )

    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False
    )

    class Meta:
        model = SlurpitInterface
        fields = [
            "enable_reconcile",
            "status",
            "device",
            "name",
            "label",
            "type",
            "mode",
            "vrf",
            "description",
        ]
        widgets = {
            "type": StaticSelect2(),
            "mode": StaticSelect2(),
        }
        labels = {
            "mode": "802.1Q Mode",
        }
        help_texts = {
            "mode": INTERFACE_MODE_HELP_TEXT,
        }

class SlurpitPrefixForm(NautobotModelForm, TenancyForm, PrefixFieldMixin):
    namespace = DynamicModelChoiceField(queryset=Namespace.objects.all())
    # It is required to add prefix_length here and set it to required=False and hidden input so that
    # form validation doesn't complain and that it doesn't show in forms.
    # Ref:  https://github.com/nautobot/nautobot/issues/4550
    prefix_length = forms.IntegerField(required=False, widget=forms.HiddenInput())
    prefix = formfields.IPNetworkFormField(
        required=False
    )
    enable_reconcile = forms.BooleanField(
        required=False,
        label=_('Enable to reconcile every incoming IPAM data')
    )

    class Meta:
        model = SlurpitPrefix
        fields = [
            "prefix",
            "enable_reconcile",
            "namespace",
            "status",
            "role",
            "type",
            "description",
            "tenant_group",
            "tenant",
            "date_allocated",
        ]
        widgets = {
            "date_allocated": DateTimePicker(),
        }

    def _get_validation_exclusions(self):
        """
        By default Django excludes "network"/"prefix_length" from model validation because they are not form fields.

        This is wrong since we need those fields to be included in the validate_unique() calculation!
        """
        exclude = super()._get_validation_exclusions()
        exclude.remove("network")
        exclude.remove("prefix_length")
        return exclude

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        # Translate model ValidationError to forms.ValidationError
        try:
            return super().clean()
        except ValidationError as e:
            raise forms.ValidationError(e.message_dict) from e

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)
        return instance
    
class SlurpitIPAddressEditForm(SlurpitIPAddressForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields['enable_reconcile']

class SlurpitInterfaceEditForm(SlurpitInterfaceForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields['enable_reconcile']
        del self.fields['device']

class SlurpitPrefixEditForm(SlurpitPrefixForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields['enable_reconcile']

class SlurpitIPAddressBulkEditForm(
    TagsBulkEditFormMixin, StatusModelBulkEditFormMixin, RoleModelBulkEditFormMixin, NautobotBulkEditForm
):
    pk = forms.ModelMultipleChoiceField(queryset=SlurpitIPAddress.objects.all(), widget=forms.MultipleHiddenInput())
    mask_length = forms.IntegerField(
        min_value=IPADDRESS_MASK_LENGTH_MIN,
        max_value=IPADDRESS_MASK_LENGTH_MAX,
        required=False,
    )
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)
    dns_name = forms.CharField(max_length=CHARFIELD_MAX_LENGTH, required=False)
    description = forms.CharField(max_length=CHARFIELD_MAX_LENGTH, required=False)
    type = forms.ChoiceField(
        required=False,
        choices=add_blank_choice(IPAddressTypeChoices),
        widget=StaticSelect2(),
    )
    

    class Meta:
        nullable_fields = [
            "tenant",
            "dns_name",
            "description",
        ]
        model = SlurpitIPAddress

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["status"] = DynamicModelChoiceField(
            required=True,
            queryset=Status.objects.all(),
            query_params={"content_types": IPAddress._meta.label_lower},
        )

        self.fields["role"] = DynamicModelChoiceField(
            required=True,
            queryset=Role.objects.all(),
            query_params={"content_types": IPAddress._meta.label_lower},
        )
        
        del self.fields['add_tags']
        del self.fields['remove_tags']

class SlurpitPrefixBulkEditForm(
    TagsBulkEditFormMixin,
    StatusModelBulkEditFormMixin,
    RoleModelBulkEditFormMixin,
    NautobotBulkEditForm,
):
    pk = forms.ModelMultipleChoiceField(queryset=SlurpitPrefix.objects.all(), widget=forms.MultipleHiddenInput())
    type = forms.ChoiceField(
        choices=add_blank_choice(PrefixTypeChoices),
        required=False,
    )
    """
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label="VRF",
    )
    """
    prefix_length = forms.IntegerField(min_value=PREFIX_LENGTH_MIN, max_value=PREFIX_LENGTH_MAX, required=False)
    namespace = DynamicModelChoiceField(queryset=Namespace.objects.all(), required=False)

    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)
    date_allocated = forms.DateTimeField(required=False, widget=DateTimePicker)
    description = forms.CharField(max_length=CHARFIELD_MAX_LENGTH, required=False)

    class Meta:
        model = SlurpitPrefix
        nullable_fields = [
            # "vrf",
            "tenant",
            "date_allocated",
            "description",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["status"] = DynamicModelChoiceField(
            required=True,
            queryset=Status.objects.all(),
            query_params={"content_types": Prefix._meta.label_lower},
        )

        self.fields["role"] = DynamicModelChoiceField(
            required=False,
            queryset=Role.objects.all(),
            query_params={"content_types": Prefix._meta.label_lower},
        )
        
        del self.fields['add_tags']
        del self.fields['remove_tags']


class SlurpitInterfaceBulkEditForm(
    form_from_model(
        SlurpitInterface, ["label", "type", "mtu", "description", "mode"]
    ),
    TagsBulkEditFormMixin,
    StatusModelBulkEditFormMixin,
    NautobotBulkEditForm,
):
    pk = forms.ModelMultipleChoiceField(queryset=SlurpitInterface.objects.all(), widget=forms.MultipleHiddenInput())
    
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        label="VRF",
        required=False,
    )

    class Meta:
        nullable_fields = [
            "label",
            "parent_interface",
            "bridge",
            "lag",
            "mac_address",
            "mtu",
            "description",
            "mode",
            "untagged_vlan",
            "tagged_vlans",
            "vrf",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["status"] = DynamicModelChoiceField(
            required=True,
            queryset=Status.objects.all(),
            query_params={"content_types": Interface._meta.label_lower},
        )

        del self.fields['add_tags']
        del self.fields['remove_tags']

    def clean(self):
        super().clean()
