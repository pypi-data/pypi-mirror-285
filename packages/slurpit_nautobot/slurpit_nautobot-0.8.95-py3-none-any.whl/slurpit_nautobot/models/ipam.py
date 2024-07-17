from nautobot.extras.utils import extras_features
from nautobot.core.models.generics import PrimaryModel
from nautobot.ipam.fields import VarbinaryIPField
from django.db import models
from nautobot.ipam import choices, constants
from nautobot.extras.models import RoleField, StatusField
from nautobot.ipam.validators import DNSValidator
from nautobot.core.constants import CHARFIELD_MAX_LENGTH
from nautobot.core.models import BaseManager
from nautobot.ipam.querysets import IPAddressQuerySet
import netaddr
from django.contrib.contenttypes.models import ContentType
from nautobot.extras.models import Status
from nautobot.ipam.choices import IPAddressStatusChoices, IPAddressRoleChoices
from nautobot.core.forms import fields
from nautobot.ipam.models import get_default_namespace
from nautobot.core.models.fields import ForeignKeyLimitedByContentTypes
from django.urls import reverse
from urllib.parse import urlencode

class IPAddressStatusField(StatusField):
    def get_limit_choices_to(self):
        """
        Limit this field to only objects which are assigned to this model's content-type.

        Note that this is implemented via specifying `content_types__app_label=` and `content_types__model=`
        rather than via the more obvious `content_types=ContentType.objects.get_for_model(self.model)`
        because the latter approach would involve a database query, and in some cases
        (most notably FilterSet definition) this function is called **before** database migrations can be run.
        """
        return {
            "content_types__app_label": "ipam",
            "content_types__model": "ipaddress",
        }

    def formfield(self, **kwargs):
        """Return a prepped formfield for use in model forms."""
        defaults = {
            "form_class": fields.DynamicModelChoiceField,
            "queryset": self.related_model.objects.all(),
            # label_lower e.g. "dcim.device"
            "query_params": {"content_types": "ipam.ipaddress"},
        }
        defaults.update(**kwargs)
        return super().formfield(**defaults)

class IPAddressRoleField(RoleField):
    def get_limit_choices_to(self):
        """
        Limit this field to only objects which are assigned to this model's content-type.

        Note that this is implemented via specifying `content_types__app_label=` and `content_types__model=`
        rather than via the more obvious `content_types=ContentType.objects.get_for_model(self.model)`
        because the latter approach would involve a database query, and in some cases
        (most notably FilterSet definition) this function is called **before** database migrations can be run.
        """
        return {
            "content_types__app_label": "ipam",
            "content_types__model": "ipaddress",
        }

    def formfield(self, **kwargs):
        """Return a prepped formfield for use in model forms."""
        defaults = {
            "form_class": fields.DynamicModelChoiceField,
            "queryset": self.related_model.objects.all(),
            # label_lower e.g. "dcim.device"
            "query_params": {"content_types": "ipam.ipaddress"},
        }
        defaults.update(**kwargs)
        return super().formfield(**defaults)

    
