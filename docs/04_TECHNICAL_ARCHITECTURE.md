# Technical Architecture

## Architecture goals

The architecture must support two different rates of change:

- The **product shell** should remain stable and understandable.
- The **ecological and optimization methods** should be replaceable as research improves.

The primary rule is:

> Flask views depend on stable service contracts, not experimental implementations.

---

## Recommended stack

### Web application

- Flask 3.x
- application factory
- blueprints
- Jinja templates
- HTMX for partial updates
- semantic HTML
- project CSS
- minimal JavaScript map adapter
- SQLite
- Alembic or Flask-Migrate for schema migrations

Flask’s official documentation recommends application factories for larger, testable applications and blueprints for modular components. The app factory makes it possible to create differently configured instances for testing and development.

### Ecological and data core

- Python package `ovon_core`
- NumPy, pandas or Polars
- scikit-learn for initial calibrated models
- GeoPandas/Shapely for vector preprocessing
- Rasterio/Xarray for raster extraction when introduced
- DuckDB/Parquet for analytical datasets
- serialized model and data manifests

### Routing

Target provider: Valhalla.

Valhalla supports pedestrian, bicycle, automobile, and multimodal routes, time-distance matrices, route geometry, isochrones, map matching, and elevation. The matrix service is appropriate for optimized-route inputs, while isochrones are appropriate for generating reachable candidate regions.

### Database and artifacts

SQLite stores:

- application records;
- route requests;
- route outputs;
- user/session preferences;
- taxon metadata;
- candidate metadata;
- model/data manifest references;
- study assignments.

Large rasters, Parquet tables, and model artifacts live in files or object storage. SQLite stores paths, hashes, versions, and bounds.

### Optional Rust

Rust is not required for the MVP. Add it only after profiling identifies a stable bottleneck such as:

- repeated large route searches;
- local-search iteration;
- matrix transformations;
- exact small-instance optimization;
- batch simulation;
- spatial indexing unavailable through existing libraries.

PyO3 is the preferred bridge so Flask and Python services can call Rust without introducing a separate network service.

---

## Logical layers

```text
HTTP / HTML layer
        ↓
Application services
        ↓
Stable domain contracts
        ↓
Ecology | Opportunity | Routing | Evidence | Provenance
        ↓
Repositories and provider adapters
        ↓
SQLite | Parquet | GeoTIFF | Valhalla | external APIs
```

### Presentation layer

Responsibilities:

- parse requests;
- validate ordinary form input;
- call application service;
- render template or partial;
- never calculate ecological scores;
- never call routing APIs directly;
- never know raw file layouts.

### Application services

Examples:

- `PlanNatureLoop`
- `PlanNatureTrip`
- `BuildFieldPack`
- `CompareRouteMenu`
- `ExplainRoute`
- `RunSearchLabQuery`
- `RecordRouteFeedback`

They coordinate domain providers and repositories.

### Domain core

Contains:

- value objects;
- route request/option types;
- taxon identifiers;
- evidence records;
- ecological predictions;
- reward functions;
- provenance;
- validation rules.

The domain package must not import Flask.

### Infrastructure

Contains:

- SQLite repositories;
- Valhalla adapter;
- geocoder adapter;
- EBD/SED loaders;
- GBIF and iNaturalist adapters;
- raster stores;
- cache;
- file artifact registry.

---

## Flask application structure

```text
apps/web/app/
├── __init__.py
├── config.py
├── extensions.py
├── blueprints/
│   ├── planner/
│   │   ├── routes.py
│   │   ├── forms.py
│   │   └── services.py
│   ├── route_detail/
│   ├── species/
│   ├── search_lab/
│   ├── research/
│   ├── admin/
│   └── health/
├── templates/
│   ├── layouts/
│   ├── components/
│   ├── planner/
│   ├── routes/
│   ├── species/
│   └── errors/
└── static/
    ├── css/
    ├── js/map_adapter.js
    └── images/
```

Application factory:

```python
def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(DefaultConfig)

    if config:
        app.config.update(config)

    init_extensions(app)
    register_blueprints(app)
    register_error_handlers(app)
    register_cli(app)

    return app
```

Extensions should be created without binding to a global Flask instance and initialized in the factory.

---

## HTMX boundary

HTMX is suitable for:

- address lookup result list;
- route form validation;
- route-generation progress panel;
- route cards;
- route timeline;
- species field pack;
- filter changes;
- admin metadata pages.

The map remains a small JavaScript island. HTMX responses may include a JSON script block or `data-*` payload that the map adapter reads.

Avoid building a general front-end state framework.

---

## Core contracts

### Routing provider

