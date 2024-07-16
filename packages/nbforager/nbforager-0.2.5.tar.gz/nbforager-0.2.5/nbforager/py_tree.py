"""Tree of pynetbox model objects."""
from typing import Dict

from pydantic import BaseModel, Field, ConfigDict
from pynetbox.core.response import Record  # type: ignore
from pynetbox.models.circuits import Circuits, CircuitTerminations  # type: ignore
from pynetbox.models.dcim import (  # type: ignore
    Cables,
    ConsolePorts,
    ConsoleServerPorts,
    DeviceTypes,
    Devices,
    FrontPorts,
    Interfaces,
    PowerOutlets,
    PowerPorts,
    RackReservations,
    Racks,
    RearPorts,
    VirtualChassis,
)
from pynetbox.models.extras import ConfigContexts, ObjectChanges  # type: ignore
from pynetbox.models.ipam import (  # type: ignore
    Aggregates,
    IpAddresses,
    IpRanges,
    Prefixes,
    Vlans,
    VlanGroups,
    AsnRanges,
)
from pynetbox.models.users import Users, Permissions  # type: ignore
from pynetbox.models.virtualization import VirtualMachines  # type: ignore
from pynetbox.models.wireless import WirelessLans  # type: ignore

DiRecord = Dict[int, Record]
# circuits
DiCircuits = Dict[int, Circuits]
DiCircuitTerminations = Dict[int, CircuitTerminations]
# dcim
DiCables = Dict[int, Cables]
DiConsolePorts = Dict[int, ConsolePorts]
DiConsoleServerPorts = Dict[int, ConsoleServerPorts]
DiDeviceTypes = Dict[int, DeviceTypes]
DiDevices = Dict[int, Devices]
DiFrontPorts = Dict[int, FrontPorts]
DiInterfaces = Dict[int, Interfaces]
DiPowerOutlets = Dict[int, PowerOutlets]
DiPowerPorts = Dict[int, PowerPorts]
DiRackReservations = Dict[int, RackReservations]
DiRacks = Dict[int, Racks]
DiRearPorts = Dict[int, RearPorts]
DiVirtualChassis = Dict[int, VirtualChassis]
# extras
DiConfigContexts = Dict[int, ConfigContexts]
DiObjectChanges = Dict[int, ObjectChanges]
# ipam
DiAggregates = Dict[int, Aggregates]
DiIpAddresses = Dict[int, IpAddresses]
DiIpRanges = Dict[int, IpRanges]
DiPrefixes = Dict[int, Prefixes]
DiVlans = Dict[int, Vlans]
DiVlanGroups = Dict[int, VlanGroups]
DiAsnRanges = Dict[int, AsnRanges]
# users
DiUsers = Dict[int, Users]
DiPermissions = Dict[int, Permissions]
# virtualization
DiVirtualMachines = Dict[int, VirtualMachines]
# wireless
DiWirelessLans = Dict[int, WirelessLans]


# noinspection DuplicatedCode
class CircuitsM(BaseModel):
    """Base for Circuits application."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    circuit_terminations: DiCircuitTerminations = Field(default={})
    circuit_types: DiRecord = Field(default={})
    circuits: DiCircuits = Field(default={})
    provider_accounts: DiRecord = Field(default={})
    provider_networks: DiRecord = Field(default={})
    providers: DiRecord = Field(default={})


class CoreM(BaseModel):
    """Base for Core application."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    data_files: DiRecord = Field(default={})
    data_sources: DiRecord = Field(default={})
    jobs: DiRecord = Field(default={})


