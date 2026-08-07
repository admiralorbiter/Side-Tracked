"""Unit and integration tests for advanced spatial graph routing solver (Sprint 8.5)."""

import networkx as nx

from packages.ovon_core.domain import Coordinate, LoopRequest, RoutePersona
from packages.ovon_core.fixtures import ROUTE_BIRDY, ROUTE_EASY, ROUTE_WEIRD
from packages.ovon_core.routing import (
    GraphCacheManager,
    OSMnxIgraphRoutingProvider,
    RoutingResult,
    TradeoffExplanationGenerator,
)
from packages.ovon_core.routing.osmnx_solver import (
    calculate_jaccard_edge_overlap,
    calculate_repeated_edge_ratio,
    calculate_spatial_corridor_overlap,
)


def test_graph_cache_manager_path(tmp_path):
    cache = GraphCacheManager(cache_dir=tmp_path)
    assert cache.cache_dir == tmp_path


def test_osmnx_igraph_routing_provider_initialization():
    provider = OSMnxIgraphRoutingProvider()
    assert provider.provider_name == "OSMnx + igraph (Pedestrian)"


def test_jaccard_edge_overlap_metric():
    epath1 = [1, 2, 3, 4]
    epath2 = [3, 4, 5, 6]
    overlap = calculate_jaccard_edge_overlap(epath1, epath2)
    assert 0.0 < overlap < 1.0
    assert calculate_jaccard_edge_overlap(epath1, epath1) == 1.0


def test_repeated_edge_ratio_backtracking_metric():
    G_nx = nx.MultiDiGraph()
    G_nx.add_edge(1, 2, key=0, length=100.0)
    G_nx.add_edge(2, 3, key=0, length=100.0)

    # Path with out-and-back repetition: 1->2, 2->3, 3->2, 2->1
    seq = [(1, 2, 0), (2, 3, 0), (3, 2, 0), (2, 1, 0)]
    b_r = calculate_repeated_edge_ratio(seq, G_nx)
    assert b_r > 0.0


def test_spatial_corridor_overlap_metric():
    geom_a = {
        "type": "LineString",
        "coordinates": [
            [-94.5906, 39.0347],
            [-94.5910, 39.0350],
            [-94.5915, 39.0355],
        ],
    }
    geom_b = {
        "type": "LineString",
        "coordinates": [
            [-94.5906, 39.0347],
            [-94.5911, 39.0351],
            [-94.5915, 39.0355],
        ],
    }
    s_iou, s_contain = calculate_spatial_corridor_overlap(geom_a, geom_b, buffer_meters=75.0)
    assert 0.0 < s_iou <= 1.0
    assert 0.0 < s_contain <= 1.0


def test_tradeoff_explanation_generator():
    gen = TradeoffExplanationGenerator()
    easy_desc = gen.generate_tradeoff_description(ROUTE_EASY, ROUTE_EASY)
    birdy_desc = gen.generate_tradeoff_description(ROUTE_BIRDY, ROUTE_EASY)
    weird_desc = gen.generate_tradeoff_description(ROUTE_WEIRD, ROUTE_EASY)

    assert "Lowest physical effort" in easy_desc
    assert "Adds" in birdy_desc or "canopy" in birdy_desc
    assert "exploration" in weird_desc or "secondary" in weird_desc


def test_convert_nx_to_igraph_preserves_exact_multiedges():
    provider = OSMnxIgraphRoutingProvider()
    G_nx = nx.MultiDiGraph()
    G_nx.add_node(1, y=39.0347, x=-94.5906)
    G_nx.add_node(2, y=39.0360, x=-94.5900)
    G_nx.add_edge(1, 2, key=0, length=150.0)

    G_ig, node_to_idx, idx_to_node, node_coords, ig_edge_to_nx_key = provider._convert_nx_to_igraph(
        G_nx
    )

    assert len(G_ig.vs) == 2
    assert len(G_ig.es) == 1
    assert ig_edge_to_nx_key[0] == (1, 2, 0)
    assert G_ig.es[0]["weight"] == 150.0


def test_calculate_loop_returns_valid_budget_compliant_result():
    provider = OSMnxIgraphRoutingProvider()
    loose_park = Coordinate(39.0347, -94.5906)
    req = LoopRequest(
        origin=loose_park, origin_name="Loose Park, Kansas City, MO", duration_minutes=45
    )

    result = provider.calculate_loop(req)

    assert isinstance(result, RoutingResult)
    assert len(result.candidates) >= 1
    assert result.provenance.provider_name == "OSMnx + igraph (Pedestrian)"

    personas = [c.persona for c in result.candidates]
    assert RoutePersona.EASY in personas

    for cand in result.candidates:
        assert cand.duration_minutes > 0
        assert cand.distance_meters > 0
        assert req.duration_minutes * 0.80 <= cand.duration_minutes <= req.duration_minutes * 1.05
        assert "LineString" in cand.geojson_geometry["type"]
        assert len(cand.geojson_geometry["coordinates"]) >= 3

        # Start and end coordinates must form a closed loop
        start_coords = cand.geojson_geometry["coordinates"][0]
        end_coords = cand.geojson_geometry["coordinates"][-1]

        start_c = Coordinate(start_coords[1], start_coords[0])
        end_c = Coordinate(end_coords[1], end_coords[0])
        dist_between = start_c.haversine_distance_meters(end_c)
        assert dist_between <= 25.0
