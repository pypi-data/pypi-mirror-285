from __future__ import annotations as _annotations

import os
from typing import Optional, List, Union, TYPE_CHECKING, Literal
from uuid import UUID

from pydantic import field_validator, BaseModel, Field, PrivateAttr
from pydantic_extra_types.color import ColorType, Color

if TYPE_CHECKING:
    from pydantic._internal import _repr

from ipfabric.tools import valid_snapshot
from .constants import (
    VALID_DEV_TYPES,
    DEFAULT_NETWORK,
    DEFAULT_PATHLOOKUP,
    VALID_NET_PROTOCOLS,
    VALID_PROTOCOL_LABELS,
    VALID_PATH_PROTOCOLS,
    HIDDEN_DEV_TYPES,
)

PYDANTIC_EXTRAS = os.getenv("IPFABRIC_PYDANTIC_EXTRAS", "allow")


class Color(Color):
    """https://github.com/pydantic/pydantic-extra-types/issues/140"""
    def __repr_args__(self) -> _repr.ReprArgs:
        return [(None, self.as_named(fallback=True))]

    def __repr__(self) -> str:
        return self.__repr_str__(", ")


class Style(BaseModel, extra=PYDANTIC_EXTRAS):
    color: Union[ColorType]
    pattern: Optional[str] = "solid"
    thicknessThresholds: Optional[List[int]] = [2, 4, 8]

    @field_validator("pattern")
    @classmethod
    def _valid_patterns(cls, v):
        if v.lower() not in ["solid", "dashed", "dotted"]:
            raise ValueError(f'Pattern "{v}" not in ["solid", "dashed", "dotted"]')
        return v.lower()

    @field_validator("color")
    @classmethod
    def _parse_color(cls, v):
        return Color(v)

    def style_settings(self) -> dict:
        return dict(color=self.color.as_hex(), pattern=self.pattern, thicknessThresholds=self.thicknessThresholds)


class Setting(BaseModel, extra=PYDANTIC_EXTRAS):
    name: str
    style: Style
    type: Literal["protocol", "pathLookupEdge", "group"]
    visible: bool = True
    grouped: bool = True
    id: Optional[UUID] = None

    def base_settings(self) -> dict:
        return dict(
            name=self.name,
            visible=self.visible,
            grouped=self.grouped,
            style=self.style.style_settings(),
            type=self.type,
        )

    def __repr_args__(self) -> _repr.ReprArgs:
        for k, v in self.__dict__.items():
            if k == 'id':
                continue
            field = self.model_fields.get(k)
            if field and field.repr:
                yield k, v
        yield from ((k, getattr(self, k)) for k, v in self.model_computed_fields.items() if v.repr)


class EdgeSettings(Setting, BaseModel, extra=PYDANTIC_EXTRAS):
    type: Literal["protocol", "pathLookupEdge"]
    labels: List[str] = ["protocol"]

    def settings(self) -> dict:
        base_settings = self.base_settings()
        base_settings["labels"] = self.labels
        return base_settings


class GroupSettings(Setting, BaseModel, extra=PYDANTIC_EXTRAS):
    label: str
    children: List[EdgeSettings]
    type: Literal["group"] = 'group'

    def settings(self) -> dict:
        base_settings = self.base_settings()
        base_settings.update(dict(children=[child.settings() for child in self.children], label=self.label))
        return base_settings


class PathLookup(BaseModel, extra=PYDANTIC_EXTRAS):
    ignoredTopics: Optional[List[str]] = Field(
        default_factory=list,
        description="List of topics to ignore.  Valid topics are in ['ACL', 'FORWARDING', 'ZONEFW'].",
    )
    colorDetectedLoops: Optional[bool] = True

    @field_validator("ignoredTopics")
    @classmethod
    def _valid_topics(cls, v):
        if v and not all(t in ["ACL", "FORWARDING", "ZONEFW"] for t in v):
            raise ValueError(f"Ignored Topics '{v}' must be None or in ['ACL', 'FORWARDING', 'ZONEFW'].")
        return v


