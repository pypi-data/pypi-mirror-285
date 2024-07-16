from django import forms
from ipam.models import Prefix, IPAddress, VRF
from dcim.models import Device
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms.fields import CommentField, DynamicModelChoiceField, TagFilterField
from netbox_cesnet_services_plugin.models import BGPConnection, BGPConnectionChoices
from utilities.forms.rendering import FieldSet


class BGPConnectionForm(NetBoxModelForm):
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=True,
        label="Device",
        help_text="Device",
        selector=True,
    )
    raw_next_hop = forms.GenericIPAddressField(
        required=True,
        label="Next Hop IP Address",
        help_text="IPv4 or IPv6 address (without mask)",
    )
    next_hop = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        required=True,
        label="Next Hop Interface IP Address",
        help_text="Next Hop Interface IP Address",
        selector=True,
    )
    bgp_prefix = DynamicModelChoiceField(
        queryset=Prefix.objects.all(),
        required=True,
        label="BGP Prefix",
        help_text="BGP Prefix",
        selector=True,
    )
    comments = CommentField(required=False, label="Comments", help_text="Comments")

    fieldsets = (
        FieldSet("raw_next_hop", "raw_bgp_prefix", "raw_vrf", name="Raw Data"),
        FieldSet(
            "device", "next_hop", "bgp_prefix", "vrf", name="NetBox Related Objects"
        ),
        FieldSet("import_data", name="Imported Data"),
        FieldSet("role", "tags", name="Misc"),
    )

    class Meta:
        model = BGPConnection
        fields = (
            "device",
            "raw_next_hop",
            "next_hop",
            "raw_bgp_prefix",
            "bgp_prefix",
            "raw_vrf",
            "vrf",
            "role",
            "import_data",
            "comments",
            "tags",
        )


class BGPConnectionFilterForm(NetBoxModelFilterSetForm):
    model = BGPConnection

    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label="Device",
        help_text="Device - related to Next Hop",
        # selector=True, # Selector does not work in FilterForm
    )
    raw_next_hop = forms.CharField(
        required=False,
        label="Raw Next Hop IP Address",
        help_text="IP Address | Treated as CharField => contains",
    )
    next_hop = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        label="Next Hop Interface IP Address",
        help_text="IP Address assigned to Interface",
        # selector=True, # Selector does not work in FilterForm
    )
    raw_bgp_prefix = forms.CharField(
        required=False,
        label="Raw BGP Prefix",
        help_text="Prefix | Treated as CharField => contains",
    )
    bgp_prefix = DynamicModelChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        label="BGP Prefix",
        help_text="BGP Prefix assigned to Prefix",
        # selector=True, # Selector does not work in FilterForm
    )
    raw_vrf = forms.CharField(
        required=False,
        label="Raw VRF",
        help_text="VRF | Treated as CharField => contains",
    )
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label="VRF",
        help_text="VRF assigned to BGP Connection",
    )
    tag = TagFilterField(model)
    role = forms.MultipleChoiceField(
        choices=BGPConnectionChoices, required=False, label="Role", help_text="Role"
    )

    fieldsets = (
        FieldSet("filter_id", "q"),
        FieldSet("raw_next_hop", "raw_bgp_prefix", "raw_vrf", name="Raw Data"),
        FieldSet(
            "device", "next_hop", "bgp_prefix", "vrf", name="NetBox Related Objects"
        ),
        FieldSet("role", "tag", name="Misc"),
    )