class DcimM(BaseModel):
    """Base for DCIM application."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    cable_terminations: DiRecord = Field(default={})
    cables: DiCables = Field(default={})
    # connected_device, is not model
    console_port_templates: DiRecord = Field(default={})
    console_ports: DiConsolePorts = Field(default={})
    console_server_port_templates: DiRecord = Field(default={})
    console_server_ports: DiConsoleServerPorts = Field(default={})
    device_bay_templates: DiRecord = Field(default={})
    device_bays: DiRecord = Field(default={})
    device_roles: DiRecord = Field(default={})
    device_types: DiDeviceTypes = Field(default={})
    devices: DiDevices = Field(default={})
    front_port_templates: DiRecord = Field(default={})
    front_ports: DiFrontPorts = Field(default={})
    interface_templates: DiRecord = Field(default={})
    interfaces: DiInterfaces = Field(default={})
    inventory_item_roles: DiRecord = Field(default={})
    inventory_item_templates: DiRecord = Field(default={})
    inventory_items: DiRecord = Field(default={})
    locations: DiRecord = Field(default={})
    manufacturers: DiRecord = Field(default={})
    module_bay_templates: DiRecord = Field(default={})
    module_bays: DiRecord = Field(default={})
    module_types: DiRecord = Field(default={})
    modules: DiRecord = Field(default={})
    platforms: DiRecord = Field(default={})
    power_feeds: DiRecord = Field(default={})
    power_outlet_templates: DiRecord = Field(default={})
    power_outlets: DiPowerOutlets = Field(default={})
    power_panels: DiRecord = Field(default={})
    power_port_templates: DiRecord = Field(default={})
    power_ports: DiPowerPorts = Field(default={})
    rack_reservations: DiRackReservations = Field(default={})
    rack_roles: DiRecord = Field(default={})
    racks: DiRacks = Field(default={})
    rear_port_templates: DiRecord = Field(default={})
    rear_ports: DiRearPorts = Field(default={})
    regions: DiRecord = Field(default={})
    site_groups: DiRecord = Field(default={})
    sites: DiRecord = Field(default={})
    virtual_chassis: DiVirtualChassis = Field(default={})
    virtual_device_contexts: DiRecord = Field(default={})


class ExtrasM(BaseModel):
    """Base for extras application."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    bookmarks: DiRecord = Field(default={})
    config_contexts: DiConfigContexts = Field(default={})
    config_templates: DiRecord = Field(default={})
    content_types: DiRecord = Field(default={})
    custom_field_choice_sets: DiRecord = Field(default={})
    custom_fields: DiRecord = Field(default={})
    custom_links: DiRecord = Field(default={})
    export_templates: DiRecord = Field(default={})
    image_attachments: DiRecord = Field(default={})
    journal_entries: DiRecord = Field(default={})
    object_changes: DiObjectChanges = Field(default={})
    reports: DiRecord = Field(default={})
    saved_filters: DiRecord = Field(default={})
    scripts: DiRecord = Field(default={})
    tags: DiRecord = Field(default={})
    webhooks: DiRecord = Field(default={})


class IpamM(BaseModel):
    """Base for IPAM application."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    aggregates: DiAggregates = Field(default={})
    asn_ranges: DiAsnRanges = Field(default={})
    asns: DiRecord = Field(default={})
    fhrp_group_assignments: DiRecord = Field(default={})
    fhrp_groups: DiRecord = Field(default={})
    ip_addresses: DiIpAddresses = Field(default={})
    ip_ranges: DiIpRanges = Field(default={})
    l2vpn_terminations: DiRecord = Field(default={})  # v3.5
    l2vpns: DiRecord = Field(default={})  # v3.5
    prefixes: DiPrefixes = Field(default={})
    rirs: DiRecord = Field(default={})
    roles: DiRecord = Field(default={})
    route_targets: DiRecord = Field(default={})
    service_templates: DiRecord = Field(default={})
    services: DiRecord = Field(default={})
    vlan_groups: DiVlanGroups = Field(default={})
    vlans: DiVlans = Field(default={})
    vrfs: DiRecord = Field(default={})


# noinspection DuplicatedCode
class TenancyM(BaseModel):
    """Base for Tenancy application."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    contact_assignments: DiRecord = Field(default={})
    contact_groups: DiRecord = Field(default={})
    contact_roles: DiRecord = Field(default={})
    contacts: DiRecord = Field(default={})
    tenant_groups: DiRecord = Field(default={})
    tenants: DiRecord = Field(default={})


class UsersM(BaseModel):
    """Base for Users application."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # config: is not DiRecord
    groups: DiRecord = Field(default={})
    permissions: DiPermissions = Field(default={})
    tokens: DiRecord = Field(default={})
    users: DiUsers = Field(default={})


class VirtualizationM(BaseModel):
    """Base for Virtualization application."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    cluster_groups: DiRecord = Field(default={})
    cluster_types: DiRecord = Field(default={})
    clusters: DiRecord = Field(default={})
    interfaces: DiRecord = Field(default={})
    virtual_machines: DiVirtualMachines = Field(default={})


class WirelessM(BaseModel):
    """Base for Wireless application."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    wireless_lan_groups: DiRecord = Field(default={})
    wireless_lans: DiWirelessLans = Field(default={})
    wireless_links: DiRecord = Field(default={})


class PyTree(BaseModel):
    """Structure that holds pynetbox objects.

    Model: PyTree.{app}.{model}[id] = object.
    Example: PyTree.{app}.{model}[id] = object.

    {app} - Attribute representing application name.
    {model} - Attribute representing model name.
    [id] - Unique identifier of Netbox object.
    object - Pynetbox object, documented on https://pynetbox.readthedocs.io/
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    circuits: CircuitsM = Field(default=CircuitsM())
    core: CoreM = Field(default=CoreM())
    dcim: DcimM = Field(default=DcimM())
    extras: ExtrasM = Field(default=ExtrasM())
    ipam: IpamM = Field(default=IpamM())
    tenancy: TenancyM = Field(default=TenancyM())
    users: UsersM = Field(default=UsersM())
    virtualization: VirtualizationM = Field(default=VirtualizationM())
    wireless: WirelessM = Field(default=WirelessM())
