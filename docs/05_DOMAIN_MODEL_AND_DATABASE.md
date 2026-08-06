# Domain Model and Database

## Modeling principles

1. A taxon has one canonical internal identity.
2. An observation event is separate from a species outcome.
3. Presence-only evidence is not a checklist.
4. A route request is separate from a generated route artifact.
5. A candidate location is separate from a route stop action.
6. Environmental vectors have named, versioned schemas.
7. Provenance is a first-class relation, not a note.
8. Raw addresses are transient by default.
9. Sensitive taxa and locations are handled before rendering.
10. Large analytical surfaces remain outside ordinary relational rows.

---

## Core value objects

### TaxonId

Stable internal key. Prefer a taxonomic concept identifier or normalized scientific-name concept. Common names are presentation data.

```python
@dataclass(frozen=True)
class TaxonRef:
    taxon_id: str
    scientific_name: str
    common_name: str
    rank: str
    taxonomy_version: str
```

### Coordinate

```python
@dataclass(frozen=True)
class Coordinate:
    latitude: float
    longitude: float
```

Validate ranges and never default missing coordinates to `(0, 0)`.

### SpatialCellId

A versioned grid identifier:

```text
kc_3km_v1:cell_472
```

The grid version is part of the identity.

### EnvironmentalSchema

```python
@dataclass(frozen=True)
class EnvironmentalSchema:
    schema_id: str
    feature_names: tuple[str, ...]
    units: tuple[str, ...]
    data_release_ids: tuple[str, ...]
```

### EnvironmentalVector

```python
@dataclass(frozen=True)
class EnvironmentalVector:
    schema_id: str
    values: tuple[float, ...]
```

### ProvenanceRef

```python
@dataclass(frozen=True)
class ProvenanceRef:
    source_id: str
    source_type: str
    release_id: str | None
    retrieved_at: datetime | None
    transformation_id: str | None
    evidence_status: str
```

---

## Evidence model

Separate event and species outcomes.

### ObservationEvent

Fields:

- `event_id`
- `source_id`
- `source_event_id`
- `observed_at`
- `latitude`
- `longitude`
- `cell_id`
- `protocol`
- `duration_minutes`
- `distance_km`
- `observer_count`
- `complete_checklist`
- `effort_valid`
- `provenance_id`

### SpeciesObservation

Fields:

- `event_id`
- `taxon_id`
- `evidence_type`
- `detected`
- `count`
- `sensitive`
- `validation_status`

Evidence types:

- complete-checklist detection
- complete-checklist non-detection
- presence-only
- photo-verified presence
- acoustic candidate
- acoustic verified
- structured point-count detection
- structured point-count non-detection

A recent eBird occurrence must remain presence-only. Only EBD/SED events that satisfy the complete-checklist rules can create explicit non-detections.

---

## Route model

### RouteRequest

Fields:

- request ID
- created time
- route type
- coarse origin cell
- destination cell when present
- travel mode
- budget
- detour budget
- departure time
- observer profile
- preference set
- accessibility constraints
- requested taxa/bundle
- model/data manifest ID
- raw address retained: always false in MVP

### RouteOption

Fields:

- route ID
- request ID
- route label
- rank
- total duration
- distance
- travel duration
- observation duration
- access/setup duration
- waiting duration
- route geometry artifact
- utility total
- provenance status
- routing provider/version
- model/data manifest
- feasible flag
- validation messages

### RouteStopAction

Fields:

- route ID
- sequence
- candidate ID
- arrival offset
- observation duration
- stop reward
- explanation
- protocol
- access confidence

### RouteSegment

Fields:

- route ID
- sequence
- geometry
- length
- duration
- environmental summary
- edge reward
- expected taxa summary
- comfort summary

The route optimizer should return immutable stop actions rather than mutating candidate-site records.

---

## Candidate location model

Fields:

- candidate ID
- region ID
- candidate type
- name
- coordinate
- cell ID
- environmental vector ID
- public access state
- safety review state
- accessibility state
- opening-hours reference
- source/provenance
- active date range

Access states:

- verified public
- likely public
- unknown
- restricted

Safety states:

- reviewed
- unknown
- seasonal
- excluded

Accessibility states should preserve unknown separately from unavailable.

---

## Species prediction model

A prediction record is versioned by:

- model ID
- data release
- taxon ID
- spatial cell/location
- date/time bucket
- observer profile
- duration
- protocol

Fields:

- relative presence
- conditional detectability
- encounter estimate
- epistemic uncertainty
- aleatoric uncertainty
- calibration status
- extrapolation flag
- provenance
- sensitive display policy

Predictions should usually be stored as Parquet/model artifacts, not as millions of ordinary SQLite rows. SQLite may cache a bounded subset.

---

## Suggested SQLite tables

```sql
taxa
taxonomy_aliases
data_sources
data_releases
transformations
artifact_manifests

regions
spatial_grids
spatial_cells
environmental_schemas
environmental_vectors
candidate_locations
candidate_location_rtree

observation_events
species_observations

model_registry
model_artifacts
prediction_cache

route_requests
route_options
route_stops
route_segments
route_explanations

anonymous_sessions
user_accounts
user_preferences
route_feedback

studies
study_conditions
study_participants
route_assignments
field_observations

sensitive_taxa
sensitive_location_rules
access_reports
```

Not all tables belong in the MVP migration. The schema should be introduced by milestone.

---

## SQLite spatial indexing

SQLite’s R*Tree extension can index bounding boxes. Use it for:

- candidate locations within route bounds;
- evidence event bounding-box queries;
- route segment intersection prefiltering;
- spatial-cell lookup support.

Example:

```sql
CREATE VIRTUAL TABLE candidate_location_rtree USING rtree(
    candidate_id,
    min_lon, max_lon,
    min_lat, max_lat
);
```

Keep authoritative geometry in the base table or artifact. The RTree is an index.

---

## Artifact registry

Every analytical artifact should have:

- artifact ID
- artifact type
- path or URI
- checksum
- size
- created time
- generating command
- source release IDs
- code version
- parameters
- spatial bounds
- temporal coverage
- schema version
- license/terms note
- sensitivity classification

Artifact types:

- GeoTIFF
- Parquet
- model file
- route graph extract
- matrix cache
- species metadata snapshot
- taxon crosswalk
- report

---

## Canonical taxonomy

Taxonomy normalization pipeline:

1. ingest provider taxon identity;
2. preserve raw provider name and ID;
3. resolve to current project taxonomy version;
4. store alias/crosswalk;
5. mark unresolved concepts;
6. never join solely on a common name.

Example alias table:

| provider | provider ID | raw name | project taxon ID | status |
|---|---|---|---|---|
| eBird | species code | Passerina cyanea | taxon:passerina_cyanea:v2025 | exact |
| GBIF | taxonKey | Indigo Bunting | taxon:passerina_cyanea:v2025 | resolved |
| iNaturalist | taxon ID | Passerina cyanea | taxon:passerina_cyanea:v2025 | exact |

---

## Dates and seasonal keys

Store:

- source-local timestamp when available;
- UTC timestamp when derivable;
- local date;
- ISO week;
- project annual-week key;
- timezone;
- uncertainty when time is incomplete.

Do not overwrite source dates with ingestion time.

---

## Provenance status model

Example route provenance:

```json
{
  "routing": "VALHALLA_OSM_2026_07",
  "environment": "ANNUAL_NLCD_C1_2_2025",
  "evidence": [
    "GBIF_LIVE_OCCURRENCE",
    "INATURALIST_LIVE_OCCURRENCE",
    "EBIRD_CURATED_DEMO"
  ],
  "prediction": "PROVISIONAL_HABITAT_ANALOG_V2",
  "calibration": "NOT_EVALUATED"
}
```

User-facing short form:

> Live occurrence records + provisional habitat model; not a calibrated encounter probability.

---

## Privacy model

The `route_requests` table stores a coarse origin cell, not raw address text. A transient in-memory object may hold the address during geocoding.

Optional future account location:

- user-selected label;
- coarse cell or intentionally shifted point;
- encryption and retention policy;
- explicit consent.

---

## Data retention

MVP recommendation:

- raw address: not persisted;
- exact anonymous origin coordinate: delete after route generation or retain only in short-lived logs disabled by default;
- coarse origin cell: retain with route request;
- generated route geometry: retain for reproducibility;
- external provider response: cache only when terms allow;
- route feedback: retain without direct identity;
- sensitive evidence: never expose through ordinary export.

---

## Migration strategy

Use ordered SQL migrations. Every migration should:

- be reversible when practical;
- include a local test on a copy of the database;
- avoid mixing data backfills with schema changes when the backfill is large;
- record application version;
- never silently reinterpret an existing column.

A semantic change such as “recent eBird occurrence is no longer a checklist” requires a data migration or cache invalidation, not only a code change.

---

# Species media and field-guide model

## MediaAsset

```python
@dataclass(frozen=True)
class MediaAsset:
    media_asset_id: str
    taxon_id: str
    media_type: Literal["image", "audio", "sonogram"]
    media_role: str
    source_name: str
    source_asset_id: str
    original_url: str
    creator_name: str
    license_code: str
    license_url: str
    attribution_text: str
    mime_type: str | None
    duration_seconds: float | None
    cached_path: str | None
    checksum_sha256: str | None
    retrieved_at: datetime
    status: Literal["active", "unavailable", "replaced", "revoked"]
```

The media record is invalid if creator, license, source asset ID, or attribution is missing.

## TaxonMediaSelection

A taxon may have many source assets, but the public application uses an editorial selection:

```python
@dataclass(frozen=True)
class TaxonMediaSelection:
    taxon_id: str
    primary_image_id: str | None
    primary_song_id: str | None
    primary_call_id: str | None
    selected_by: str
    selected_at: datetime
    selection_reason: str
```

Selections are versioned so a route artifact can reproduce the field pack that a user actually saw.

## FieldCue

```python
@dataclass(frozen=True)
class FieldCue:
    field_cue_id: str
    taxon_id: str
    audience: Literal["beginner", "intermediate", "advanced"]
    look_for: tuple[str, ...]
    listen_for: str | None
    where_to_look: str | None
    where_to_listen: str | None
    confusion_taxon_ids: tuple[str, ...]
    ethics_note: str | None
    content_source: str
    version: str
```

Field cues are content artifacts, not predictions. A route service selects cues based on segment habitat, season, observer profile, and available media.

## RouteFieldPack

```python
@dataclass(frozen=True)
class RouteFieldPack:
    route_id: str
    taxon_cards: tuple[RouteTaxonCard, ...]
    segment_cues: tuple[SegmentFieldCue, ...]
    media_manifest_id: str
    generated_at: datetime
    provenance: ProvenanceSummary
```

## Suggested media tables

```text
media_assets
media_asset_versions
taxon_media_selections
field_cues
field_cue_versions
route_field_packs
route_field_pack_items
media_access_audit
```

### `media_assets`

Important columns:

- `media_asset_id` primary key;
- `taxon_id` foreign key;
- `media_type`;
- `source_name`;
- `source_asset_id`;
- `original_url`;
- `creator_name`;
- `license_code`;
- `license_url`;
- `attribution_text`;
- `cached_path`;
- `checksum_sha256`;
- `status`;
- `retrieved_at`;
- `last_verified_at`.

Unique constraint:

```text
(source_name, source_asset_id)
```

### `field_cues`

Store structured fields rather than one large HTML blob. HTML is rendered by the application.

## Media provenance status

A route field pack should summarize:

- number of active images;
- number of active audio clips;
- number of missing-media fallbacks;
- media manifest version;
- whether every displayed asset passed the current license allowlist;
- whether any asset is linked rather than cached.

## Address and session model

The first planner steps create a transient planning session. The session stores:

- journey intent;
- geocoded coordinate;
- coarse origin cell when needed;
- time budget;
- travel mode;
- optional preferences;
- expiration time.

It does not store the raw address by default. The raw string should not appear in ordinary logs.
