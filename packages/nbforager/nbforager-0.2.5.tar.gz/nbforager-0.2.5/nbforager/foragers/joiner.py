"""Joiner."""
from operator import itemgetter

from netports import Intf
from vhelpers import vlist

from nbforager.api.base_c import BaseC
from nbforager.foragers.forager import find_objects
from nbforager.foragers.ipv4 import IPv4
from nbforager.nb_tree import NbTree
from nbforager.parser.nb_value import NbValue
from nbforager.types_ import LDAny, DAny, LStr, DiDAny, LInt, DiLDAny


class Joiner:
    """Helper methods are used to create additional keys in Netbox objects,

    representing them similarly to the WEB UI.
    """

    def __init__(self, tree: NbTree):
        """Init Joiner.
        :param NbTree tree: Contains Netbox that need to be updated similar to the WEB UI.
        """
        self.tree = tree

    # noinspection PyProtectedMember
    def init_extra_keys(self) -> None:
        """Init extra keys to represent Netbox objects similar to the WEB UI.

        :return: None. Update NbTree object.
        """
        for app, model in [
            ("dcim", "devices"),
            ("dcim", "interfaces"),
            ("virtualization", "virtual_machines"),
            ("virtualization", "interfaces"),
        ]:
            key = f"{app}/{model}/".replace("_", "-")
            reserved_keys: LStr = BaseC._reserved_keys[key]  # pylint: disable=W0212
            objects_d: DiDAny = getattr(getattr(self.tree, app), model)
            for object_d in objects_d.values():
                for _key in reserved_keys:
                    object_d[_key] = {}

        for model, key, strict in [
            ("aggregates", "prefix", True),
            ("prefixes", "prefix", True),
            ("ip_addresses", "address", False),
        ]:
            objects: DiDAny = getattr(self.tree.ipam, model)
            for data in objects.values():
                nbv = NbValue(data=data)
                family: int = nbv.family_value()
                if family != 4:
                    continue
                snet = data[key]
                data["_ipv4"] = IPv4(snet, strict=strict)
                data["_aggregate"] = {}  # DAny
                data["_super_prefix"] = {}  # DAny
                data["_sub_prefixes"] = []  # LDAny
                data["_ip_addresses"] = []  # LDAny

    def join_dcim_devices(self, **kwargs) -> None:
        """Create additional keys to represent dcim.devices similar to the WEB UI.

            In dcim.devices:

            - ``_console_ports``
            - ``_console_server_ports``
            - ``_device_bays``
            - ``_front_ports``
            - ``_interfaces``
            - ``_inventory_items``
            - ``_module_bays``
            - ``_power_outlets``
            - ``_power_ports``
            - ``_rear_ports``

            In dcim.interfaces:

            - ``_ip_addresses``

        :param kwargs: Filtering parameters.

        :return: None. Update NbTree object.
        """
        intf_ids: LInt = self._join_dcim_devices(app="dcim", **kwargs)
        params = {"id": intf_ids} if kwargs else {}
        self._join_dcim_interfaces(app="dcim", **params)

    def join_virtualization_virtual_machines(self, **kwargs) -> None:
        """Create additional keys to represent virtualization.virtual_machines.

            In virtualization.virtual_machines:

            - ``_interfaces``

            In virtualization.interfaces:

            - ``_ip_addresses``

        :param kwargs: Filtering parameters.

        :return: None. Update NbTree object.
        """
        intf_ids: LInt = self._join_dcim_devices(app="virtualization", **kwargs)
        params = {"id": intf_ids} if kwargs else {}
        self._join_dcim_interfaces(app="virtualization", **params)

    # noinspection PyProtectedMember
    def _join_dcim_devices(self, app: str, **kwargs) -> LInt:
        """Create additional key/values to represent devices/VM similar to the WEB UI.

        Create key/values: _interfaces, _front_ports, _console_ports, etc.

        :param app: Application name: "dcim", "virtualization"
        :param kwargs: Filtering parameters.

        :return: IDs of joined interfaces. Update NbTree.dcim.devices object.
        """
        model = "devices"
        key = "dcim/devices/"
        if app == "virtualization":
            model = "virtual_machines"
            key = "virtualization/virtual-machines/"
        reserved_keys: LStr = BaseC._reserved_keys[key]  # pylint: disable=W0212
        devices_d: DiDAny = getattr(getattr(self.tree, app), model)
        if kwargs:
            devices_d = {
                d["id"]: d for d in find_objects(objects=list(devices_d.values()), **kwargs)
            }

        # set values
        key = "device"
        if app == "virtualization":
            key = "virtual_machine"

        intf_ids: LInt = []  # id of joined interfaces

        models = [s.lstrip("_") for s in reserved_keys]
        for model in models:
            ports_d: DiDAny = getattr(getattr(self.tree, app), model)
            ports: LDAny = list(ports_d.values())

            # sort by interface idx
            ports_lt = [(Intf(d["name"]), d) for d in ports]
            ports_lt.sort(key=itemgetter(0))
            ports = [dict(t[1]) for t in ports_lt]

            for port_d in ports:
                name = port_d["name"]
                id_ = port_d[key]["id"]
                device_d: DAny = devices_d.get(id_, {})  # pylint: disable=E1101
                _key = f"_{model}"
                if _key in device_d:
                    device_d[_key][name] = port_d
                    intf_ids.append(id_)

        return intf_ids

    def _join_dcim_interfaces(self, app: str, **kwargs) -> None:
        """Create additional key/values for ipam/ip-addresses.

        Create key/values: _interfaces, _front_ports, _console_ports, etc.

        :param app: Application name: "dcim", "virtualization"
        :param kwargs: Filtering parameters.

        :return: None. Update NbTree object.
        """
        model = "interfaces"
        object_type = "virtualization.vminterface" if app == "virtualization" else "dcim.interface"
        intfs_d: DiDAny = getattr(getattr(self.tree, app), model)
        if kwargs:
            intfs_d = {d["id"]: d for d in find_objects(objects=list(intfs_d.values()), **kwargs)}

        app = "ipam"
        model = "ip_addresses"
        _key = f"_{model}"
        addresses_d: DiDAny = getattr(getattr(self.tree, app), model)
        addresses: LDAny = list(addresses_d.values())
        addresses.sort(key=itemgetter("address"))

        for address_d in addresses:
            address = address_d["address"]
            assigned_object_id = address_d["assigned_object_id"]
            if not assigned_object_id:
                continue
            if address_d["assigned_object_type"] != object_type:
                continue
            intf_d: DAny = intfs_d.get(assigned_object_id, {})  # pylint: disable=E1101
            if _key in intf_d:
                intf_d[_key][address] = address_d

    def join_ipam_ipv4(self) -> None:
        """Create additional keys to represent ipam similar to the WEB UI.

            Add new attributes in ipam.aggregate, ipam.prefixes, ipam.ip_addresses:

            - ``_ipv4`` IPv4 object, child of ciscoconfparse.IPv4Obj
            - ``_aggregate`` Aggregate data for ipam.prefixes and ipam.ip_addresses
            - ``_super_prefix`` Related parent prefix data for ipam.prefixes and ipam.ip_addresses
            - ``_sub_prefixes`` Related child prefixes data for ipam.prefixes and ipam.ip_addresses
            - ``_ip_addresses`` Related IP addresses data for ipam.aggregates and ipam.prefixes

        :return: None. Update NbTree object.
        """
        self._join_ipam_aggregates()
        self._join_ipam_prefixes()
        self._join_ipam_ip_addresses()
        self._join_update_sub_prefixes()

    def _join_ipam_aggregates(self) -> None:
        """Add prefixes to tree.ipam.aggregates._sub_prefixes."""
        aggregates: LDAny = self._get_aggregates_ip4()
        prefixes_d: DiLDAny = self._get_prefixes_ip4_d()
        for aggregate in aggregates:
            for depth, prefixes in prefixes_d.items():
                for prefix in prefixes:
                    _aggregate = aggregate["prefix"]
                    _prefix = prefix["prefix"]
                    if prefix["_ipv4"] in aggregate["_ipv4"]:
                        prefix["_aggregate"] = aggregate
                        if depth == 0:
                            aggregate["_sub_prefixes"].append(prefix)

    def _join_ipam_ip_addresses(self) -> None:
        """Add prefixes to tree.ipam.ip-addresses._super_prefix."""
        ip_addresses: LDAny = self._get_ip_addresses_ip4()
        prefixes_d: DiLDAny = self._get_prefixes_ip4_d()
        depths: LInt = list(prefixes_d)
        depths.reverse()

        added_addresses: LDAny = []
        for depth in depths:
            ip_addresses_ = ip_addresses.copy()
            prefixes: LDAny = prefixes_d.get(depth, [])
            for ip_address in ip_addresses_:
                for prefix in prefixes:
                    if ip_address["_ipv4"] not in prefix["_ipv4"]:
                        continue
                    if ip_address in added_addresses:
                        continue
                    ip_address["_aggregate"] = prefix["_aggregate"]
                    ip_address["_super_prefix"] = prefix
                    prefix["_ip_addresses"].append(ip_address)
                    added_addresses.append(ip_address)
            ip_addresses = [d for d in ip_addresses if d not in added_addresses]

    def _join_ipam_prefixes(self) -> None:
        """Add prefixes to tree.ipam.prefixes._sub_prefixes, _super_prefix"""
        super_prefixes = []
        prefixes_d: DiLDAny = self._get_prefixes_ip4_d()
        for depth, sub_prefixes in enumerate(prefixes_d.values()):
            if not depth:
                super_prefixes = sub_prefixes
                continue
            for super_prefix in super_prefixes:
                if super_prefix["_ipv4"].prefixlen == 32:
                    continue
                for sub_prefix in sub_prefixes:
                    if sub_prefix["_ipv4"] in (super_prefix["_ipv4"]):
                        super_prefix["_sub_prefixes"].append(sub_prefix)
                        sub_prefix["_super_prefix"] = super_prefix
            super_prefixes = sub_prefixes

    def _join_update_sub_prefixes(self) -> None:
        """Update _sub_prefixes in ipam.aggregates and ipam.prefixes.

        Remove duplicates, remove objects with improper depth, sort by IPv4.
        """
        aggregates = self._get_aggregates_ip4()
        for aggregate in aggregates:
            sub_prefixes = vlist.no_dupl(aggregate["_sub_prefixes"])
            sub_prefixes = [d for d in sub_prefixes if not d["_super_prefix"]]
            aggregate["_sub_prefixes"] = sorted(sub_prefixes, key=itemgetter("_ipv4"))

        prefixes = self._get_prefixes_ip4()
        for prefix in prefixes:
            sub_prefixes = vlist.no_dupl(prefix["_sub_prefixes"])
            prefix["_sub_prefixes"] = sorted(sub_prefixes, key=itemgetter("_ipv4"))
            ip_addresses = vlist.no_dupl(prefix["_ip_addresses"])
            prefix["_ip_addresses"] = sorted(ip_addresses, key=itemgetter("_ipv4"))

    # ============================= helpers ==============================

    def _get_aggregates_ip4(self) -> LDAny:
        """Return ipam.aggregates family=4 sorted by IPv4."""
        aggregates: LDAny = list(self.tree.ipam.aggregates.values())
        aggregates = [d for d in aggregates if d["family"]["value"] == 4]
        return sorted(aggregates, key=itemgetter("_ipv4"))

    def _get_ip_addresses_ip4(self) -> LDAny:
        """Return ipam.ip_addresses family=4 sorted by IPv4."""
        ip_addresses: LDAny = list(self.tree.ipam.ip_addresses.values())
        ip_addresses = [d for d in ip_addresses if d["family"]["value"] == 4 and d["vrf"] is None]
        return sorted(ip_addresses, key=itemgetter("_ipv4"))

    def _get_prefixes_ip4(self) -> LDAny:
        """Return ipam.prefixes family=4 sorted by IPv4."""
        prefixes: LDAny = list(self.tree.ipam.prefixes.values())
        prefixes = [d for d in prefixes if d["family"]["value"] == 4 and d["vrf"] is None]
        return sorted(prefixes, key=itemgetter("_ipv4"))

    def _get_prefixes_ip4_d(self) -> DiLDAny:
        """Split prefixes by depth.

        :return: A dictionary of prefixes where the key represents the depth
            and the value represents a list of prefixes at that depth.
        """
        prefixes: LDAny = self._get_prefixes_ip4()
        prefixes_d: DiLDAny = {d["_depth"]: [] for d in prefixes}
        for prefix in prefixes:
            depth = int(prefix["_depth"])
            prefixes_d[depth].append(prefix)
        return prefixes_d
