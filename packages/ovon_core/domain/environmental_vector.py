"""Environmental Feature Vector and Schema Domain Models."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from packages.ovon_core.domain.habitat import HabitatType


@dataclass(frozen=True, slots=True)
class EnvironmentalSchema:
    """Versioned schema definition for environmental feature vectors."""

    schema_id: str
    feature_names: tuple[str, ...]
    units: tuple[str, ...]
    data_release_ids: tuple[str, ...]


SIDETRACK_ENV_SCHEMA_V1 = EnvironmentalSchema(
    schema_id="sidetrack_env_v1",
    feature_names=(
        "canopy_cover_percent",
        "impervious_surface_percent",
        "water_edge_distance_m",
        "elevation_m",
        "slope_gradient_percent",
    ),
    units=("%", "%", "m", "m", "%"),
    data_release_ids=("nlcd_canopy_2025", "nlcd_impervious_2025", "nhd_water_v2", "usgs_3dep_10m"),
)


@dataclass(frozen=True, slots=True)
class EnvironmentalFeatureVector:
    """Continuous environmental covariate vector extracted along spatial geometries."""

    schema: EnvironmentalSchema
    values: tuple[float, ...]
    status: str = "ok"  # "ok" or "degraded_fallback"
    extracted_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self) -> None:
        if len(self.values) != len(self.schema.feature_names):
            raise ValueError(
                f"Vector value count ({len(self.values)}) does not match schema feature count ({len(self.schema.feature_names)})."
            )

    def get_feature(self, name: str) -> float:
        """Return the value for a named environmental feature."""
        if name not in self.schema.feature_names:
            raise KeyError(f"Feature '{name}' not found in schema '{self.schema.schema_id}'.")
        idx = self.schema.feature_names.index(name)
        return self.values[idx]

    @property
    def canopy_cover_percent(self) -> float:
        return self.get_feature("canopy_cover_percent")

    @property
    def water_edge_distance_m(self) -> float:
        return self.get_feature("water_edge_distance_m")

    @property
    def impervious_surface_percent(self) -> float:
        return self.get_feature("impervious_surface_percent")

    @property
    def slope_gradient_percent(self) -> float:
        return self.get_feature("slope_gradient_percent")

    @property
    def elevation_m(self) -> float:
        return self.get_feature("elevation_m")

    def derive_habitat_type(self) -> HabitatType:
        """Rule-based derivation of HabitatType from real environmental feature values."""
        if self.water_edge_distance_m <= 75.0:
            return HabitatType.POND_WATER_EDGE
        if self.canopy_cover_percent >= 45.0:
            return HabitatType.MATURE_CANOPY
        if self.canopy_cover_percent >= 20.0 and self.impervious_surface_percent < 30.0:
            return HabitatType.ORCHARD_EDGE
        return HabitatType.OPEN_PARKLAND

    def to_dict(self) -> dict[str, Any]:
        """Convert feature vector to dictionary representation."""
        res = {name: val for name, val in zip(self.schema.feature_names, self.values)}
        res["schema_id"] = self.schema.schema_id
        res["status"] = self.status
        return res


def create_default_environmental_vector() -> EnvironmentalFeatureVector:
    """Create a clean default environmental vector when spatial rasters are unmapped."""
    return EnvironmentalFeatureVector(
        schema=SIDETRACK_ENV_SCHEMA_V1,
        values=(15.0, 10.0, 250.0, 260.0, 2.0),
        status="degraded_fallback",
    )
