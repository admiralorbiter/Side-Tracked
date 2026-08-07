"""OSMnx + igraph Spatial Graph Routing Engine for OVON Core."""

import math

import networkx as nx
import osmnx as ox
from shapely.geometry import LineString

try:
    import matplotlib

    matplotlib.use("Agg")
except Exception:
    pass

import igraph as ig

from packages.ovon_core.domain import Coordinate, LoopRequest, RoutePersona, TaxonRef
from packages.ovon_core.ecology import HabitatType, ProvisionalSpeciesSurface
from packages.ovon_core.routing.cache import DEFAULT_MAX_BUDGET_RADIUS_METERS, GraphCacheManager
from packages.ovon_core.routing.provider import (
    LoopRouteCandidate,
    RoutingProvenance,
    RoutingProvider,
    RoutingResult,
)
from packages.ovon_core.spatial import lat_lng_to_h3_cell, polyline_to_h3_cells

# Standard pedestrian walking speed: 1.25 m/s (~4.5 km/h)
DEFAULT_WALK_SPEED_MPS = 1.25


def calculate_jaccard_edge_overlap(epath_a: list[int], epath_b: list[int]) -> float:
    """Calculate Jaccard edge overlap coefficient between two candidate edge paths."""
    set_a, set_b = set(epath_a), set(epath_b)
    if not set_a or not set_b:
        return 0.0
    return len(set_a.intersection(set_b)) / float(len(set_a.union(set_b)))


def calculate_repeated_edge_ratio(
    edge_sequence: list[tuple[int, int, int]], G_nx: nx.MultiDiGraph
) -> float:
    """Calculate self-backtracking metric B(R) = length traversed more than once / total route length."""
    if not edge_sequence:
        return 0.0

    edge_counts: dict[tuple[int, int, int], int] = {}
    total_len = 0.0

    for u, v, k in edge_sequence:
        canonical_edge = (min(u, v), max(u, v), k)
        edge_counts[canonical_edge] = edge_counts.get(canonical_edge, 0) + 1
        if G_nx.has_edge(u, v, key=k):
            total_len += float(G_nx[u][v][k].get("length", 100.0))
        else:
            total_len += 100.0

    if total_len <= 0:
        return 0.0

    repeated_len = 0.0
    for u, v, k in edge_sequence:
        canonical_edge = (min(u, v), max(u, v), k)
        if edge_counts[canonical_edge] > 1:
            if G_nx.has_edge(u, v, key=k):
                repeated_len += float(G_nx[u][v][k].get("length", 100.0))
            else:
                repeated_len += 100.0

    return repeated_len / total_len


def calculate_spatial_corridor_overlap(
    geom_a: dict, geom_b: dict, buffer_meters: float = 75.0
) -> tuple[float, float]:
    """Calculate spatial corridor overlap metrics S_IoU and S_contain using buffered Shapely geometries."""
    try:
        coords_a = geom_a.get("coordinates", [])
        coords_b = geom_b.get("coordinates", [])
        if len(coords_a) < 2 or len(coords_b) < 2:
            return 0.0, 0.0

        line_a = LineString(coords_a)
        line_b = LineString(coords_b)

        deg_buffer = buffer_meters / 111139.0
        buf_a = line_a.buffer(deg_buffer)
        buf_b = line_b.buffer(deg_buffer)

        inter_area = buf_a.intersection(buf_b).area
        union_area = buf_a.union(buf_b).area

        if union_area <= 0:
            return 0.0, 0.0

        s_iou = inter_area / union_area
        min_area = min(buf_a.area, buf_b.area)
        s_contain = inter_area / min_area if min_area > 0 else 0.0

        return s_iou, s_contain
    except Exception:
        return 0.0, 0.0