@extras_features(
    "custom_links",
    "custom_validators",
    "dynamic_groups",
    "export_templates",
    "graphql",
    "statuses",
    "webhooks",
)
class SlurpitIPAddress(PrimaryModel):
    """
    An IPAddress represents an individual IPv4 or IPv6 address and its mask. The mask length should match what is
    configured in the real world. (Typically, only loopback interfaces are configured with /32 or /128 masks.) Like
    Prefixes, IPAddresses can optionally be assigned to a VRF. An IPAddress can optionally be assigned to an Interface.
    Interfaces can have zero or more IPAddresses assigned to them.

    An IPAddress can also optionally point to a NAT inside IP, designating itself as a NAT outside IP. This is useful,
    for example, when mapping public addresses to private addresses. When an Interface has been assigned an IPAddress
    which has a NAT outside IP, that Interface's Device can use either the inside or outside IP as its primary IP.
    """

    host = VarbinaryIPField(
        null=True,
        db_index=True,
        help_text="IPv4 or IPv6 host address",
    )
    namespace = models.ForeignKey(
        to="ipam.Namespace",
        on_delete=models.PROTECT,
        related_name="slurpit_ip_namespace",
        blank=True,
        null=True,
    )
    mask_length = models.IntegerField(
        null=True, db_index=True, help_text="Length of the network mask, in bits."
    )
    type = models.CharField(
        max_length=50,
        choices=choices.IPAddressTypeChoices,
        default=choices.IPAddressTypeChoices.TYPE_HOST,
    )
    status = IPAddressStatusField(blank=False, null=False)
    role = IPAddressRoleField(blank=True, null=True)
    # ip_version is set internally just like network, and mask_length.
    ip_version = models.IntegerField(
        choices=choices.IPAddressVersionChoices,
        editable=False,
        null=True,
        db_index=True,
        verbose_name="IP Version",
    )
    tenant = models.ForeignKey(
        to="tenancy.Tenant",
        on_delete=models.PROTECT,
        related_name="slurpit_ip_addresses",
        blank=True,
        null=True,
    )
    dns_name = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH,
        blank=True,
        validators=[DNSValidator],
        verbose_name="DNS Name",
        help_text="Hostname or FQDN (not case-sensitive)",
        db_index=True,
    )

    enable_reconcile = models.BooleanField(
        default=False,
        verbose_name="Enable reconcile",
    )

    description = models.CharField(max_length=CHARFIELD_MAX_LENGTH, blank=True)

    dynamic_group_skip_missing_fields = True  # Problematic form labels for `vminterface` and `interface`

    objects = BaseManager.from_queryset(IPAddressQuerySet)()

    class Meta:
        ordering = ("ip_version", "host", "mask_length")  # address may be non-unique
        verbose_name = "Slurpit IP address"
        verbose_name_plural = "Slurpit IP addresses"
        unique_together = ["host"]

    def __init__(self, *args, address=None, **kwargs):
        super().__init__(*args, **kwargs)

        if address is not None and not self.present_in_database:
            self._deconstruct_address(address)

    def __str__(self):
        return str(self.address)

    def _deconstruct_address(self, address):
        if address:
            if isinstance(address, str):
                address = netaddr.IPNetwork(address)
            self.host = str(address.ip)
            self.mask_length = address.prefixlen
            self.ip_version = address.version


    def clean(self):
        super().clean()

    def save(self, *args, **kwargs):
        # 3.0 TODO: uncomment the below to enforce this constraint
        # if self.parent.type != choices.PrefixTypeChoices.TYPE_NETWORK:
        #     err_msg = f"IP addresses cannot be created in {self.parent.type} prefixes. You must create a network prefix first."
        #     raise ValidationError({"address": err_msg})

        self.address = self.address  # not a no-op - forces re-calling of self._deconstruct_address()

        # Force dns_name to lowercase
        if not self.dns_name.islower:
            self.dns_name = self.dns_name.lower()
            
        super().save(*args, **kwargs)

    @property
    def address(self):
        if self.host is not None and self.mask_length is not None:
            cidr = f"{self.host}/{self.mask_length}"
            return netaddr.IPNetwork(cidr)
        return None

    @address.setter
    def address(self, address):
        self._deconstruct_address(address)

    def get_absolute_url(self):
        return reverse('plugins:slurpit_nautobot:reconcile_detail', args=[self.pk, 'ipam'])

    def get_edit_url(self):
        query_params = {'tab': "ipam"}
        base_url = reverse("plugins:slurpit_nautobot:reconcile_list")
        # Encode your query parameters and append them to the base URL
        url_with_querystring = f"{base_url}?{urlencode(query_params)}"

        base_url = reverse('plugins:slurpit_nautobot:slurpitipaddress_edit', args=[self.pk])
        query_params = {'return_url': url_with_querystring}
        url_with_querystring = f"{base_url}?{urlencode(query_params)}"

        return url_with_querystring
