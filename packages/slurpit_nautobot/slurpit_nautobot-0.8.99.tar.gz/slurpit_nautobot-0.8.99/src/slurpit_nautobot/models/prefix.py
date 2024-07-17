from django.db import models, transaction
import netaddr
from django.core.exceptions import MultipleObjectsReturned, ValidationError
import operator
from django.utils.functional import cached_property
from nautobot.core.utils.data import UtilizationData

# Nautobot Import
from nautobot.ipam.models import Prefix
from nautobot.extras.utils import extras_features

from nautobot.ipam.fields import VarbinaryIPField
from nautobot.extras.models import RoleField, StatusField
from nautobot.ipam import choices, constants
from nautobot.ipam.models import get_default_namespace, get_default_namespace_pk, IPAddress
from nautobot.core.models.generics import PrimaryModel
from nautobot.core.constants import CHARFIELD_MAX_LENGTH
from nautobot.core.models import BaseManager, BaseModel
from nautobot.ipam.querysets import IPAddressQuerySet, PrefixQuerySet, RIRQuerySet, VLANQuerySet
from nautobot.core.forms import fields
from django.urls import reverse
from urllib.parse import urlencode

class PrefixStatusField(StatusField):
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
            "content_types__model": "prefix",
        }

    def formfield(self, **kwargs):
        """Return a prepped formfield for use in model forms."""
        defaults = {
            "form_class": fields.DynamicModelChoiceField,
            "queryset": self.related_model.objects.all(),
            # label_lower e.g. "dcim.device"
            "query_params": {"content_types": "ipam.prefix"},
        }
        defaults.update(**kwargs)
        return super().formfield(**defaults)

