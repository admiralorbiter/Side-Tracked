"""Spatial Graph Tile Cache Manager for OSM Pedestrian Networks."""

import pickle
from pathlib import Path

import networkx as nx

from packages.ovon_core.domain import SpatialCellId

DEFAULT_MAX_BUDGET_RADIUS_METERS = 2500.0
GRAPH_SCHEMA_VERSION = "osmnx_v1"


class GraphCacheManager:
    """Manages local disk persistence for downloaded max-budget OSM spatial graph tiles."""

    def __init__(self, cache_dir: Path | str | None = None):
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path("data/cache/osm")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_file_path(
        self, cell: SpatialCellId, radius_meters: float = DEFAULT_MAX_BUDGET_RADIUS_METERS
    ) -> Path:
        cell_str = cell.to_string().replace(":", "_")
        filename = f"{cell_str}_r{int(radius_meters)}_{GRAPH_SCHEMA_VERSION}.pickle"
        return self.cache_dir / filename

    def get_graph_for_cell(
        self, cell: SpatialCellId, radius_meters: float = DEFAULT_MAX_BUDGET_RADIUS_METERS
    ) -> nx.MultiDiGraph | None:
        """Retrieve cached NetworkX spatial graph for an H3 SpatialCellId if available."""
        file_path = self._get_file_path(cell, radius_meters)
        if not file_path.exists():
            return None

        try:
            with open(file_path, "rb") as f:
                graph = pickle.load(f)
                if isinstance(graph, nx.MultiDiGraph):
                    return graph
        except (pickle.PickleError, OSError):
            return None
        return None

    def save_graph_for_cell(
        self,
        cell: SpatialCellId,
        graph: nx.MultiDiGraph,
        radius_meters: float = DEFAULT_MAX_BUDGET_RADIUS_METERS,
    ) -> Path:
        """Save a NetworkX spatial graph to local disk cache."""
        file_path = self._get_file_path(cell, radius_meters)
        with open(file_path, "wb") as f:
            pickle.dump(graph, f, protocol=pickle.HIGHEST_PROTOCOL)
        return file_path