class GraphSettings(BaseModel, extra=PYDANTIC_EXTRAS):
    edges: List[Union[GroupSettings, EdgeSettings]]
    hiddenDeviceTypes: Optional[List[str]] = Field(default_factory=list)
    pathLookup: Optional[PathLookup] = None
    _parent_settings: str = PrivateAttr('GraphSettings')

    @field_validator("hiddenDeviceTypes")
    @classmethod
    def _valid_dev_types(cls, v):
        if v and not all(d in VALID_DEV_TYPES for d in v):
            raise ValueError(f"Device Types '{v}' must be None or in {VALID_DEV_TYPES}.")
        return v

    def __repr_args__(self) -> _repr.ReprArgs:
        for k, v in self.__dict__.items():
            if (
                    (self._parent_settings == 'PathLookupSettings' and k == 'hiddenDeviceTypes')
                    or (self._parent_settings == 'NetworkSettings' and k == 'pathLookup')
            ):
                continue
            field = self.model_fields.get(k)
            if field and field.repr:
                yield k, v
        yield from ((k, getattr(self, k)) for k, v in self.model_computed_fields.items() if v.repr)


class NetworkSettings(GraphSettings, BaseModel):
    _parent_settings: str = PrivateAttr('NetworkSettings')

    def __init__(
            self,
            edges: List[Union[GroupSettings, dict]] = None,
            hiddenDeviceTypes: Optional[List[str]] = None
    ):
        if not edges:
            edges = [GroupSettings(**edge) for edge in DEFAULT_NETWORK]
        if not isinstance(edges[0], GroupSettings):
            edges = [GroupSettings(**edge) for edge in edges]
        super().__init__(edges=edges, hiddenDeviceTypes=hiddenDeviceTypes or HIDDEN_DEV_TYPES)

    @staticmethod
    def _update_edge(children: List[EdgeSettings], name: str, attribute: str, bool_value=False):
        for edge in children:
            if edge.name.lower() == name:
                setattr(edge, attribute, bool_value)
                return True
        return False

    def _update_group(self, name: str, attribute: str, group: bool = False, bool_value=False):
        for edge in self.edges:
            if group and isinstance(edge, GroupSettings) and edge.name.lower() == name:
                setattr(edge, attribute, bool_value)
                return True
            elif not group:
                if isinstance(edge, GroupSettings) and self._update_edge(edge.children, name, attribute, bool_value):
                    return self._update_group(edge.name.lower(), "grouped", True)
                elif isinstance(edge, EdgeSettings) and self._update_edge([edge], name, attribute, bool_value):
                    return True
        return False

    def hide_protocol(self, protocol_name: str, unhide: bool = False):
        if protocol_name.lower() in VALID_NET_PROTOCOLS:
            return self._update_group(
                VALID_NET_PROTOCOLS[protocol_name.lower()], attribute="visible", group=False, bool_value=unhide
            )
        else:
            raise KeyError(
                f"Protocol {protocol_name} does not exist.  Valid protocols are {VALID_NET_PROTOCOLS.values()}"
            )

    def hide_all_protocols(self):
        for protocol_name in VALID_NET_PROTOCOLS.values():
            self._update_group(protocol_name, attribute="visible", group=False)

    def ungroup_protocol(self, protocol_name: str):
        if protocol_name.lower() in VALID_NET_PROTOCOLS:
            return self._update_group(VALID_NET_PROTOCOLS[protocol_name.lower()], attribute="grouped", group=False)
        else:
            raise KeyError(
                f"Protocol {protocol_name} does not exist.  Valid protocols are {VALID_NET_PROTOCOLS.values()}"
            )

    def hide_group(self, group_name: str):
        group_names = [g.name.lower() for g in self.edges if isinstance(g, GroupSettings)]
        if group_name.lower() in group_names:
            return self._update_group(group_name.lower(), attribute="visible", group=True)
        else:
            raise KeyError(f"Group {group_name} does not exist.  Valid groups are {group_names}")

    def ungroup_group(self, group_name: str):
        group_names = [g.name.lower() for g in self.edges if isinstance(g, GroupSettings)]
        if group_name.lower() in group_names:
            return self._update_group(group_name.lower(), attribute="grouped", group=True)
        else:
            raise KeyError(f"Group {group_name} does not exist.  Valid groups are {group_names}")

    @staticmethod
    def _proto_label(edge: EdgeSettings, protocol_name: str, label_name: str):
        if edge.name.lower() == protocol_name:
            proto = next(x for x in VALID_PROTOCOL_LABELS[protocol_name].labels if x == label_name)
            if proto.center:
                edge.labels[0] = proto.name
            else:
                edge.labels[1] = proto.name
            return True
        return False

    def change_label(self, protocol_name: str, label_name: str):
        protocol_name, label_name = protocol_name.lower(), label_name.lower()
        if protocol_name not in VALID_NET_PROTOCOLS:
            raise KeyError(
                f"Protocol {protocol_name} does not exist.  Valid protocols are {VALID_NET_PROTOCOLS.values()}"
            )
        else:
            protocol_name = VALID_NET_PROTOCOLS[protocol_name]
        if label_name not in VALID_PROTOCOL_LABELS[protocol_name].labels:
            raise KeyError(
                f"Label {label_name} does not exist for protocol {protocol_name}.  "
                f"Valid labels for {protocol_name} are {VALID_PROTOCOL_LABELS[protocol_name].labels}"
            )
        for edge in self.edges:
            if isinstance(edge, GroupSettings):
                for child in edge.children:
                    if self._proto_label(child, protocol_name, label_name):
                        return True
            if self._proto_label(edge, protocol_name, label_name):
                return True
        return False

    def settings(self) -> dict:
        settings = dict(
            edges=[edge.settings() for edge in self.edges],
            hiddenDeviceTypes=self.hiddenDeviceTypes,
        )
        return settings


