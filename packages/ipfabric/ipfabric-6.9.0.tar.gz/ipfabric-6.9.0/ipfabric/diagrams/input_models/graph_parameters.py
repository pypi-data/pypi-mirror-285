from __future__ import annotations as _annotations

import os
import re
from copy import deepcopy
from ipaddress import IPv4Interface
from typing import Optional, Union, List, TYPE_CHECKING

try:
    from typing import Annotated  # py38 required Annotated
except ImportError:
    from typing_extensions import Annotated

if TYPE_CHECKING:
    from pydantic._internal import _repr

from pydantic import field_validator, BaseModel, Field, AliasChoices
from pydantic.functional_validators import BeforeValidator
from ipfabric.tools import validate_ip_network_str, VALID_IP

from .constants import VALID_LAYOUTS

PYDANTIC_EXTRAS = os.getenv("IPFABRIC_PYDANTIC_EXTRAS", "allow")
PORT_REGEX = re.compile(r"^\d*$|^\d*-\d*$")
ALL_NETWORK = "$main"

IPv4 = Annotated[Union[str, VALID_IP], BeforeValidator(validate_ip_network_str)]


class Instance(BaseModel, extra=PYDANTIC_EXTRAS):
    rootId: str
    vlanId: int
    visible: bool = True
    grouped: bool = True


class STPInstances(BaseModel, extra=PYDANTIC_EXTRAS):
    isolate: bool = False
    instances: List[Instance] = Field(default_factory=list)


class Technologies(BaseModel, extra=PYDANTIC_EXTRAS):
    expandDeviceGroups: Optional[List[str]] = Field(default_factory=list)
    stpInstances: Optional[STPInstances] = None

    def technologies_parameters(self) -> dict:
        params = dict(expandDeviceGroups=self.expandDeviceGroups)
        if self.stpInstances:
            params["stpInstances"] = dict(isolate=self.stpInstances.isolate, instances=list())
            for i in self.stpInstances.instances:
                params["stpInstances"]["instances"].append(vars(i))
        return params


class ICMP(BaseModel, extra=PYDANTIC_EXTRAS):
    type: int
    code: int


class OtherOptions(BaseModel, extra=PYDANTIC_EXTRAS):
    applications: Optional[str] = ".*"
    tracked: Optional[bool] = False


class EntryPoint(BaseModel, extra=PYDANTIC_EXTRAS):
    sn: str = Field(title="Serial Number", description="IP Fabric Unique Device Serial Number API column sn")
    iface: str = Field(
        title="Interface", description="Interface to use as entry point. This is the intName not nameOriginal."
    )
    hostname: str = Field(title="Hostname", description="Hostname of the Device")


class Algorithm(BaseModel):
    """Default is automatic. Adding entryPoints will change to userDefined."""

    vrf: Optional[str] = None
    entryPoints: Optional[List[EntryPoint]] = None

    @property
    def type(self):
        return "userDefined" if self.entryPoints else "automatic"

    def algorithm_parameters(self) -> dict:
        if self.entryPoints:
            return dict(type=self.type, entryPoints=[vars(e) for e in self.entryPoints])
        else:
            return dict(type=self.type, vrf=self.vrf) if self.vrf else dict(type=self.type)


