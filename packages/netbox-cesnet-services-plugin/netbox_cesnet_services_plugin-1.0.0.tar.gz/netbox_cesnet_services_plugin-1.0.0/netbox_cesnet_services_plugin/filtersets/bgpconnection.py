from django.db.models import Q
from django.utils.translation import gettext as _
import django_filters
from netbox.filtersets import NetBoxModelFilterSet
from ipam.models import IPAddress, Prefix, VRF
from extras.filters import TagFilter
from netbox_cesnet_services_plugin.models import BGPConnection, BGPConnectionChoices
from utilities.forms.fields import DynamicMultipleChoiceField
from dcim.models import Device


class BGPConnectionFilterSet(NetBoxModelFilterSet):
    q = django_filters.CharFilter(method="search", label="Search")
    device = django_filters.ModelMultipleChoiceFilter(queryset=Device.objects.all())
    next_hop = django_filters.ModelMultipleChoiceFilter(
        queryset=IPAddress.objects.all()
    )
    bgp_prefix = django_filters.ModelMultipleChoiceFilter(queryset=Prefix.objects.all())
    vrf = django_filters.ModelMultipleChoiceFilter(queryset=VRF.objects.all())

    # TODO: as CHAR filter or as IPAddress filter?
    raw_next_hop = django_filters.CharFilter(
        # method='filter_address',
        label=_("Address"),
        lookup_expr="icontains",
    )
    raw_bgp_prefix = django_filters.CharFilter(
        # method='filter_prefix',
        label=_("Prefix"),
        lookup_expr="icontains",
    )
    raw_vrf = django_filters.CharFilter(
        label=_("VRF"),
    )

    role = DynamicMultipleChoiceField(choices=BGPConnectionChoices, required=False)

    tag = TagFilter()

    class Meta:
        model = BGPConnection
        fields = [
            "raw_next_hop",
            "next_hop",
            "raw_bgp_prefix",
            "bgp_prefix",
            "vrf",
            "role",
            "tag",
        ]

    def search(self, queryset, name, value):
        filters = (
            Q(device__name=value)
            | Q(raw_next_hop__icontains=value)
            | Q(raw_bgp_prefix__icontains=value)
            | Q(bgp_prefix__tenant__name__icontains=value)
            | Q(raw_vrf__icontains=value)
            | Q(vrf__name__icontains=value)
            | Q(role__icontains=value)
        )

        return queryset.filter(filters)

    # TODO: Filter `raw`` Address and Prefix with netaddr or treat it like a string?
    """
    def filter_address(self, queryset, name, value):
        # Let's first parse the addresses passed
        # as argument. If they are all invalid,
        # we return an empty queryset
        # TODO: Use Netaddr or ipaddress module
        value = self.parse_inet_addresses(value)
        if len(value) == 0:
            return queryset.none()
        try:
            return queryset.filter(address__net_in=value)
        except ValidationError:
            return queryset.none()

    def filter_prefix(self, queryset, name, value):
        query_values = []
        for v in value:
            try:
                query_values.append(netaddr.IPNetwork(v))
            except (AddrFormatError, ValueError):
                pass
        return queryset.filter(prefix__in=query_values)
    """
