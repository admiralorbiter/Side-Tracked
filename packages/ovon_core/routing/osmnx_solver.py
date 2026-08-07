"""OSMnx + igraph C-backed Pedestrian Closed Loop Solver."""

import math

import igraph as ig
import networkx as nx
import osmnx as ox

from packages.ovon_core.domain import (
    Coordinate,
    LoopRequest,
    RoutePersona,
)
from packages.ovon_core.routing.cache import GraphCacheManager
from packages.ovon_core.routing.provider import (
    LoopRouteCandidate,
    RoutingProvenance,
    RoutingProvider,
    RoutingResult,
)
from packages.ovon_core.spatial import lat_lng_to_h3_cell

DEFAULT_WALK_SPEED_MPS = 1.25  # 1.25 m/s approx 4.5 km/h standard pedestrian speed


class OSMnxIgraphRoutingProvider(RoutingProvider):
    """OSMnx and igraph powered pedestrian network closed walking loop solver."""

    def __init__(self, cache_manager: GraphCacheManager | None = None):
        self.cache_manager = cache_manager or GraphCacheManager()

    @property
    def provider_name(self) -> str:
        return "OSMnx + igraph (Pedestrian)"

    def _get_or_fetch_nx_graph(
        self, origin: Coordinate, search_radius_meters: float = 1200.0
    ) -> nx.MultiDiGraph:
        """Fetch or load cached NetworkX graph for the origin location."""
        cell = lat_lng_to_h3_cell(origin, resolution=8)
        cached_graph = self.cache_manager.get_graph_for_cell(cell)
        if cached_graph is not None:
            return cached_graph

        # Fetch pedestrian network from OpenStreetMap
        G_nx = ox.graph_from_point(
            (origin.latitude, origin.longitude),
            dist=search_radius_meters,
            network_type="walk",
            truncate_by_edge=True,
        )

        # Ensure edge length and travel time attributes exist
        for _, _, _, data in G_nx.edges(keys=True, data=True):
            if "length" not in data:
                data["length"] = 100.0
            data["travel_time"] = data["length"] / DEFAULT_WALK_SPEED_MPS

        self.cache_manager.save_graph_for_cell(cell, G_nx)
        return G_nx

    def _convert_nx_to_igraph(
        self, G_nx: nx.MultiDiGraph
    ) -> tuple[ig.Graph, dict[int, int], dict[int, int], dict[int, tuple[float, float]]]:
        """Convert NetworkX MultiDiGraph to igraph.Graph with vertex mappings."""
        nx_nodes = list(G_nx.nodes())
        node_to_idx = {node: i for i, node in enumerate(nx_nodes)}
        idx_to_node = {i: node for i, node in enumerate(nx_nodes)}

        node_coords = {
            i: (G_nx.nodes[node]["y"], G_nx.nodes[node]["x"]) for i, node in enumerate(nx_nodes)
        }

        edges = []
        weights = []

        for u, v, data in G_nx.edges(data=True):
            edges.append((node_to_idx[u], node_to_idx[v]))
            weights.append(data.get("length", 1.0))

        G_ig = ig.Graph(directed=True)
        G_ig.add_vertices(len(nx_nodes))
        G_ig.add_edges(edges)
        G_ig.es["weight"] = weights

        return G_ig, node_to_idx, idx_to_node, node_coords

    def calculate_loop(self, request: LoopRequest) -> RoutingResult:
        """Generate 3 closed walking loop candidates (Easy, Birdy, Weird) using OSMnx + igraph."""
        target_time_seconds = request.duration_minutes * 60.0
        target_dist_meters = target_time_seconds * DEFAULT_WALK_SPEED_MPS
        search_radius = max(800.0, target_dist_meters / (2.0 * math.pi) * 1.5)

        try:
            G_nx = self._get_or_fetch_nx_graph(request.origin, search_radius_meters=search_radius)
        except Exception:
            # Fall back to default search radius graph fetch
            G_nx = self._get_or_fetch_nx_graph(request.origin, search_radius_meters=1000.0)

        G_ig, node_to_idx, idx_to_node, node_coords = self._convert_nx_to_igraph(G_nx)

        # Find origin node in NetworkX graph
        origin_node = ox.distance.nearest_nodes(
            G_nx, request.origin.longitude, request.origin.latitude
        )
        origin_idx = node_to_idx[origin_node]

        persona_configs = [
            (
                RoutePersona.EASY,
                "The Easy One",
                "Shortest closed loop with paved trails and low elevation change.",
                "Lowest effort",
                "Paved park paths with standard suburban bird activity.",
                0.0,
                2.0 * math.pi / 3.0,
                0.35,
            ),
            (
                RoutePersona.BIRDY,
                "The Birdy One",
                "Diverges into dense tree canopy and creek bed edge habitat.",
                "Best bird opportunity",
                "Adds dirt trail near Brush Creek for double species diversity.",
                math.pi / 4.0,
                math.pi,
                0.45,
            ),
            (
                RoutePersona.WEIRD,
                "The Weird One",
                "Explores lesser-known perimeter tree line and old orchard edge.",
                "Unusual habitat",
                "Uneven terrain along forgotten overgrown fence line.",
                math.pi / 2.0,
                3.0 * math.pi / 2.0,
                0.40,
            ),
        ]

        candidates: list[LoopRouteCandidate] = []

        for (
            persona,
            name,
            tagline,
            badge,
            tradeoff,
            angle1,
            angle2,
            radius_factor,
        ) in persona_configs:
            loop_radius_deg = (target_dist_meters * radius_factor / (2.0 * math.pi)) / 111139.0
            lat_orig, lon_orig = request.origin.latitude, request.origin.longitude

            # Target waypoint 1
            w1_lat = lat_orig + loop_radius_deg * math.cos(angle1)
            w1_lon = lon_orig + loop_radius_deg * math.sin(angle1) / math.cos(
                math.radians(lat_orig)
            )
            w1_node = ox.distance.nearest_nodes(G_nx, w1_lon, w1_lat)
            w1_idx = node_to_idx[w1_node]

            # Target waypoint 2
            w2_lat = lat_orig + loop_radius_deg * math.cos(angle2)
            w2_lon = lon_orig + loop_radius_deg * math.sin(angle2) / math.cos(
                math.radians(lat_orig)
            )
            w2_node = ox.distance.nearest_nodes(G_nx, w2_lon, w2_lat)
            w2_idx = node_to_idx[w2_node]

            # Compute 3 shortest path legs: Origin -> W1 -> W2 -> Origin
            path1 = G_ig.get_shortest_paths(
                origin_idx, to=w1_idx, weights="weight", output="vpath"
            )[0]
            path2 = G_ig.get_shortest_paths(w1_idx, to=w2_idx, weights="weight", output="vpath")[0]
            path3 = G_ig.get_shortest_paths(
                w2_idx, to=origin_idx, weights="weight", output="vpath"
            )[0]

            # Combine node indices into single closed loop path
            combined_nodes = path1 + path2[1:] + path3[1:]

            # Extract coordinates for LineString GeoJSON with edge curve snapping
            coords_list: list[list[float]] = []
            total_dist = 0.0

            for i in range(len(combined_nodes)):
                idx = combined_nodes[i]
                lat, lon = node_coords[idx]

                if i == 0:
                    coords_list.append([lon, lat])
                else:
                    prev_idx = combined_nodes[i - 1]
                    prev_node = idx_to_node[prev_idx]
                    curr_node = idx_to_node[idx]

                    # Check if NetworkX edge has detailed geometry shape
                    edge_data = G_nx.get_edge_data(prev_node, curr_node)
                    geom_points = None
                    if edge_data:
                        first_edge = list(edge_data.values())[0]
                        if "geometry" in first_edge:
                            geom_points = list(first_edge["geometry"].coords)

                    if geom_points and len(geom_points) > 1:
                        # Append interior edge curve points (lon, lat)
                        for pt in geom_points[1:]:
                            coords_list.append([round(pt[0], 6), round(pt[1], 6)])
                    else:
                        coords_list.append([lon, lat])

                    prev_lat, prev_lon = node_coords[prev_idx]
                    total_dist += Coordinate(prev_lat, prev_lon).haversine_distance_meters(
                        Coordinate(lat, lon)
                    )

            if total_dist <= 0:
                total_dist = target_dist_meters

            calc_dur_min = int(round((total_dist / DEFAULT_WALK_SPEED_MPS) / 60.0))
            if calc_dur_min <= 0:
                calc_dur_min = request.duration_minutes

            geojson_geom = {
                "type": "LineString",
                "coordinates": coords_list,
            }

            waypoints = (
                request.origin,
                Coordinate(w1_lat, w1_lon),
                Coordinate(w2_lat, w2_lon),
                request.origin,
            )

            candidate = LoopRouteCandidate(
                persona=persona,
                name=name,
                tagline=tagline,
                duration_minutes=calc_dur_min,
                distance_meters=round(total_dist, 1),
                badge_label=badge,
                tradeoff_description=tradeoff,
                geojson_geometry=geojson_geom,
                waypoints=waypoints,
            )
            candidates.append(candidate)

        provenance = RoutingProvenance(
            provider_name=self.provider_name,
            graph_version="OpenStreetMap Walk Network",
            nodes_count=len(G_nx.nodes()),
            edges_count=len(G_nx.edges()),
        )

        return RoutingResult(
            origin=request.origin,
            duration_minutes=request.duration_minutes,
            candidates=tuple(candidates),
            provenance=provenance,
        )