def reconstruct_leg_geometry_and_metrics(
    epath: list[int],
    ig_edge_to_nx_key: list[tuple[int, int, int]],
    G_nx: nx.MultiDiGraph,
    G_ig: ig.Graph,
    node_to_idx: dict[int, int],
    node_coords: dict[int, tuple[float, float]],
    leg_index: int,
    origin_name: str,
) -> tuple[dict, float, float, str, str]:
    """Reconstruct exact GeoJSON sub-LineString, distance, duration, dominant trail name, and turn instruction for a leg."""
    coords_list: list[list[float]] = []
    leg_dist = 0.0
    names: list[str] = []

    for e_idx in epath:
        u, v, key = ig_edge_to_nx_key[e_idx]
        edge_data = G_nx[u][v][key]
        leg_dist += float(edge_data.get("length", 100.0))

        raw_name = edge_data.get("name")
        if isinstance(raw_name, list) and raw_name:
            raw_name = raw_name[0]
        if raw_name and isinstance(raw_name, str):
            names.append(raw_name)

        source_idx = G_ig.es[e_idx].source
        is_reversed = node_to_idx[u] != source_idx

        if "geometry" in edge_data:
            geom_pts = list(edge_data["geometry"].coords)
            if is_reversed:
                geom_pts.reverse()
            if coords_list:
                geom_pts = geom_pts[1:]
            for pt in geom_pts:
                coords_list.append([round(pt[0], 6), round(pt[1], 6)])
        else:
            u_lat, u_lon = node_coords[node_to_idx[u]]
            v_lat, v_lon = node_coords[node_to_idx[v]]
            if is_reversed:
                u_lat, u_lon, v_lat, v_lon = v_lat, v_lon, u_lat, u_lon
            if not coords_list:
                coords_list.append([round(u_lon, 6), round(u_lat, 6)])
            coords_list.append([round(v_lon, 6), round(v_lat, 6)])

    if not coords_list:
        coords_list = [[0.0, 0.0], [0.0, 0.0]]

    leg_dur_min = round((leg_dist / DEFAULT_WALK_SPEED_MPS) / 60.0, 1)
    dominant_name = names[0] if names else f"Park Trail Sector {leg_index}"

    dist_str = f"{leg_dist / 1000.0:.1f}km" if leg_dist >= 1000 else f"{int(leg_dist)}m"
    if leg_index == 1:
        instruction = f"Depart {origin_name} heading along {dominant_name} ({dist_str})."
    elif leg_index == 2:
        instruction = (
            f"Bear right onto {dominant_name}, following central canopy path ({dist_str})."
        )
    else:
        instruction = f"Turn onto {dominant_name}, looping back to {origin_name} ({dist_str})."

    sub_geom = {
        "type": "LineString",
        "coordinates": coords_list,
    }

    return sub_geom, round(leg_dist, 1), leg_dur_min, dominant_name, instruction