class PrefixRoleField(RoleField):
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
            "content_types__model": "prefix",
        }

    def formfield(self, **kwargs):
        """Return a prepped formfield for use in model forms."""
        defaults = {
            "form_class": fields.DynamicModelChoiceField,
            "queryset": self.related_model.objects.all(),
            # label_lower e.g. "dcim.device"
            "query_params": {"content_types": "ipam.prefix"},
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
class SlurpitPrefix(PrimaryModel):
    network = VarbinaryIPField(
        null=True,
        db_index=True,
        help_text="IPv4 or IPv6 network address",
    )
    broadcast = VarbinaryIPField(null=True, db_index=True, help_text="IPv4 or IPv6 broadcast address")
    prefix_length = models.IntegerField(null=True, blank=True, db_index=True, help_text="Length of the Network prefix, in bits.")
    type = models.CharField(
        max_length=50,
        choices=choices.PrefixTypeChoices,
        default=choices.PrefixTypeChoices.TYPE_NETWORK,
    )
    status = PrefixStatusField(blank=False, null=False)
    role = PrefixRoleField(blank=True, null=True)
    ip_version = models.IntegerField(
        choices=choices.IPAddressVersionChoices,
        editable=False,
        db_index=True,
        verbose_name="IP Version",
        null=True
    )
    parent = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        related_name="slurpit_children",  # `IPAddress` to use `related_name="ip_addresses"`
        on_delete=models.PROTECT,
        help_text="The parent Prefix of this Prefix.",
    )
    namespace = models.ForeignKey(
        to="ipam.Namespace",
        on_delete=models.PROTECT,
        related_name="slurpit_prefixes",
        default=get_default_namespace_pk,
    )
    tenant = models.ForeignKey(
        to="tenancy.Tenant",
        on_delete=models.PROTECT,
        related_name="slurpit_prefixes",
        blank=True,
        null=True,
    )
    vlan = models.ForeignKey(
        to="ipam.VLAN",
        on_delete=models.PROTECT,
        related_name="slurpit_prefixes",
        blank=True,
        null=True,
        verbose_name="VLAN",
    )
    rir = models.ForeignKey(
        to="ipam.RIR",
        on_delete=models.PROTECT,
        related_name="slurpit_prefixes",
        blank=True,
        null=True,
        verbose_name="RIR",
        help_text="Regional Internet Registry responsible for this prefix",
    )

    enable_reconcile = models.BooleanField(
        default=False,
        verbose_name="Enable reconcile",
    )

    date_allocated = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Date this prefix was allocated to an RIR, reserved in IPAM, etc.",
    )
    description = models.CharField(max_length=CHARFIELD_MAX_LENGTH, blank=True)

    objects = BaseManager.from_queryset(PrefixQuerySet)()

    clone_fields = [
        "date_allocated",
        "description",
        "namespace",
        "rir",
        "role",
        "status",
        "tenant",
        "type",
        "vlan",
    ]
    """
    dynamic_group_filter_fields = {
        "vrf": "vrf_id",  # Duplicate filter fields that will be collapsed in 2.0
    }
    """

    class Meta:
        ordering = (
            "namespace",
            "ip_version",
            "network",
            "prefix_length",
        )
        index_together = [
            ["network", "broadcast", "prefix_length"],
            ["namespace", "network", "broadcast", "prefix_length"],
        ]
        unique_together = ["namespace", "network", "prefix_length"]
        verbose_name_plural = "Slurpit prefixes"
    
    def validate_unique(self, exclude=None):
        if self.namespace is None:
            if Prefix.objects.filter(
                network=self.network, prefix_length=self.prefix_length, namespace__isnull=True
            ).exists():
                raise ValidationError(
                    {"__all__": "Prefix with this Namespace, Network and Prefix length already exists."}
                )
        super().validate_unique(exclude)

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop("prefix", None)
        super().__init__(*args, **kwargs)
        self._deconstruct_prefix(prefix)

    def __str__(self):
        return str(self.prefix)

    def _deconstruct_prefix(self, prefix):
        if prefix:
            if isinstance(prefix, str):
                prefix = netaddr.IPNetwork(prefix)
            # Note that our "broadcast" field is actually the last IP address in this prefix.
            # This is different from the more accurate technical meaning of a network's broadcast address in 2 cases:
            # 1. For a point-to-point prefix (IPv4 /31 or IPv6 /127), there are two addresses in the prefix,
            #    and neither one is considered a broadcast address. We store the second address as our "broadcast".
            # 2. For a host prefix (IPv6 /32 or IPv6 /128) there's only one address in the prefix.
            #    We store this address as both the network and the "broadcast".
            # This variance is intentional in both cases as we use the "broadcast" primarily for filtering and grouping
            # of addresses and prefixes, not for packet forwarding. :-)
            broadcast = prefix.broadcast if prefix.broadcast else prefix[-1]
            self.network = str(prefix.network)
            self.broadcast = str(broadcast)
            self.prefix_length = prefix.prefixlen
            self.ip_version = prefix.version

    def delete(self, *args, **kwargs):
        """
        A Prefix with children will be impossible to delete and raise a `ProtectedError`.

        If a Prefix has children, this catches the error and explicitly updates the
        `protected_objects` from the exception setting their parent to the old parent of this
        prefix, and then this prefix will be deleted.
        """

        try:
            return super().delete(*args, **kwargs)
        except models.ProtectedError as err:
            for instance in err.protected_objects:
                # This will be either IPAddress or Prefix.
                protected_model = instance._meta.model

                # IPAddress objects must have a valid parent.
                # 3.0 TODO: uncomment this check to enforce it
                # if protected_model == IPAddress and (
                #     self.parent is None
                #     or self.parent.type != choices.PrefixTypeChoices.TYPE_NETWORK
                # ):
                if protected_model == IPAddress and self.parent is None:
                    raise models.ProtectedError(
                        msg=(
                            f"Cannot delete Prefix {self} because it has child IPAddress objects that "
                            "would no longer have a valid parent."
                        ),
                        protected_objects=err.protected_objects,
                    ) from err

                elif protected_model not in (IPAddress, Prefix):
                    raise
                # 3.0 TODO: uncomment this check to enforce it
                # Prefix objects must have a valid parent
                # elif (
                #     protected_model == Prefix
                #     and self.parent is not None
                #     and constants.PREFIX_ALLOWED_PARENT_TYPES[instance.type] != self.parent.type
                # ):
                #     raise models.ProtectedError(
                #         msg=(
                #             f"Cannot delete Prefix {self} because it has child Prefix objects that "
                #             "would no longer have a valid parent."
                #         ),
                #         protected_objects=err.protected_objects,
                #     ) from err

            # Update protected objects to use the new parent and delete the old parent (self).
            protected_pks = (po.pk for po in err.protected_objects)
            protected_objects = protected_model.objects.filter(pk__in=protected_pks)
            protected_objects.update(parent=self.parent)
            return super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if isinstance(self.prefix, netaddr.IPNetwork):
            # Clear host bits from prefix
            # This also has the subtle side effect of calling self._deconstruct_prefix(),
            # which will (re)set the broadcast and ip_version values of this instance to their correct values.
            self.prefix = self.prefix.cidr

        # Validate that creation of this prefix does not create an invalid parent/child relationship
        # 3.0 TODO: uncomment this to enforce this constraint
        # if self.parent and self.parent.type != constants.PREFIX_ALLOWED_PARENT_TYPES[self.type]:
        #     err_msg = f"{self.type.title()} prefixes cannot be children of {self.parent.type.title()} prefixes"
        #     raise ValidationError({"type": err_msg})

        # This is filtering on prefixes that share my parent and will be reparented to me
        # but are not the correct type for this parent/child relationship
        # 3.0 TODO: uncomment the below to enforce this constraint
        # invalid_children = Prefix.objects.filter(
        #     ~models.Q(id=self.id),
        #     ~models.Q(type__in=constants.PREFIX_ALLOWED_CHILD_TYPES[self.type]),
        #     parent_id=self.parent_id,
        #     prefix_length__gt=self.prefix_length,
        #     ip_version=self.ip_version,
        #     network__gte=self.network,
        #     broadcast__lte=self.broadcast,
        #     namespace=self.namespace,
        # )
        #
        # if invalid_children.exists():
        #     invalid_child_prefixes = [
        #         f"{child.cidr_str} ({child.type})" for child in invalid_children.only("network", "prefix_length")
        #     ]
        #     err_msg = (
        #         f'Creating prefix "{self.prefix}" in namespace "{self.namespace}" with type "{self.type}" '
        #         f"would create an invalid parent/child relationship with prefixes {invalid_child_prefixes}"
        #     )
        #     raise ValidationError({"__all__": err_msg})

        with transaction.atomic():
            super().save(*args, **kwargs)


    @property
    def cidr_str(self):
        if self.network is not None and self.prefix_length is not None:
            return f"{self.network}/{self.prefix_length}"
        return None

    @property
    def prefix(self):
        if self.cidr_str:
            return netaddr.IPNetwork(self.cidr_str)
        return None

    @prefix.setter
    def prefix(self, prefix):
        self._deconstruct_prefix(prefix)

    def reparent_subnets(self):
        """
        Determine the list of child Prefixes and set the parent to self.

        This query is similiar performing update from the query returned by `subnets(direct=True)`,
        but explicitly filters for subnets of the parent of this Prefix so they can be reparented.
        """
        query = Prefix.objects.select_for_update().filter(
            ~models.Q(id=self.id),  # Don't include yourself...
            parent_id=self.parent_id,
            prefix_length__gt=self.prefix_length,
            ip_version=self.ip_version,
            network__gte=self.network,
            broadcast__lte=self.broadcast,
            namespace=self.namespace,
        )

        return query.update(parent=self)

    def reparent_ips(self):
        """Determine the list of child IPAddresses and set the parent to self."""
        query = IPAddress.objects.select_for_update().filter(
            ip_version=self.ip_version,
            parent_id=self.parent_id,
            host__gte=self.network,
            host__lte=self.broadcast,
        )

        return query.update(parent=self)

    def supernets(self, direct=False, include_self=False, for_update=False):
        """
        Return supernets of this Prefix.

        Args:
            direct (bool): Whether to only return the direct ancestor.
            include_self (bool): Whether to include this Prefix in the list of supernets.
            for_update (bool): Lock rows until the end of any subsequent transactions.

        Returns:
            QuerySet
        """
        query = Prefix.objects.all()

        if for_update:
            query = query.select_for_update()

        if direct:
            return query.filter(id=self.parent_id)

        if not include_self:
            query = query.exclude(id=self.id)
    
        return query.filter(
            ip_version=self.ip_version,
            prefix_length__lte=self.prefix_length,
            network__lte=self.network,
            broadcast__gte=self.broadcast,
            namespace=self.namespace,
        )

    def subnets(self, direct=False, include_self=False, for_update=False):
        """
        Return subnets of this Prefix.

        Args:
            direct (bool): Whether to only return direct descendants.
            include_self (bool): Whether to include this Prefix in the list of subnets.
            for_update (bool): Lock rows until the end of any subsequent transactions.

        Returns:
            QuerySet
        """
        query = Prefix.objects.all()

        if for_update:
            query = query.select_for_update()

        if direct:
            return query.filter(parent_id=self.id)

        if not include_self:
            query = query.exclude(id=self.id)

        return query.filter(
            ip_version=self.ip_version,
            network__gte=self.network,
            broadcast__lte=self.broadcast,
            namespace=self.namespace,
        )

    def is_child_node(self):
        """
        Returns whether I am a child node.
        """
        return self.parent is not None

    def is_leaf_node(self):
        """
        Returns whether I am leaf node (no children).
        """
        return not self.children.exists()

    def is_root_node(self):
        """
        Returns whether I am a root node (no parent).
        """
        return self.parent is None

    def ancestors(self, ascending=False, include_self=False):
        """
        Return my ancestors descending from larger to smaller prefix lengths.

        Args:
            ascending (bool): If set, reverses the return order.
            include_self (bool): Whether to include this Prefix in the list of subnets.
        """
        query = self.supernets(include_self=include_self)
        if ascending:
            query = query.reverse()
        return query

    def descendants(self, include_self=False):
        """
        Return all of my children!

        Args:
            include_self (bool): Whether to include this Prefix in the list of subnets.
        """
        return self.subnets(include_self=include_self)

    @cached_property
    def descendants_count(self):
        """Display count of descendants."""
        return self.descendants().count()

    def root(self):
        """
        Returns the root node (the parent of all of my ancestors).
        """
        return self.ancestors().first()

    def siblings(self, include_self=False):
        """
        Return my siblings. Root nodes are siblings to other root nodes.

        Args:
            include_self (bool): Whether to include this Prefix in the list of subnets.
        """
        query = Prefix.objects.filter(parent=self.parent)
        if not include_self:
            query = query.exclude(id=self.id)

        return query

    def get_available_prefixes(self):
        """
        Return all available Prefixes within this prefix as an IPSet.
        """
        prefix = netaddr.IPSet(self.prefix)
        child_prefixes = netaddr.IPSet([child.prefix for child in self.descendants()])
        available_prefixes = prefix - child_prefixes

        return available_prefixes

    def get_available_ips(self):
        """
        Return all available IPs within this prefix as an IPSet.
        """
        prefix = netaddr.IPSet(self.prefix)
        child_ips = netaddr.IPSet([ip.address.ip for ip in self.ip_addresses.all()])
        available_ips = prefix - child_ips

        # IPv6, pool, or IPv4 /31-32 sets are fully usable
        if any(
            [
                self.ip_version == 6,
                self.type == choices.PrefixTypeChoices.TYPE_POOL,
                self.ip_version == 4 and self.prefix_length >= 31,
            ]
        ):
            return available_ips

        # Omit first and last IP address from the available set
        # For "normal" IPv4 prefixes, omit first and last addresses
        available_ips -= netaddr.IPSet(
            [
                netaddr.IPAddress(self.prefix.first),
                netaddr.IPAddress(self.prefix.last),
            ]
        )
        return available_ips

    def get_child_ips(self):
        """
        Return IP addresses with this prefix as parent.

        In a future release, if this prefix is a pool, it will return IP addresses within the pool's address space.

        Returns:
            IPAddress QuerySet
        """
        # 3.0 TODO: uncomment this to enable this logic
        # if self.type == choices.PrefixTypeChoices.TYPE_POOL:
        #     return IPAddress.objects.filter(
        #         parent__namespace=self.namespace, host__gte=self.network, host__lte=self.broadcast
        #     )
        # else:
        return self.ip_addresses.all()

    def get_first_available_prefix(self):
        """
        Return the first available child prefix within the prefix (or None).
        """
        available_prefixes = self.get_available_prefixes()
        if not available_prefixes:
            return None
        return available_prefixes.iter_cidrs()[0]

    def get_first_available_ip(self):
        """
        Return the first available IP within the prefix (or None).
        """
        available_ips = self.get_available_ips()
        if not available_ips:
            return None
        return f"{next(available_ips.__iter__())}/{self.prefix_length}"

    def get_utilization(self):
        """Return the utilization of this prefix as a UtilizationData object.

        For prefixes containing other prefixes, all direct child prefixes are considered fully utilized.

        For prefixes containing IP addresses and/or pools, pools are considered fully utilized while
        only IP addresses that are not contained within pools are added to the utilization.

        Returns:
            UtilizationData (namedtuple): (numerator, denominator)
        """
        denominator = self.prefix.size
        child_ips = netaddr.IPSet()
        child_prefixes = netaddr.IPSet()

        # 3.0 TODO: In the long term, TYPE_POOL prefixes will be disallowed from directly containing IPAddresses,
        # and the addresses will instead be parented to the containing TYPE_NETWORK prefix. It should be possible to
        # change this when that is the case, see #3873 for historical context.
        if self.type != choices.PrefixTypeChoices.TYPE_CONTAINER:
            pool_ips = IPAddress.objects.filter(
                parent__namespace=self.namespace, host__gte=self.network, host__lte=self.broadcast
            ).values_list("host", flat=True)
            child_ips = netaddr.IPSet(pool_ips)

        if self.type != choices.PrefixTypeChoices.TYPE_POOL:
            child_prefixes = netaddr.IPSet(p.prefix for p in self.children.only("network", "prefix_length").iterator())

        numerator_set = child_ips | child_prefixes

        # Exclude network and broadcast address from the denominator unless they've been assigned to an IPAddress or child pool.
        # Only applies to IPv4 network prefixes with a prefix length of /30 or shorter
        if all(
            [
                denominator > 2,
                self.type == choices.PrefixTypeChoices.TYPE_NETWORK,
                self.ip_version == 4,
            ]
        ):
            if not any([self.network in numerator_set, self.broadcast in numerator_set]):
                denominator -= 2

        return UtilizationData(numerator=numerator_set.size, denominator=denominator)
    
    def get_absolute_url(self):
        return reverse('plugins:slurpit_nautobot:reconcile_detail', args=[self.pk, 'prefix'])
    
    def get_edit_url(self):
        query_params = {'tab': "prefix"}
        base_url = reverse("plugins:slurpit_nautobot:reconcile_list")
        # Encode your query parameters and append them to the base URL
        url_with_querystring = f"{base_url}?{urlencode(query_params)}"

        base_url = reverse('plugins:slurpit_nautobot:slurpitprefix_edit', args=[self.pk])
        query_params = {'return_url': url_with_querystring}
        url_with_querystring = f"{base_url}?{urlencode(query_params)}"

        return url_with_querystring