class PathLookup(BaseModel, extra=PYDANTIC_EXTRAS):
    protocol: Optional[str] = Field("tcp", title="Protocol", description="Valid protocols are tcp, udp, or icmp.")
    srcPorts: Optional[Union[str, int]] = Field(
        "1024-65535",
        title="Source Ports",
        description="Source ports if protocol is tcp or udp. "
        "Can be comma separated, a range using -, or any combination.",
    )
    dstPorts: Optional[Union[str, int]] = Field(
        "80,443",
        title="Destination Ports",
        description="Destination ports if protocol is tcp or udp. "
        "Can be comma separated, a range using -, or any combination.",
    )
    tcpFlags: Optional[list] = Field(
        default_factory=list,
        title="TCP Flags",
        description="Optional additional flags if protocol = TCP. "
        "Valid flags are ['ack', 'fin', 'psh', 'rst', 'syn', 'urg']",
        validation_alias=AliasChoices("tcpFlags", "flags"),
    )
    icmp: Optional[ICMP] = Field(
        ICMP(type=0, code=0),
        title="ICMP Packet",
        description="Default is Echo Reply (type=0, code=0). You can pass in an ICMP model from ipfabric.diagrams.icmp "
        "or specify your own values like {'type': 1, 'code': 2}.",
    )
    ttl: Optional[int] = Field(128, title="Time To Live", description="TTL value, default is 128.")
    fragmentOffset: Optional[int] = Field(
        0, title="Fragment Offset", description="Fragment Offset value, default is 0."
    )
    securedPath: Optional[bool] = True
    enableRegions: Optional[bool] = False
    srcRegions: Optional[str] = ".*"
    dstRegions: Optional[str] = ".*"
    otherOptions: Optional[OtherOptions] = Field(default_factory=OtherOptions)
    firstHopAlgorithm: Optional[Algorithm] = Field(default_factory=Algorithm)

    def __repr_args__(self) -> _repr.ReprArgs:
        for k, v in self.__dict__.items():
            if (
                v is None
                or (k == "icmp" and self.protocol != "icmp")
                or (k in ["fragmentOffset", "srcPorts", "dstPorts"] and self.protocol == "icmp")
                or (k == "tcpFlags" and self.protocol != "tcp")
                or v == self.model_fields[k].default
                or (self.model_fields[k].default_factory and v == self.model_fields[k].default_factory())
            ):
                continue
            field = self.model_fields.get(k)
            if field and field.repr:
                yield k, v
        yield from ((k, getattr(self, k)) for k, v in self.model_computed_fields.items() if v.repr)

    @field_validator("protocol")
    @classmethod
    def _valid_protocols(cls, v):
        if v.lower() not in ["tcp", "udp", "icmp"]:
            raise ValueError(f'Protocol "{v}" not in ["tcp", "udp", "icmp"]')
        return v.lower()

    @field_validator("srcPorts", "dstPorts")
    @classmethod
    def _check_ports(cls, v):
        ports = str(v).replace(" ", "").split(",")
        for p in ports:
            if not PORT_REGEX.match(p):
                raise ValueError(
                    f'Ports "{v}" is not in the valid syntax, examples: ["80", "80,443", "0-1024", "80,8000-8100,8443"]'
                )
            if "-" in p:
                pn = p.split("-")
                if int(pn[0]) >= int(pn[1]):
                    raise ValueError(f'Ports "{p}" is invalid. {pn[0]} must be smaller than {pn[1]}.')
        return str(",".join(ports))

    @field_validator("tcpFlags")
    @classmethod
    def _valid_flags(cls, v):
        v = [f.lower() for f in v] if v else list()
        if all(f in ["ack", "fin", "psh", "rst", "syn", "urg"] for f in v):
            return v
        raise ValueError(f'TCP Flags "{v}" must be None or combination of ["ack", "fin", "psh", "rst", "syn", "urg"]')

    def _l4_options(self):
        if self.protocol == "icmp":
            return dict(type=self.icmp.type, code=self.icmp.code)
        elif self.protocol == "udp":
            return dict(srcPorts=self.srcPorts, dstPorts=self.dstPorts)
        else:
            return dict(srcPorts=self.srcPorts, dstPorts=self.dstPorts, flags=self.tcpFlags)

    def base_parameters(self) -> dict:
        return dict(
            type="pathLookup",
            groupBy="siteName",
            protocol=self.protocol,
            ttl=self.ttl,
            fragmentOffset=self.fragmentOffset,
            securedPath=self.securedPath,
            enableRegions=self.enableRegions,
            srcRegions=self.srcRegions,
            dstRegions=self.dstRegions,
            l4Options=self._l4_options(),
            otherOptions=vars(self.otherOptions),
            firstHopAlgorithm=self.firstHopAlgorithm.algorithm_parameters(),
        )

    @staticmethod
    def swap_src_dst(parameters: dict) -> dict:
        params = deepcopy(parameters)
        if params["protocol"] != "icmp":
            params["l4Options"]["srcPorts"], params["l4Options"]["dstPorts"] = (
                params["l4Options"]["dstPorts"],
                params["l4Options"]["srcPorts"],
            )
        params["srcRegions"], params["dstRegions"] = params["dstRegions"], params["srcRegions"]
        params["startingPoint"], params["destinationPoint"] = params["destinationPoint"], params["startingPoint"]
        return params