```python
class RoutingProvider(Protocol):
    def geocode(self, query: str) -> list[GeocodedPlace]: ...

    def isochrone(
        self,
        origin: Coordinate,
        minutes: int,
        mode: TravelMode,
        departure_at: datetime | None,
    ) -> ReachableRegion: ...

    def matrix(
        self,
        coordinates: list[Coordinate],
        mode: TravelMode,
        departure_at: datetime | None,
    ) -> TravelMatrix: ...

    def route(
        self,
        coordinates: list[Coordinate],
        mode: TravelMode,
        departure_at: datetime | None,
        closed_loop: bool,
    ) -> RouteGeometry: ...
```

Geocoding may use a separate provider contract if deployment requires it.

### Species surface provider

```python
class SpeciesSurfaceProvider(Protocol):
    def predict(
        self,
        taxon_ids: list[TaxonId],
        locations: list[EcologicalLocation],
        observed_at: datetime,
        observer: ObserverProfile,
        durations_minutes: list[float],
    ) -> SpeciesSurfaceResult: ...
```

### Evidence repository

```python
class EvidenceRepository(Protocol):
    def query(
        self,
        taxon_ids: list[TaxonId],
        bounds: Bounds,
        time_window: TimeWindow,
        evidence_types: set[EvidenceType],
    ) -> list[SpeciesEvidence]: ...
```

### Environmental provider

```python
class EnvironmentalProvider(Protocol):
    @property
    def schema(self) -> EnvironmentalSchema: ...

    def at_point(self, coordinate: Coordinate) -> EnvironmentalVector: ...

    def along_geometry(
        self,
        geometry: LineString,
        interval_meters: float,
    ) -> list[EnvironmentalSample]: ...
```

### Route optimizer

```python
class EcologicalRouteOptimizer(Protocol):
    def loop(self, request: LoopRequest) -> list[RouteOption]: ...

    def point_to_point(self, request: TripRequest) -> list[RouteOption]: ...
```

### Reward function

```python
class RouteReward(Protocol):
    def stop_reward(
        self,
        site: CandidateSite,
        duration_minutes: float,
        context: RouteContext,
    ) -> RewardBreakdown: ...

    def edge_reward(
        self,
        segment: RouteSegment,
        context: RouteContext,
    ) -> RewardBreakdown: ...
```

This dynamic reward replaces static opportunity dictionaries for duration-sensitive modes.

---

## Route-planning request flow

### Nature Loop

1. Receive origin, budget, mode, priorities, and constraints.
2. Geocode or resolve map pin.
3. Do not persist raw address.
4. Generate an isochrone.
5. Find candidate stops and graph segments inside the region.
6. Load environmental features.
7. load evidence and model artifacts for the selected date.
8. calculate stop and edge rewards.
9. request the routing matrix.
10. construct several route alternatives.
11. request exact geometry for each final route.
12. verify time budget and return-to-origin.
13. build species and route explanations.
14. persist request metadata, coarse origin, artifact versions, and route result.
15. render comparison.

### Point-to-point

1. Obtain baseline fastest route.
2. generate candidate detour corridors or waypoints.
3. calculate ecological value along baseline and alternatives.
4. solve for multiple detour budgets.
5. identify Pareto-efficient routes.
6. render frontier and route alternatives.

---

## Candidate generation

Do not treat every raster cell as a route stop.

Candidate types:

- public observation points;
- park entrances;
- trail intersections;
- habitat transitions;
- transit nodes;
- verified rest points;
- route-segment sample points;
- organization-defined survey points.

Candidate records must distinguish:

- `STOP`
- `CORRIDOR_SAMPLE`
- `ACCESS_POINT`
- `ORIGIN`
- `TRANSIT_NODE`
- `RESTRICTED`
- `SENSITIVE`

An isochrone constrains the search region before the optimizer builds a matrix.

---

## Caching

Cache by semantic key:

```text
routing_matrix:
    provider_version
    travel_mode
    sorted coordinate hashes
    departure bucket

species_surface:
    model_id
    data_release_id
    taxon_ids
    cell_ids
    date/time bucket
    observer profile
    duration bucket

environment:
    dataset_release
    schema_version
    spatial key
```

External API responses should retain:

- provider;
- request time;
- status;
- fallback state;
- license/attribution metadata.

Never cache a raw address as the lookup key in a shared persistent cache unless the privacy policy explicitly allows it. Use a transient request cache or coordinate hash.

---

## Background and offline work

The first version does not require a distributed queue. Use CLI jobs for:

- downloading data;
- normalizing taxa;
- extracting environmental features;
- creating candidate sites;
- building route graph extracts;
- fitting models;
- generating manifests;
- refreshing public metadata.

Example:

