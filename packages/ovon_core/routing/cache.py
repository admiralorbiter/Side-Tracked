"""Spatial Graph Tile Cache Manager for OSM Pedestrian Networks."""

import pickle
from pathlib import Path

import networkx as nx

from packages.ovon_core.domain import SpatialCellId


class GraphCacheManager:
    """Manages local disk persistence for downloaded OSM spatial graph tiles."""

    def __init__(self, cache_dir: Path | str | None = None):
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path("data/cache/osm")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, cell: SpatialCellId) -> Path:
        filename = f"{cell.to_string().replace(':', '_')}.pickle"
        return self.cache_dir / filename

    def get_graph_for_cell(self, cell: SpatialCellId) -> nx.MultiDiGraph | None:
        """Retrieve cached NetworkX spatial graph for an H3 SpatialCellId if available."""
        file_path = self._get_file_path(cell)
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

    def save_graph_for_cell(self, cell: SpatialCellId, graph: nx.MultiDiGraph) -> Path:
        """Save a NetworkX spatial graph to local disk cache."""
        file_path = self._get_file_path(cell)
        with open(file_path, "wb") as f:
            pickle.dump(graph, f, protocol=pickle.HIGHEST_PROTOCOL)
        return file_path
