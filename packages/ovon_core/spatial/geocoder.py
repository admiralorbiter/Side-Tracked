"""Geocoder Provider ABC, Nominatim implementation, and caching for OVON Core."""

import hashlib
import json
import time
import urllib.parse
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path

from packages.ovon_core.domain import Coordinate, SpatialCellId
from packages.ovon_core.spatial.h3_indexer import is_within_kc_pilot_bounds, lat_lng_to_h3_cell

NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org"
USER_AGENT = "Sidetrack/0.1 (nature-walk-planner; contact@sidetrack.app)"


@dataclass(frozen=True, slots=True)
class GeocodeResult:
    """Result of an address geocoding or reverse-geocoding operation."""

    coordinate: Coordinate
    display_name: str
    cell: SpatialCellId
    address_details: dict = field(default_factory=dict, compare=False)


class GeocoderProvider(ABC):
    """Abstract Base Class for spatial geocoders."""

    @abstractmethod
    def geocode(self, query: str) -> GeocodeResult | None:
        """Geocode an address or place string into a GeocodeResult."""
        pass

    @abstractmethod
    def reverse_geocode(self, coord: Coordinate) -> GeocodeResult | None:
        """Reverse geocode a Coordinate into a GeocodeResult."""
        pass


class NominatimGeocoderProvider(GeocoderProvider):
    """OpenStreetMap Nominatim API Geocoder with SHA256 hashed query disk caching and rate limiting."""

    def __init__(self, cache_dir: Path | str | None = None, rate_limit_seconds: float = 1.0):
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path("data/cache/geocoder")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.rate_limit_seconds = rate_limit_seconds
        self._last_request_time: float = 0.0

    def _get_cache_path(self, key: str) -> Path:
        hashed_key = hashlib.sha256(key.lower().strip().encode("utf-8")).hexdigest()
        return self.cache_dir / f"geo_{hashed_key}.json"

    def _read_cache(self, key: str) -> dict | None:
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
            except Exception:
                return None
        return None

    def _write_cache(self, key: str, data: dict) -> None:
        cache_path = self._get_cache_path(key)
        try:
            # Preserve privacy: cache coordinates and coarse display name without raw query string
            sanitized_data = {
                "lat": data.get("lat"),
                "lon": data.get("lon"),
                "display_name": data.get("display_name"),
            }
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(sanitized_data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _enforce_rate_limit(self) -> None:
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < self.rate_limit_seconds:
            time.sleep(self.rate_limit_seconds - elapsed)
        self._last_request_time = time.time()

    def geocode(self, query: str) -> GeocodeResult | None:
        """Geocode an input address query string."""
        clean_query = query.strip()
        if not clean_query:
            return None

        cache_key = f"geocode_{clean_query}"
        cached = self._read_cache(cache_key)
        if cached:
            return self._build_geocode_result_from_dict(cached)

        self._enforce_rate_limit()

        params = {
            "q": clean_query,
            "format": "json",
            "addressdetails": 1,
            "limit": 1,
            "countrycodes": "us",
        }
        url = f"{NOMINATIM_BASE_URL}/search?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

        try:
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                if resp.status == 200:
                    results = json.loads(resp.read().decode("utf-8"))
                    if results and isinstance(results, list):
                        data = results[0]
                        self._write_cache(cache_key, data)
                        return self._build_geocode_result_from_dict(data)
        except Exception:
            return None
        return None

    def reverse_geocode(self, coord: Coordinate) -> GeocodeResult | None:
        """Reverse geocode a Coordinate into a display name."""
        cache_key = f"reverse_{coord.latitude:.5f}_{coord.longitude:.5f}"
        cached = self._read_cache(cache_key)
        if cached:
            return self._build_geocode_result_from_dict(cached)

        self._enforce_rate_limit()

        params = {
            "lat": str(coord.latitude),
            "lon": str(coord.longitude),
            "format": "json",
            "addressdetails": 1,
        }
        url = f"{NOMINATIM_BASE_URL}/reverse?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

        try:
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    if data and isinstance(data, dict):
                        self._write_cache(cache_key, data)
                        return self._build_geocode_result_from_dict(data)
        except Exception:
            return None
        return None

    def _build_geocode_result_from_dict(self, data: dict) -> GeocodeResult | None:
        try:
            lat = float(data.get("lat", 0.0))
            lon = float(data.get("lon", 0.0))
            coord = Coordinate(lat, lon, allow_zero=True)

            if not is_within_kc_pilot_bounds(coord):
                return None

            disp_name = data.get("display_name", f"{lat:.4f}, {lon:.4f}")
            cell = lat_lng_to_h3_cell(coord, resolution=8)

            return GeocodeResult(
                coordinate=coord,
                display_name=disp_name,
                cell=cell,
                address_details=data.get("address", {}),
            )
        except (ValueError, TypeError, Exception):
            return None