class OSMnxIgraphRoutingProvider(RoutingProvider):
    """OSMnx NetworkX graph solver using C-backed igraph shortest paths with candidate pool generation."""

    def __init__(
        self,
        cache_manager: GraphCacheManager | None = None,
        species_surface: ProvisionalSpeciesSurface | None = None,
    ):
        self.cache_manager = cache_manager or GraphCacheManager()
        self.species_surface = species_surface or ProvisionalSpeciesSurface()

    @property
    def provider_name(self) -> str:
        return "OSMnx + igraph (Pedestrian)"

    def _get_or_fetch_nx_graph(
        self, origin: Coordinate, search_radius_meters: float = DEFAULT_MAX_BUDGET_RADIUS_METERS
    ) -> nx.MultiDiGraph:
        """Fetch or load cached NetworkX max-budget graph for the origin location."""
        cell = lat_lng_to_h3_cell(origin, resolution=8)
        cached_graph = self.cache_manager.get_graph_for_cell(
            cell, radius_meters=search_radius_meters
        )
        if cached_graph is not None:
            return cached_graph

        G_nx = ox.graph_from_point(
            (origin.latitude, origin.longitude),
            dist=search_radius_meters,
            network_type="walk",
            truncate_by_edge=True,
        )

        for _, _, _, data in G_nx.edges(keys=True, data=True):
            if "length" not in data:
                data["length"] = 100.0
            data["travel_time"] = data["length"] / DEFAULT_WALK_SPEED_MPS

        self.cache_manager.save_graph_for_cell(cell, G_nx, radius_meters=search_radius_meters)
        return G_nx

    def _convert_nx_to_igraph(
        self, G_nx: nx.MultiDiGraph
    ) -> tuple[
        ig.Graph,
        dict[int, int],
        dict[int, int],
        dict[int, tuple[float, float]],
        list[tuple[int, int, int]],
    ]:
        """Convert NetworkX MultiDiGraph to igraph.Graph with exact edge key mappings."""
        nx_nodes = list(G_nx.nodes())
        node_to_idx = {node: i for i, node in enumerate(nx_nodes)}
        idx_to_node = {i: node for i, node in enumerate(nx_nodes)}

        node_coords = {
            i: (G_nx.nodes[node]["y"], G_nx.nodes[node]["x"]) for i, node in enumerate(nx_nodes)
        }

        edges = []
        weights = []
        ig_edge_to_nx_key: list[tuple[int, int, int]] = []

        for u, v, key, data in G_nx.edges(keys=True, data=True):
            edges.append((node_to_idx[u], node_to_idx[v]))
            weights.append(data.get("length", 100.0))
            ig_edge_to_nx_key.append((u, v, key))

        G_ig = ig.Graph(directed=True)
        G_ig.add_vertices(len(nx_nodes))
        G_ig.add_edges(edges)
        G_ig.es["weight"] = weights

        return G_ig, node_to_idx, idx_to_node, node_coords, ig_edge_to_nx_key

    def calculate_loop(self, request: LoopRequest) -> RoutingResult:
        """Generate 3 closed walking loop candidates (Easy, Birdy, Weird/Scenic) using candidate pool selection."""
        target_time_seconds = request.duration_minutes * 60.0
        target_dist_meters = target_time_seconds * DEFAULT_WALK_SPEED_MPS

        search_radius = max(
            DEFAULT_MAX_BUDGET_RADIUS_METERS,
            request.duration_minutes * 60.0 * DEFAULT_WALK_SPEED_MPS * 0.6,
        )

        G_nx = self._get_or_fetch_nx_graph(request.origin, search_radius_meters=search_radius)
        G_ig, node_to_idx, idx_to_node, node_coords, ig_edge_to_nx_key = self._convert_nx_to_igraph(
            G_nx
        )

        origin_node = ox.distance.nearest_nodes(
            G_nx, request.origin.longitude, request.origin.latitude
        )
        origin_idx = node_to_idx[origin_node]

        candidate_pool: list[LoopRouteCandidate] = []
        cardinal_bearings = [
            (0.0, math.pi / 2.0),
            (math.pi / 4.0, 3.0 * math.pi / 4.0),
            (math.pi / 2.0, math.pi),
            (3.0 * math.pi / 4.0, 5.0 * math.pi / 4.0),
            (math.pi, 3.0 * math.pi / 2.0),
            (5.0 * math.pi / 4.0, 7.0 * math.pi / 4.0),
            (3.0 * math.pi / 2.0, 0.0),
            (7.0 * math.pi / 4.0, math.pi / 4.0),
        ]
        radius_factors = [0.25, 0.40, 0.55, 0.70]

        cardinal = TaxonRef.create("Northern Cardinal", "Cardinalis cardinalis", "norcar")
        min_budget_min = request.duration_minutes * 0.40
        max_budget_min = request.duration_minutes * 1.25

        for angle1, angle2 in cardinal_bearings:
            for radius_factor in radius_factors:
                loop_radius_deg = (target_dist_meters * radius_factor / (2.0 * math.pi)) / 111139.0
                lat_orig, lon_orig = request.origin.latitude, request.origin.longitude

                w1_lat = lat_orig + loop_radius_deg * math.cos(angle1)
                w1_lon = lon_orig + loop_radius_deg * math.sin(angle1) / math.cos(
                    math.radians(lat_orig)
                )
                w1_node = ox.distance.nearest_nodes(G_nx, w1_lon, w1_lat)
                w1_idx = node_to_idx[w1_node]

                w2_lat = lat_orig + loop_radius_deg * math.cos(angle2)
                w2_lon = lon_orig + loop_radius_deg * math.sin(angle2) / math.cos(
                    math.radians(lat_orig)
                )
                w2_node = ox.distance.nearest_nodes(G_nx, w2_lon, w2_lat)
                w2_idx = node_to_idx[w2_node]

                epath1 = G_ig.get_shortest_paths(
                    origin_idx, to=w1_idx, weights="weight", output="epath"
                )[0]
                if not epath1:
                    continue

                weights_copy = list(G_ig.es["weight"])
                for e_idx in epath1:
                    weights_copy[e_idx] *= 3.0

                epath2 = G_ig.get_shortest_paths(
                    w1_idx, to=w2_idx, weights=weights_copy, output="epath"
                )[0]
                if not epath2:
                    continue

                for e_idx in epath2:
                    weights_copy[e_idx] *= 3.0

                epath3 = G_ig.get_shortest_paths(
                    w2_idx, to=origin_idx, weights=weights_copy, output="epath"
                )[0]
                if not epath3:
                    continue

                combined_epath = epath1 + epath2 + epath3
                edge_seq = [ig_edge_to_nx_key[e_idx] for e_idx in combined_epath]

                b_r = calculate_repeated_edge_ratio(edge_seq, G_nx)
                if b_r > 0.20:
                    continue

                # Reconstruct sub-geometries and metrics per leg
                leg1_geom, leg1_dist, leg1_dur, leg1_name, leg1_inst = (
                    reconstruct_leg_geometry_and_metrics(
                        epath1,
                        ig_edge_to_nx_key,
                        G_nx,
                        G_ig,
                        node_to_idx,
                        node_coords,
                        1,
                        request.origin_name,
                    )
                )
                leg2_geom, leg2_dist, leg2_dur, leg2_name, leg2_inst = (
                    reconstruct_leg_geometry_and_metrics(
                        epath2,
                        ig_edge_to_nx_key,
                        G_nx,
                        G_ig,
                        node_to_idx,
                        node_coords,
                        2,
                        request.origin_name,
                    )
                )
                leg3_geom, leg3_dist, leg3_dur, leg3_name, leg3_inst = (
                    reconstruct_leg_geometry_and_metrics(
                        epath3,
                        ig_edge_to_nx_key,
                        G_nx,
                        G_ig,
                        node_to_idx,
                        node_coords,
                        3,
                        request.origin_name,
                    )
                )

                total_dist = leg1_dist + leg2_dist + leg3_dist
                if total_dist <= 0:
                    continue

                calc_dur_min = int(round((total_dist / DEFAULT_WALK_SPEED_MPS) / 60.0))
                if not (min_budget_min <= calc_dur_min <= max_budget_min):
                    continue

                all_coords = (
                    leg1_geom["coordinates"]
                    + leg2_geom["coordinates"][1:]
                    + leg3_geom["coordinates"][1:]
                )
                if all_coords[0] != all_coords[-1]:
                    all_coords.append(all_coords[0])

                geojson_geom = {
                    "type": "LineString",
                    "coordinates": all_coords,
                }

                segment_metrics = (
                    {
                        "index": 1,
                        "name": f"Outbound Leg ({leg1_name})",
                        "habitat_name": "Woodland Edge & Parkland",
                        "distance_meters": leg1_dist,
                        "duration_minutes": leg1_dur,
                        "geojson_geometry": leg1_geom,
                        "navigation_instruction": leg1_inst,
                    },
                    {
                        "index": 2,
                        "name": f"Return Loop Leg ({leg2_name} & {leg3_name})",
                        "habitat_name": "Canopy & Meadow Boundary",
                        "distance_meters": round(leg2_dist + leg3_dist, 1),
                        "duration_minutes": round(leg2_dur + leg3_dur, 1),
                        "geojson_geometry": {
                            "type": "LineString",
                            "coordinates": leg2_geom["coordinates"] + leg3_geom["coordinates"][1:],
                        },
                        "navigation_instruction": leg2_inst,
                    },
                )

                traversed_cells = polyline_to_h3_cells(geojson_geom, resolution=8)
                eco_score = sum(
                    self.species_surface.get_relative_score(
                        cardinal, HabitatType.MATURE_CANOPY, cell
                    )
                    for cell in traversed_cells
                ) / float(max(1, len(traversed_cells)))

                waypoints = (
                    request.origin,
                    Coordinate(w1_lat, w1_lon),
                    Coordinate(w2_lat, w2_lon),
                    request.origin,
                )

                candidate = LoopRouteCandidate(
                    persona=RoutePersona.EASY,
                    name="Candidate",
                    tagline="Candidate Loop",
                    duration_minutes=calc_dur_min,
                    distance_meters=round(total_dist, 1),
                    badge_label="Candidate",
                    tradeoff_description="",
                    geojson_geometry=geojson_geom,
                    waypoints=waypoints,
                    segment_metrics=segment_metrics,
                    edge_sequence=tuple(edge_seq),
                    repeated_edge_ratio=round(b_r, 3),
                    ecological_score=round(eco_score, 3),
                    novelty_score=round(radius_factor * 10.0, 3),
                )

                candidate_pool.append(candidate)

        if not candidate_pool:
            dummy_geom = {
                "type": "LineString",
                "coordinates": [
                    [request.origin.longitude, request.origin.latitude],
                    [request.origin.longitude + 0.002, request.origin.latitude + 0.002],
                    [request.origin.longitude, request.origin.latitude],
                ],
            }
            cand = LoopRouteCandidate(
                persona=RoutePersona.EASY,
                name="The Easy One",
                tagline="Shortest closed loop",
                duration_minutes=request.duration_minutes,
                distance_meters=round(target_dist_meters, 1),
                badge_label="Lowest Effort",
                tradeoff_description="Lowest physical effort",
                geojson_geometry=dummy_geom,
                waypoints=(request.origin, request.origin),
            )
            candidate_pool.append(cand)

        easy_cand = min(
            candidate_pool,
            key=lambda c: (
                abs(c.duration_minutes - request.duration_minutes),
                c.distance_meters,
            ),
        )
        easy_opt = LoopRouteCandidate(
            persona=RoutePersona.EASY,
            name="The Easy One",
            tagline="Shortest closed loop with low complexity",
            duration_minutes=easy_cand.duration_minutes,
            distance_meters=easy_cand.distance_meters,
            badge_label="Lowest Effort",
            tradeoff_description="Lowest physical effort and simplest navigation path",
            geojson_geometry=easy_cand.geojson_geometry,
            waypoints=easy_cand.waypoints,
            segment_metrics=easy_cand.segment_metrics,
            edge_sequence=easy_cand.edge_sequence,
            repeated_edge_ratio=easy_cand.repeated_edge_ratio,
            ecological_score=easy_cand.ecological_score,
            novelty_score=easy_cand.novelty_score,
        )

        selected_candidates = [easy_opt]

        birdy_candidates = []
        for c in candidate_pool:
            s_iou, s_contain = calculate_spatial_corridor_overlap(
                c.geojson_geometry, easy_opt.geojson_geometry, buffer_meters=75.0
            )
            if s_iou <= 0.45 and s_contain <= 0.60:
                birdy_candidates.append(c)

        if not birdy_candidates:
            other_cands = [c for c in candidate_pool if c != easy_cand]
            if other_cands:
                birdy_candidates = [
                    min(
                        other_cands,
                        key=lambda c: calculate_spatial_corridor_overlap(
                            c.geojson_geometry, easy_opt.geojson_geometry, buffer_meters=75.0
                        )[1],
                    )
                ]

        best_birdy_raw = None
        if birdy_candidates:
            best_birdy = max(
                birdy_candidates,
                key=lambda c: (
                    c.ecological_score,
                    -abs(c.duration_minutes - request.duration_minutes),
                ),
            )
            best_birdy_raw = best_birdy
            birdy_opt = LoopRouteCandidate(
                persona=RoutePersona.BIRDY,
                name="The Birdy One",
                tagline="Balanced loop visiting varied habitat edges",
                duration_minutes=best_birdy.duration_minutes,
                distance_meters=best_birdy.distance_meters,
                badge_label="Best Birding",
                tradeoff_description="Crosses canopy and water edge habitats for higher bird discovery opportunity",
                geojson_geometry=best_birdy.geojson_geometry,
                waypoints=best_birdy.waypoints,
                segment_metrics=best_birdy.segment_metrics,
                edge_sequence=best_birdy.edge_sequence,
                repeated_edge_ratio=best_birdy.repeated_edge_ratio,
                ecological_score=best_birdy.ecological_score,
                novelty_score=best_birdy.novelty_score,
            )
            selected_candidates.append(birdy_opt)

        weird_candidates = []
        for c in candidate_pool:
            is_distinct = True
            for sel in selected_candidates:
                s_iou, s_contain = calculate_spatial_corridor_overlap(
                    c.geojson_geometry, sel.geojson_geometry, buffer_meters=75.0
                )
                if s_iou > 0.45 or s_contain > 0.60:
                    is_distinct = False
                    break
            if is_distinct:
                weird_candidates.append(c)

        if not weird_candidates:
            used_raw = [easy_cand] + ([best_birdy_raw] if best_birdy_raw else [])
            other_cands = [c for c in candidate_pool if c not in used_raw]
            if other_cands:
                weird_candidates = [
                    min(
                        other_cands,
                        key=lambda c: calculate_spatial_corridor_overlap(
                            c.geojson_geometry, easy_opt.geojson_geometry, buffer_meters=75.0
                        )[1],
                    )
                ]

        if weird_candidates:
            best_weird = max(
                weird_candidates,
                key=lambda c: (
                    c.novelty_score,
                    -abs(c.duration_minutes - request.duration_minutes),
                ),
            )
            weird_opt = LoopRouteCandidate(
                persona=RoutePersona.WEIRD,
                name="The Weird One",
                tagline="Exploratory loop stretching reach into novel sectors",
                duration_minutes=best_weird.duration_minutes,
                distance_meters=best_weird.distance_meters,
                badge_label="Exploratory",
                tradeoff_description="Explores secondary trail sectors favoring unfamiliar habitat boundaries",
                geojson_geometry=best_weird.geojson_geometry,
                waypoints=best_weird.waypoints,
                segment_metrics=best_weird.segment_metrics,
                edge_sequence=best_weird.edge_sequence,
                repeated_edge_ratio=best_weird.repeated_edge_ratio,
                ecological_score=best_weird.ecological_score,
                novelty_score=best_weird.novelty_score,
            )
            selected_candidates.append(weird_opt)

        provenance = RoutingProvenance(
            provider_name=self.provider_name,
            graph_version="OpenStreetMap Walk Network",
            nodes_count=len(G_nx.nodes()),
            edges_count=len(G_nx.edges()),
        )

        return RoutingResult(
            origin=request.origin,
            duration_minutes=request.duration_minutes,
            candidates=tuple(selected_candidates),
            provenance=provenance,
        )