class PathLookupSettings(GraphSettings, BaseModel):
    _parent_settings: str = PrivateAttr('PathLookupSettings')

    def __init__(
            self,
            edges: List[Union[EdgeSettings, dict]] = None,
            pathLookup: Optional[Union[PathLookup, dict]] = None
    ):
        if not edges:
            edges = [EdgeSettings(**edge) for edge in DEFAULT_PATHLOOKUP]
        if not isinstance(edges[0], EdgeSettings):
            edges = [EdgeSettings(**edge) for edge in edges]
        if not isinstance(pathLookup, PathLookup):
            pathLookup = PathLookup(**pathLookup) if pathLookup else PathLookup()
        super().__init__(edges=edges, pathLookup=pathLookup)

    @property
    def protocol_priority(self):
        return {edge.name.lower(): idx for idx, edge in enumerate(self.edges)}

    def increase_priority(self, protocol_name: str):
        if protocol_name.lower() not in VALID_PATH_PROTOCOLS:
            raise KeyError(f"Protocol {protocol_name} does not exist.  Valid protocols are {VALID_PATH_PROTOCOLS}")
        current = self.protocol_priority[protocol_name]
        if current != 0:
            self.edges[current], self.edges[current - 1] = self.edges[current - 1], self.edges[current]
        return True

    def decrease_priority(self, protocol_name: str):
        if protocol_name.lower() not in VALID_PATH_PROTOCOLS:
            raise KeyError(f"Protocol {protocol_name} does not exist.  Valid protocols are {VALID_PATH_PROTOCOLS}")
        current = self.protocol_priority[protocol_name]
        if current != len(self.edges) - 1:
            self.edges[current], self.edges[current + 1] = self.edges[current + 1], self.edges[current]
        return True

    def settings(self) -> dict:
        settings = dict(
            edges=[edge.settings() for edge in self.edges],
            pathLookup=vars(self.pathLookup),
        )
        return settings


class Overlay(BaseModel):
    """Set snapshotToCompare or intentRuleId, not both."""

    snapshotToCompare: Optional[Union[UUID, str]] = Field(None, description="Snapshot ID to compare.")
    intentRuleId: Optional[Union[int, str]] = Field(
        None,
        description="Intent Rule ID to overlay. Also valid: ['nonRedundantEdges', 'singlePointsOfFailure']",
    )

    @field_validator("snapshotToCompare")
    @classmethod
    def _valid_snapshot(cls, v):
        return valid_snapshot(v)

    @field_validator("intentRuleId")
    @classmethod
    def _valid_intentrule(cls, v):
        if v and v in ["nonRedundantEdges", "singlePointsOfFailure"]:
            return v
        try:
            return str(int(v))
        except ValueError:
            raise ValueError(f'"{v}" is not an Intent Rule ID or in ["nonRedundantEdges", "singlePointsOfFailure"]')

    @property
    def type(self):
        return "compare" if self.snapshotToCompare else "intent"

    def overlay(self) -> dict:
        if self.snapshotToCompare:
            return dict(type=self.type, snapshotToCompare=self.snapshotToCompare)
        else:
            return dict(type=self.type, intentRuleId=self.intentRuleId)

    def __repr_args__(self) -> _repr.ReprArgs:
        for k, v in self.__dict__.items():
            if v is None:
                continue
            field = self.model_fields.get(k)
            if field and field.repr:
                yield k, v
        yield from ((k, getattr(self, k)) for k, v in self.model_computed_fields.items() if v.repr)
