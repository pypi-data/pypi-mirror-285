import logging
from typing import Union, Dict, List, Optional, Literal, Any

from pydantic import BaseModel

from ipfabric.tools import raise_for_status
from .input_models import (
    Unicast,
    Multicast,
    Host2GW,
    Network,
    NetworkSettings,
    PathLookupSettings,
    Overlay,
    SharedView,
    GraphSettings,
    GroupSettings,
)
from .output_models.graph_result import NetworkEdge, Node, PathLookupEdge, GraphResult, PathLookup, Position

logger = logging.getLogger("ipfabric")
GRAPHS_URL = "graphs/"


class Diagram(BaseModel):
    ipf: Any

    def _check_snapshot_id(self, snapshot_id):
        snapshot_id = snapshot_id or self.ipf.snapshot_id
        if snapshot_id not in self.ipf.loaded_snapshots:
            raise ValueError(f"Snapshot {snapshot_id} is not loaded or not found in IP Fabric.")
        return snapshot_id

    def _intent_overlay(self, overlay: Overlay) -> dict:
        try:
            Overlay._valid_intentrule(overlay["intentRuleId"])
        except ValueError:
            if not self.ipf.intent.loaded:
                self.ipf.intent.load_intent()
            intents = self.ipf.intent.intents_by_name[overlay.intentRuleId]
            if len(intents) > 1:
                raise ValueError(f"Multiple Intents found with name `{overlay['intentRuleId']}`.")
            else:
                overlay.intentRuleId = intents[0].intent_id
        return overlay.overlay()

    def _snapshot_overlay(self, overlay: Overlay, snapshot_id: str = None) -> dict:
        if overlay.snapshotToCompare not in self.ipf.loaded_snapshots:
            raise ValueError(f"Snapshot `{overlay.snapshotToCompare}` is not loaded.")
        overlay.snapshotToCompare = self.ipf.snapshots[overlay.snapshotToCompare].snapshot_id
        if snapshot_id or self.ipf.snapshot_id == overlay.snapshotToCompare:
            raise ValueError(f"Cannot compare snapshot `{overlay.snapshotToCompare}` to itself.")
        self._check_snapshot_id(overlay.snapshotToCompare)
        return overlay.overlay()

    def _format_overlay(self, overlay: Union[Overlay, dict], snapshot_id: str = None) -> dict:
        if isinstance(overlay, dict):
            overlay = Overlay(**overlay)
        if overlay.intentRuleId:
            return self._intent_overlay(overlay)
        return self._snapshot_overlay(overlay, snapshot_id)

    def _query(
        self,
        parameters: dict,
        snapshot_id: str = None,
        overlay: Union[Overlay, dict] = None,
        image: Literal["png", "svg", "json"] = "json",
        graph_settings: dict = None,
        attr_filters: Optional[Dict[str, List[str]]] = None,
        positions: Optional[Dict[str, Union[Position, dict]]] = None,
    ):
        """
        Submits a query, does no formatting on the parameters.  Use for copy/pasting from the webpage.
        :param parameters: dict: Dictionary to submit in POST.
        :return: list: List of Dictionary objects.
        """
        url = GRAPHS_URL
        if image in ["svg", "png"]:
            url += image
        payload = dict(parameters=parameters, snapshot=self._check_snapshot_id(snapshot_id))
        if overlay:
            payload["overlay"] = self._format_overlay(overlay, snapshot_id)
        if graph_settings:
            payload["settings"] = graph_settings
        if attr_filters or self.ipf.attribute_filters:
            payload["attributeFilters"] = attr_filters or self.ipf.attribute_filters
        if positions:
            payload["positions"] = {k: dict(v) for k, v in positions.items()}
        res = raise_for_status(self.ipf.post(url, json=payload))
        return res.json() if image == "json" else res.content

    def json(
        self,
        parameters: Union[Unicast, Multicast, Host2GW, Network],
        snapshot_id: str = None,
        overlay: Union[Overlay, dict] = None,
        graph_settings: Union[NetworkSettings, PathLookupSettings] = None,
        attr_filters: Optional[Dict[str, List[str]]] = None,
        unicast_swap_src_dst: bool = False,
        positions: Optional[Dict[str, Union[Position, dict]]] = None,
    ) -> dict:
        return self._query(
            parameters.parameters(unicast_swap_src_dst) if isinstance(parameters, Unicast) else parameters.parameters(),
            snapshot_id=snapshot_id,
            image="json",
            overlay=overlay,
            attr_filters=attr_filters,
            graph_settings=graph_settings.settings() if graph_settings else None,
            positions=positions,
        )

    def svg(
        self,
        parameters: Union[Unicast, Multicast, Host2GW, Network],
        snapshot_id: str = None,
        overlay: Union[Overlay, dict] = None,
        graph_settings: Union[NetworkSettings, PathLookupSettings] = None,
        attr_filters: Optional[Dict[str, List[str]]] = None,
        unicast_swap_src_dst: bool = False,
        positions: Optional[Dict[str, Union[Position, dict]]] = None,
    ) -> bytes:
        return self._query(
            parameters.parameters(unicast_swap_src_dst) if isinstance(parameters, Unicast) else parameters.parameters(),
            snapshot_id=snapshot_id,
            overlay=overlay,
            attr_filters=attr_filters,
            image="svg",
            graph_settings=graph_settings.settings() if graph_settings else None,
            positions=positions,
        )

    def png(
        self,
        parameters: Union[Unicast, Multicast, Host2GW, Network],
        snapshot_id: str = None,
        overlay: Union[Overlay, dict] = None,
        graph_settings: Union[NetworkSettings, PathLookupSettings] = None,
        attr_filters: Optional[Dict[str, List[str]]] = None,
        unicast_swap_src_dst: bool = False,
        positions: Optional[Dict[str, Union[Position, dict]]] = None,
    ) -> bytes:
        return self._query(
            parameters.parameters(unicast_swap_src_dst) if isinstance(parameters, Unicast) else parameters.parameters(),
            snapshot_id=snapshot_id,
            overlay=overlay,
            attr_filters=attr_filters,
            image="png",
            graph_settings=graph_settings.settings() if graph_settings else None,
            positions=positions,
        )

    def share_link(
        self,
        parameters: Union[Unicast, Multicast, Host2GW, Network],
        snapshot_id: str = None,
        overlay: Union[Overlay, dict] = None,
        graph_settings: Union[NetworkSettings, PathLookupSettings] = None,
        attr_filters: Optional[Dict[str, List[str]]] = None,
        unicast_swap_src_dst: bool = False,
        positions: Optional[Dict[str, Union[Position, dict]]] = None,
    ) -> str:
        parameters = (
            parameters.parameters(unicast_swap_src_dst) if isinstance(parameters, Unicast) else parameters.parameters()
        )

        resp = self._query(
            parameters,
            snapshot_id=snapshot_id,
            overlay=overlay,
            image="json",
            attr_filters=attr_filters,
            graph_settings=graph_settings.settings() if graph_settings else None,
            positions=positions,
        )

        parameters.pop("layouts", None)
        payload = {
            "graphView": {
                "name": "Shared view",
                "parameters": parameters,
                "collapsedNodeGroups": [],
                "hiddenNodes": [],
                "positions": {k: v["position"] for k, v in resp["graphResult"]["graphData"]["nodes"].items()},
                "settings": resp["graphResult"]["settings"],
            },
            "snapshot": self._check_snapshot_id(snapshot_id),
        }
        if overlay:
            payload["graphView"]["overlay"] = self._format_overlay(overlay, snapshot_id)
        res = raise_for_status(self.ipf.post("graphs/urls", json=payload))
        return str(self.ipf.base_url.join(f"/diagrams/share/{res.json()['id']}"))

    def model(
        self,
        parameters: Union[Unicast, Multicast, Host2GW, Network],
        snapshot_id: str = None,
        overlay: Overlay = None,
        graph_settings: Union[NetworkSettings, PathLookupSettings] = None,
        attr_filters: Optional[Dict[str, List[str]]] = None,
        unicast_swap_src_dst: bool = False,
        positions: Optional[Dict[str, Union[Position, dict]]] = None,
    ) -> GraphResult:
        json_data = self.json(
            parameters, snapshot_id, overlay, graph_settings, attr_filters, unicast_swap_src_dst, positions
        )
        edge_setting_dict = self._diagram_edge_settings(json_data["graphResult"]["settings"])
        if isinstance(parameters, Network):
            return self._diagram_network(json_data, edge_setting_dict)
        else:
            return self._diagram_pathlookup(json_data, edge_setting_dict)

    @staticmethod
    def _diagram_network(json_data: dict, edge_setting_dict: dict, pathlookup: bool = False) -> GraphResult:
        edges, nodes = dict(), dict()
        for node_id, node in json_data["graphResult"]["graphData"]["nodes"].items():
            nodes[node_id] = Node.model_validate(node)

        for edge_id, edge_json in json_data["graphResult"]["graphData"]["edges"].items():
            edge = PathLookupEdge.model_validate(edge_json) if pathlookup else NetworkEdge.model_validate(edge_json)
            edge.protocol = (
                edge_setting_dict[edge.edgeSettingsId].name if edge.edgeSettingsId in edge_setting_dict else None
            )
            if edge.source:
                edge.source = nodes[edge.source]
            if edge.target:
                edge.target = nodes[edge.target]
            edges[edge_id] = edge

        return GraphResult(edges=edges, nodes=nodes)

    def _diagram_pathlookup(self, json_data: dict, edge_setting_dict: dict) -> GraphResult:
        graph_result = self._diagram_network(json_data, edge_setting_dict, pathlookup=True)

        for edge_id, edge in graph_result.edges.items():
            for prev_id in edge.prevEdgeIds:
                edge.prevEdge.append(graph_result.edges[prev_id])
            for next_id in edge.nextEdgeIds:
                edge.nextEdge.append(graph_result.edges[next_id] if next_id in graph_result.edges else next_id)
        graph_result.pathlookup = PathLookup.model_validate(json_data["pathlookup"])

        return graph_result

    @staticmethod
    def _diagram_edge_settings(graph_settings: dict) -> dict:
        net_settings = GraphSettings(**graph_settings)
        edge_setting_dict = dict()
        for edge in net_settings.edges:
            edge_setting_dict[edge.id] = edge
            if isinstance(edge, GroupSettings):
                for child in edge.children:
                    edge_setting_dict[child.id] = child
        return edge_setting_dict

    def shared_view(
        self,
        url: Union[int, str],
        image: Literal["json", "code", "model", "svg", "png"] = "json",
        positions: bool = False,
    ):
        """Takes a shared graph link and returns the data or the code to implement in python.

        Args:
            url: Id of the shared view (1453653298) or full/partial URL (`/diagrams/share/1453626097`)
            image: Defaults to return the data instead of printing the code
            positions: If returning code then include positions of nodes in example; Default False

        Returns: The graph data or string representing the code to produce it.
        """
        query = self.ipf._shared_url(url, False)
        if query["snapshot"] not in self.ipf.loaded_snapshots:
            logger.warning(f'Snapshot {query["snapshot"]} is not loaded, switching to {self.ipf.snapshot_id}.')
            query["snapshot"] = self.ipf.snapshot_id
        overlay = query["graphView"].get("overlay", {})
        if (
            overlay
            and overlay.get("snapshotToCompare", None)
            and overlay["snapshotToCompare"] not in self.ipf.loaded_snapshots
        ):
            logger.error(f"Snapshot `{overlay['snapshotToCompare']}` is not loaded to compare, removing overlay.")
            overlay = {}

        view = SharedView(
            snapshot_id=query["snapshot"],
            client_snapshot_id=self.ipf.snapshot_id,
            hidden_nodes=query["graphView"]["hiddenNodes"],
            collapsed_node_groups=query["graphView"]["collapsedNodeGroups"],
            positions=query["graphView"]["positions"],
            settings=query["graphView"]["settings"]["edges"],
            params=query["graphView"]["parameters"],
            hidden_devs=query["graphView"]["settings"].get("hiddenDeviceTypes", []),
            path_lookup=query["graphView"]["settings"].get("pathLookup", None),
            overlay=overlay,
        )
        if view.hidden_nodes or view.collapsed_node_groups:
            logger.warning("Hidden Nodes and Collapsed Node Groups are only available via the UI.")

        if image in ["json", "svg", "png"]:
            return self._query(
                parameters=query["graphView"]["parameters"],
                snapshot_id=query["snapshot"],
                overlay=overlay,
                image=image,
                graph_settings=query["graphView"]["settings"],
                positions=query["graphView"]["positions"],
            )

        if image == "code":
            return "\n".join(view.create_code(positions))
        if image == "model":
            return self.model(
                parameters=view.graph_model(),
                snapshot_id=query["snapshot"],
                overlay=overlay,
                graph_settings=view.graph_settings(),
                positions=query["graphView"]["positions"],
            )
        return None