```bash
flask --app app:create_app data refresh-occurrences
flask --app app:create_app data build-environment-kc
flask --app app:create_app model fit --portfolio kc-v1
flask --app app:create_app artifacts verify
```

If long-running jobs later need a worker, add one after the command contracts are stable.

---

## Error strategy

Typed domain errors:

- `NoFeasibleRoute`
- `RoutingProviderUnavailable`
- `GeocodingFailed`
- `OutsideSupportedRegion`
- `ModelUnavailable`
- `InsufficientEvidence`
- `EnvironmentalSchemaMismatch`
- `SensitiveTaxonSuppressed`
- `AccessUnknown`
- `ArtifactVersionMismatch`

The user sees an actionable explanation. Logs retain technical details without storing unnecessary personal location data.

---

## Configuration

Environment-specific settings:

- database path;
- data directory;
- artifact registry;
- routing endpoint;
- geocoder endpoint;
- region bounds;
- default model/data versions;
- secret key;
- rate limits;
- privacy retention settings;
- sensitive-taxon policy.

Do not hard-code API tokens, absolute local paths, or provider URLs in domain modules.

---

## Deployment evolution

### Local development

- Flask development server
- SQLite
- local Valhalla or controlled provider
- local artifact files

### Small regional deployment

- production WSGI server
- reverse proxy
- SQLite in WAL mode if concurrency remains modest
- scheduled local data refreshes
- backed-up artifact directory

### Larger deployment

Only when measured:

- PostgreSQL/PostGIS
- separate worker
- object storage
- Rust optimization extension
- multiple regional routing/data packages

Do not introduce these merely because the moonshot is large.

---

# Species media architecture

Species photos, audio, attribution, and field cues are stable product capabilities, not template decorations.

## Components

```text
MediaProvider
├── search_taxon_media(taxon_id, media_type)
├── fetch_metadata(source_asset_id)
└── fetch_asset(source_asset_id)          # only when terms permit

MediaRepository
├── selected_assets_for_taxon(taxon_id)
├── save_manifest(asset)
├── mark_unavailable(asset_id, reason)
└── verify_cached_asset(asset_id)

FieldGuideService
├── build_route_pack(route, observer_profile)
├── cues_for_segment(segment_id)
└── species_card(taxon_id)

AttributionRenderer
└── render(asset_id, display_context)
```

## Source boundary

The provider adapter returns metadata and never decides whether an asset may be used. A central media policy evaluates:

- source;
- license;
- commercial/noncommercial constraints;
- attribution requirements;
- derivative restrictions;
- whether caching is permitted;
- whether a deep link is required;
- current asset availability.

The application must not infer reuse permission from an image URL alone.

## Media request flow

1. `FieldGuideService` requests the selected media for a taxon.
2. `MediaRepository` returns an active, verified asset or a missing-media state.
3. The template renders the media, attribution, and license link together.
4. Audio uses user-initiated playback and never autoplays.
5. Missing or invalid media falls back to text guidance without breaking the route.

## Storage

SQLite stores media metadata and selections. Cached binary assets live in filesystem or object storage and are addressed by checksum. Each cached asset has:

- source asset ID;
- original URL;
- retrieval date;
- creator;
- license and license URL;
- checksum;
- media MIME type;
- transformation history;
- active/revoked status.

## Front-end media boundary

Use native semantic controls where possible:

- `<img>` with meaningful alt text;
- `<audio controls preload="metadata">` or `preload="none"`;
- one small controller to prevent overlapping playback;
- visible attribution adjacent to the asset;
- no hidden or automatic audio.

HTMX may load a species card or field pack. Playback remains a small browser-side behavior and does not require a single-page application.

---

# Intent-first planner architecture

The first public route is not `/plan?lat=...`. The application service accepts a product intent and then validates the fields required for that intent.

```python
class JourneyIntent(str, Enum):
    LOOP_FROM_HERE = "loop_from_here"
    NATURE_ON_THE_WAY = "nature_on_the_way"
    FIND_A_SPECIES = "find_a_species"
    SURPRISE_ME = "surprise_me"
```

The MVP enables `LOOP_FROM_HERE`. Unsupported intents return a product-state response, not a partially functioning form.

The planner workflow is modeled as a server-side state machine or explicit sequence of forms:

```text
intent → origin → budget/preferences → planning → route menu → route detail
```

Each transition is independently testable and usable without JavaScript. HTMX improves the transition but does not own the business state.

---

# Local-first quality workflow

The repository should provide one documented command that runs the complete local gate:

```bash
just check
```

Suggested implementation:

```text
format check
lint
static type check
unit tests
contract tests
deterministic route smoke test
data manifest verification
media license/attribution verification
```

A release candidate adds browser smoke tests and manual route/media checks. No hosted automation platform is assumed by the architecture.