class Multicast(PathLookup, BaseModel, extra=PYDANTIC_EXTRAS):
    group: IPv4
    source: IPv4
    receiver: Optional[IPv4] = None

    @field_validator("group")
    @classmethod
    def _valid_group(cls, v):
        ip = IPv4Interface(v)
        if not ip.network.is_multicast:
            raise ValueError(f'Group IP "{v}" is not a valid Multicast Address.')
        return v

    def parameters(self) -> dict:
        parameters = self.base_parameters()
        parameters.update(
            dict(
                pathLookupType="multicast",
                group=str(self.group),
                source=str(self.source),
            )
        )
        if self.receiver:
            parameters["receiver"] = str(self.receiver)
        return parameters


class Unicast(PathLookup, BaseModel, extra=PYDANTIC_EXTRAS):
    startingPoint: IPv4 = Field(title="Source IP Address or Subnet")
    destinationPoint: IPv4 = Field(title="Destination IP Address or Subnet")

    def parameters(self, swap: bool = False) -> dict:
        parameters = self.base_parameters()
        parameters.update(
            dict(
                pathLookupType="unicast",
                networkMode=self._check_subnets(),
                startingPoint=self.startingPoint,
                destinationPoint=self.destinationPoint,
            )
        )
        return self.swap_src_dst(parameters) if swap else parameters

    def _check_subnets(self) -> bool:
        """
        Checks for valid IP Addresses or Subnet
        :param ips: ip addresses
        :return: True if a subnet is found to set to networkMode, False if only hosts
        """
        masks = {IPv4Interface(ip).network.prefixlen for ip in [self.startingPoint, self.destinationPoint]}
        return True if masks != {32} else False


class Host2GW(BaseModel, extra=PYDANTIC_EXTRAS):
    startingPoint: IPv4
    vrf: Optional[str] = None

    def parameters(self) -> dict:
        parameters = dict(
            pathLookupType="hostToDefaultGW",
            type="pathLookup",
            groupBy="siteName",
            startingPoint=self.startingPoint,
        )
        if self.vrf:
            parameters["vrf"] = self.vrf
        return parameters

    def __repr_args__(self) -> _repr.ReprArgs:
        for k, v in self.__dict__.items():
            if v is None:
                continue
            field = self.model_fields.get(k)
            if field and field.repr:
                yield k, v
        yield from ((k, getattr(self, k)) for k, v in self.model_computed_fields.items() if v.repr)


class Layout(BaseModel, extra=PYDANTIC_EXTRAS):
    path: str
    layout: str

    @field_validator("layout")
    @classmethod
    def _valid_layout(cls, v):
        if v and v not in VALID_LAYOUTS:
            raise ValueError(f'Layout "{v}" is not in the valid layouts of {VALID_LAYOUTS}')
        return v


class Network(BaseModel, extra=PYDANTIC_EXTRAS):
    sites: Optional[Union[str, List[str]]] = Field(default_factory=list)
    all_network: Optional[bool] = Field(True, description="Show all sites as clouds, UI option 'All Network'")
    layouts: Optional[List[Layout]] = None
    technologies: Optional[Technologies] = None

    def __repr_args__(self) -> _repr.ReprArgs:
        for k, v in self.__dict__.items():
            if v is None or (k == "technologies" and self.technologies == Technologies(stpInstances=STPInstances())):
                continue
            if k == "all_network" and ALL_NETWORK in self.sites:
                v = True
            if k == "sites" and ALL_NETWORK in self.sites:
                v = list(set(self.sites).difference({"$main"}))
            field = self.model_fields.get(k)
            if field and field.repr:
                yield k, v
        yield from ((k, getattr(self, k)) for k, v in self.model_computed_fields.items() if v.repr)

    @field_validator("sites")
    @classmethod
    def _format_paths(cls, v):
        if isinstance(v, str):
            return [v]
        return v

    def parameters(self) -> dict:
        parameters = dict(type="topology", groupBy="siteName", paths=self.sites.copy())
        if self.all_network and ALL_NETWORK not in parameters["paths"]:
            parameters["paths"].append(ALL_NETWORK)
        if self.layouts:
            parameters["layouts"] = [vars(layout) for layout in self.layouts]
        if self.technologies:
            parameters["technologies"] = self.technologies.technologies_parameters()
        return parameters
