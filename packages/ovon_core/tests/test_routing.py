"""Unit and integration tests for OSMnx + igraph routing solver (Sprint 4 & 6.5)."""

import networkx as nx

from packages.ovon_core.domain import Coordinate, LoopRequest, RoutePersona
from packages.ovon_core.routing import (
    GraphCacheManager,
    OSMnxIgraphRoutingProvider,
    RoutingResult,
)


def test_graph_cache_manager_path(tmp_path):
    cache = GraphCacheManager(cache_dir=tmp_path)
    assert cache.cache_dir == tmp_path


def test_osmnx_igraph_routing_provider_initialization():
    provider = OSMnxIgraphRoutingProvider()
    assert provider.provider_name == "OSMnx + igraph (Pedestrian)"


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
    assert len(result.candidates) == 3
    assert result.provenance.provider_name == "OSMnx + igraph (Pedestrian)"

    personas = [c.persona for c in result.candidates]
    assert RoutePersona.EASY in personas
    assert RoutePersona.BIRDY in personas
    assert RoutePersona.WEIRD in personas

    for cand in result.candidates:
        assert cand.duration_minutes > 0
        assert cand.distance_meters > 0
        # Time budget enforcement check: duration must be within budget window
        assert req.duration_minutes * 0.40 <= cand.duration_minutes <= req.duration_minutes * 1.25
        assert "LineString" in cand.geojson_geometry["type"]
        assert len(cand.geojson_geometry["coordinates"]) >= 3

        # Start and end coordinates must form a closed loop (return to origin within 50m)
        start_coords = cand.geojson_geometry["coordinates"][0]
        end_coords = cand.geojson_geometry["coordinates"][-1]

        start_c = Coordinate(start_coords[1], start_coords[0])
        end_c = Coordinate(end_coords[1], end_coords[0])
        dist_between = start_c.haversine_distance_meters(end_c)
        assert dist_between < 50.0
