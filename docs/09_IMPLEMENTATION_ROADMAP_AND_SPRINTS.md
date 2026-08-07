# Implementation Roadmap and Sprints

## Development approach

Sidetrack moves slowly through large, coherent pieces. A sprint is defined by a testable artifact and an exit gate, not a fixed number of days.

Rules:

1. Product truth comes before feature count.
2. The public app never imports directly from `experiments`.
3. A route must be useful in text without the map.
4. Media licensing and attribution are release requirements.
5. No unsupported probability language.
6. Every sprint ends with documentation and a local release gate.
7. Do not broaden geography, travel modes, or taxa until the current slice works.
8. Use one local quality command; no hosted automation service is assumed.

---

# Phase 0 — Product identity and repository boundary

## Sprint 0: Freeze the product foundation

### Goal

Create the Sidetrack repository/folder and establish the separation between the public product, stable OVON core, and experiments.

### Deliverables

- Sidetrack name and tagline in README and application shell;
- copied final documentation set;
- Flask application factory;
- blueprints for home/planner, routes, species, search lab, and admin;
- base Jinja template and CSS tokens;
- SQLite connection and migration mechanism;
- `ovon_core` package boundary;
- `data/`, `media/`, and `experiments/` directories;
- `just check` local command;
- project configuration and structured logging.

### Exit gate

- application starts locally;
- no Streamlit or experiment imports in the web layer;
- no raw address, secrets, restricted files, or local database committed;
- local check command succeeds;
- product name and language are consistent.

## Sprint 1: Web domain contracts (Sprint 1A)

### Goal

Freeze stable web-facing domain contracts (`Coordinate`, `TaxonRef`, `LoopRequest`, `RouteOption`, `MediaAsset`, `FieldCue`) connecting presentation to core logic. Backend dataset schemas (`ObservationEvent`, `EnvironmentalVector`, `SpatialCellId`) are explicitly deferred to Sprints 5 and 6 when raw dataset files (eBird TSVs, NLCD land cover rasters) are ingested (ADR-017).

### Deliverables

- `TaxonRef` and canonical species ID;
- `Coordinate` and `BoundingBox` (with distance helpers and boundary validation);
- `JourneyIntent` Enum;
- `LoopRequest` (immutable origin, duration, and preferences);
- `RouteOption`, `RouteSegment`, and `RouteStopAction`;
- `MediaAsset` (mandatory licensing/attribution enforcement), `FieldCue`, and `RouteFieldPack`;
- Typed domain errors (`InvalidCoordinateError`, `MissingAttributionError`, etc.).

### Exit gate

- common and scientific names resolve to one canonical key;
- missing coordinates cannot default to zero `(0, 0)`;
- media assets fail validation if attribution/licensing fields are missing;
- route and media domain objects are immutable (`frozen=True`);
- core package imports zero Flask or web presentation code.

---

# Phase 1 — Prove the user workflow before ecological depth

## Sprint 2: Intent-first UI prototype

### Goal

Build the complete public workflow with fake but deterministic route cards before integrating routing complexity.

### Screens

1. **How do you want to get sidetracked?**
2. **Where should we start?**
3. **How long do you want to get sidetracked?**
4. Planning/loading state
5. Easy/Birdy/Weird route comparison
6. Route detail
7. Field pack
8. In-route segment view
9. After-route recap

### Deliverables

- server-rendered flow;
- HTMX progressive enhancement;
- mobile-first layouts;
- keyboard and no-JavaScript path;
- all empty/error/degraded states;
- text-equivalent route timeline;
- placeholder media with real attribution structure;
- usability script for informal review.

### Exit gate

- a first-time user can explain the product without help;
- the first interactive question is intent, not technical configuration;
- no dead future-intent controls;
- route choices and tradeoffs are understandable;
- field pack is visible before map complexity;
- all primary states render locally.

## Sprint 3: Species media foundation

### Goal

Build the photo/audio/field-cue pipeline before the ecological route model depends on it.

### Deliverables

- media provider and repository interfaces;
- media tables and manifest;
- license allowlist ADR;
- Wikimedia Commons adapter for metadata;
- optional iNaturalist open-media adapter;
- xeno-canto metadata adapter or curated import path;
- attribution renderer;
- accessible audio component;
- no-autoplay and one-clip-at-a-time behavior;
- missing-media fallback;
- curated pack for 10–15 common Kansas City birds;
- initial beginner field cues.

### Exit gate

- every shown asset has visible attribution;
- media verification command passes;
- all audio is user-initiated;
- keyboard and quiet mode work;
- a license or missing asset can be disabled without breaking the species card;
- no all-rights-reserved asset is cached without permission.

---

# Phase 2 — One truthful route

## Sprint 4: Routing provider foundation

### Goal

Generate a closed walking loop using the same routing graph for optimization costs and displayed geometry.

### Deliverables

- routing provider contract;
- `OSMnx` + `igraph` spatial graph solver adapter;
- isochrone, matrix, and route requests;
- provider cache;
- route provenance;
- return-to-origin validation;
- route-cost breakdown;
- visible provider failure state.

### Exit gate

- route returns to the origin;
- route fits the declared budget;
- matrix and geometry use the same provider/version;
- straight-line fallback is never displayed as an exact walking route;
- total time reconciles.

## Sprint 5: Origin and privacy handling

### Goal

Accept a starting place without retaining unnecessary personal data.

### Deliverables

- journey-intent form;
- current-location permission flow;
- address geocoder contract;
- map pin;
- known public place selector;
- transient raw-address processing;
- coarse origin cell;
- unsupported-region state;
- geocoder rate/cache policy.

### Exit gate

- raw address absent from database and ordinary logs;
- location denial does not block use;
- invalid address offers map pin;
- origin is validated inside the supported region.

## Sprint 6: Regional pilot package (Kansas City) & National Dataset Architecture

### Goal

Create a deterministic Kansas City regional package as our initial offline verification pilot, using H3 spatial indexing and region-agnostic data pipeline schemas built for National Public Release.

### Deliverables

- candidate entrances/locations indexed by global Coordinate and H3 cell ID;
- candidate cell IDs (`h3_res8:<index>`);
- access and safety status;
- named environmental vectors;
- deterministic provisional species surfaces (Clements / eBird taxonomy);
- taxonomy version;
- route graph version;
- data/model/media manifests;
- verification CLI;
- state-partitioned Parquet dataset pipeline structure (`/data/ebird/year=2026/state=MO/`).

### Exit gate

- same request and manifests produce the same result;
- no random ecological values at request time;
- all candidates have provenance;
- sensitive and restricted candidates are filtered;
- Kansas City package verifies offline, and schema validates against national region bounds.

## Sprint 7: One complete loop

### Goal

Connect the real routing provider to the intent-first workflow and return one reliable loop.

### Deliverables

- loop candidate generation;
- route optimization;
- route geometry;
- route timeline;
- route detail page;
- field pack selected from route/segment context;
- full provenance summary.

### Exit gate

- loop works from several public test origins;
- text timeline and map agree;
- field pack loads only permitted media;
- route total is within budget;
- failure states are truthful.

---

# Phase 3 — The three-route product

## Sprint 8: Easy, Birdy, and Weird route menu

### Goal

Return up to three meaningfully distinct route options.

### Deliverables

- Easy reward policy;
- Birdy reward policy;
- Weird/exploratory reward policy;
- Pareto filtering;
- route diversity rule;
- deterministic tie breaking;
- route comparison cards;
- explanation generator;
- behavior when only one or two meaningful routes exist.

### Exit gate

- route labels match their actual objective;
- Weird disappears when unsupported;
- routes differ materially or the interface says they do not;
- all options use the same travel assumptions and provenance;
- no user-facing lambda slider.

## Sprint 9: Route segmentation and segment ecology

### Goal

Turn geometry into a sequence of ecological experiences.

### Deliverables

- distance/habitat-based segmentation;
- environmental extraction along route edges;
- habitat-transition detection;
- segment field cues;
- map-to-timeline linking;
- segment-level species opportunity list;
- where-to-look/listen guidance.

### Exit gate

- segment order and distances reconcile with route geometry;
- environmental values come from coordinates, not arbitrary nearest candidates;
- each cue belongs to a relevant segment;
- timeline is usable without the map.

## Sprint 10: Media-complete field pack & Taxon Support Registry

### Goal

Curate 25–50 excellent KC species while introducing the national Taxon Support Registry and region/season-aware field cue profiles. Scientific ecological support and media completeness are formally decoupled.

### Deliverables

- 25–50 curated Kansas City species with primary images and audio clips where available;
- `TaxonSupport` record (`taxonomy_known`, `occurrence_data_available`, `effort_model_available`, `calibrated_model_available`, `field_cue_reviewed`, `photo_available`, `audio_available`, `sensitive`);
- `FieldCueProfile` schema (`taxon_id`, `region_scope`, `season_scope`, `audience`, `where_to_look`, `listen_for`, `confusion_taxa`, `source`, `reviewer`, `version`);
- offline candidate → review → approval media pipeline;
- low-bandwidth and missing-media fallback states without breaking species availability.

### Exit gate

- media and cue coverage reported in manifest;
- species without media remain in ecological catalog under `TaxonSupport` state;
- no species card silently lacks attribution;
- audio and image accessibility checks pass.

## Sprint 11: In-route, SQLite route plan persistence, and versioned feedback

### Goal

Persist route plans to SQLite database with explicit `(plan_id, route_id)` scoping, and support the active walk experience with versioned observation feedback.

### Deliverables

- SQLite route plan persistence (`data/route_plans.db`) storing plan creation/expiry, request parameters, route geometries, model and data versions;
- strict 410 Gone response on expired plan access (no silent cross-plan or static fixture fallbacks);
- current segment view, route progress tracking, and quiet mode;
- tap-to-play cues with single-audio playback controller;
- versioned walk feedback capture (seen / heard / unsure / not noticed, route completion, abandonment, actual duration);
- feedback treated as versioned user observation, not automatic scientific truth.

### Exit gate

- in-route screen works one-handed on small mobile displays;
- expired plan URLs return 410/404 without resolving to another user's walk;
- route plans persist across application restarts until expiration;
- completion and failure outcomes are cleanly recorded.

---

# Phase 4 — Stronger ecological evidence & National Backbone

## Sprint 12: Source-normalized evidence

### Goal

Build the full bird taxonomy and evidence pipeline with explicit source roles.

### Deliverables

- Taxon Concept Registry with Sidetrack UUIDs (`concept_id`) crosswalking eBird codes, GBIF keys, and iNaturalist IDs;
- GBIF presence-only ingestion with DOI dataset citations;
- iNaturalist Research Grade presence-only ingestion with deduplication against GBIF;
- eBird recent occurrence API ingestion as presence-only context;
- event date and cyclic week parsing mapped to H3 spatial grid cells.

### Exit gate

- no presence-only endpoint generates synthetic non-detections;
- common/scientific names resolve through concept identifiers;
- evidence lineage and deduplication verified.

## Sprint 13: EBD/SED complete-checklist pipeline

### Goal

Create the effort-aware dataset pipeline for offline derived models.

### Deliverables

- named-column EBD and SED parsers;
- explicit table separation between `observation_event` and `taxon_detection`;
- complete-checklist validation and shared-checklist deduplication;
- on-demand focal species zero-filling from eligible complete checklists;
- restricted raw-data boundary and licensing compliance manifest.

### Exit gate

- event and detection counts reconcile;
- zero-filling occurs strictly on eligible complete checklists;
- raw restricted data remains private and excluded from public redistribution.

## Sprint 13.25: Evidence Truth & Architecture Hardening (Completed)

### Goal

Eliminate implicit scientific fallbacks, fix taxonomy crosswalk collisions, enforce complete-checklist boundaries, parse authentic EBD/SED TSVs, calculate true astronomical solar time, and establish default private discoveries.

### Deliverables

- Fail-closed `validate_non_detection()` in `packages/ovon_core/evidence/boundary.py`;
- Independent Sidetrack concept UUID identity (`sidetrack_concept:<slug>`) with collision checking and slash/subspecies resolution in `packages/ovon_core/taxonomy/concept_registry.py`;
- Complete-checklist zero-filling identity validation, slash candidate masking (`detected=None`), subspecies parent rollup, and single-cell presence collapse in `packages/ovon_core/pipeline/zero_filler.py`;
- Authentic named-column EBD/SED TSV parsers with schema header validation and join in `packages/ovon_core/pipeline/ebd_ingest.py`;
- Protocol-specific distance/area missingness rules and true astronomical solar time sunrise calculation in `packages/ovon_core/pipeline/effort_filter.py`;
- Spatial disk footprint renaming (`possible_extent_cell_ids`, `is_aeqd_buffered=False`) in `packages/ovon_core/spatial/checklist_buffer.py`;
- `SpatialCellId` runtime fix in `packages/ovon_core/spatial/candidate_index.py`;
- Default `PRIVATE_ONLY` discovery records and export coordinate obfuscation in `packages/ovon_core/domain/discovery.py` & `discovery_repository.py`;
- Experimental Sidetrack Survey Mode UI opt-in and idempotent walk session management;
- Typed segment `habitat_type` persistence in `apps/web/app/services/planner_service.py`;
- Read-only `db-verify` task and SHA256 integrity checks in `packages/ovon_core/cli/verify_db.py` & `downloader.py`;
- Multi-source presence normalization scaffold in `packages/ovon_core/evidence/multisource.py`.

### Exit gate

- 88/88 test items pass cleanly across full pytest suite;
- zero-filling fails closed on non-qualifying evidence tiers;
- EBD/SED TSV reader handles column order permutations without column index assumptions;
- read-only `verify_db` and mutating `migrate_db` verify `route_plans.db`, `walk_feedback.db`, and `discovery.db`.

## Sprint 13.5: Environmental Feature Backbone

### Goal

Extract real environmental feature vectors (NLCD land cover canopy, hydrography water edge, USGS 3DEP elevation/slope) along route geometries to replace presentation string label inference with true spatial rasters.

### Deliverables

- Raster ingestion pipeline for NLCD Land Cover (30m) and USGS 3DEP Elevation;
- Vector buffer extraction for hydrography water edges and canopy boundary distance;
- `EnvironmentalFeatureVector` domain model bound to route segments and H3 spatial cells;
- Segments populate real canopy density %, water proximity meters, and slope gradients.

### Exit gate

- segment habitat classification is computed from spatial feature rasters rather than string heuristics;
- feature vector extraction is deterministic and reproducible across spatial holdouts;
- degraded fallback returns clean default vectors when spatial rasters are unmapped.

## Sprint 13.75: Route Evidence Layer

### Goal

Build a privacy-safe, source-aware occurrence evidence layer that answers *"What biodiversity observations have been reported near this route?"* without conflating occurrence reports with model probabilities, precise organism locations, or complete-checklist nondetections.

### Prerequisite

Sprint 13.5 Environmental Feature Backbone is complete enough that route segments have real environmental context rather than presentation-label inference.

### Deliverables

- **Occurrence Domain Models:** `NormalizedOccurrenceEvidence`, `SourceLineage`, `EvidenceLocation` enum (`OBSERVATION_POINT`, `CHECKLIST_LOCATION`, `OBSCURED_PUBLIC_POINT`, `COARSE_REGION`, `UNKNOWN`), `EvidenceVisibility` enum (`EXACT_DISPLAY_ALLOWED`, `UNCERTAINTY_DISPLAY_ONLY`, `COARSE_DISPLAY_ONLY`, `HIDDEN`), `DuplicateCluster`, `RouteEvidenceSummary`, and `SpeciesRouteEvidence`.
- **Provider Adapters:** eBird Recent occurrence adapter, GBIF occurrence adapter, iNaturalist observation adapter, historical EBD/SED evidence repository, and private Sidetrack `DiscoveryRepository` adapter.
- **Taxonomy:** All occurrences resolve through `TaxonConceptRegistry`; unresolved records are quarantined; no external-ID-to-eBird-code guessing.
- **Deduplication:** Lineage-aware iNaturalist->GBIF duplicate detection; provider-specific duplicate IDs; duplicate clusters preserved (`duplicate_cluster_id`, `canonical_occurrence_id`, `source_lineages[]`).
- **Spatial Engine:** Route bounding region + 1 km margin query; local metric CRS projection; exact point-to-LineString metric distance calculation ($d_i$); configurable corridor bands (0–250 m, 250–750 m, 750–1500 m); `coordinateUncertaintyInMeters` propagation.
- **Temporal Engine:** Recent evidence index $E_s^{\text{recent}}(R,t)$; seasonal historical evidence $E_s^{\text{seasonal}}(R,w)$; cyclic-week distance matching ($d_T(w_1, w_2)$).
- **Privacy & Ethics:** `EvidenceVisibilityPolicy`; sensitive taxon suppression; obscured/public/private handling; no precise distance claims from randomized coordinates ("reported in broader area"); no exact-location inference from neighboring records or timestamps.
- **Application Service & Read Models:** `RouteEvidenceService` / `BuildRouteEvidence`; `RouteEvidenceSummary` and `SpeciesRouteEvidence` read models.
- **UI:** "Reports Near This Walk" section; Recent / Seasonal / My Sightings filters; optional map toggle (off by default); non-chasing in-route guidance ("Recent context" card, no Pokémon-style chasing alerts); visible source/date/provenance.
- **Caching & Governance:** Provider-specific semantic cache with TTL; stale-data indicators; `data_rights_manifest.json` updates.

### Exit gate (20 Items)

1. No presence-only occurrence creates a nondetection.
2. Every visible occurrence resolves to a canonical Sidetrack `concept_id`.
3. Every record retains source and source-record lineage.
4. Duplicate iNaturalist-via-GBIF evidence does not count twice.
5. Precise route distance is shown only when source precision supports it.
6. `coordinateUncertaintyInMeters` affects spatial interpretation rather than being discarded.
7. Obscured iNaturalist records never receive precise route-distance claims.
8. Private locations are never displayed.
9. Sensitive species never expose precise points or indirect route clues.
10. eBird coordinates are described as checklist/report locations rather than exact bird positions.
11. Recent observation density is never called probability or abundance.
12. Historical occurrence density is never called absence coverage.
13. Complete-checklist statistics use only eligible effort-qualified checklists.
14. Evidence layers are usable without the map.
15. Evidence map is off by default.
16. Every public evidence item exposes source and date.
17. Provider/data-rights manifests verify.
18. Source failure produces a truthful degraded state rather than an empty "nothing here" interpretation.
19. Same frozen local evidence inputs produce deterministic route summaries.
20. Tests prove all privacy/sensitive branches.

### Required Degraded States

- **No recent records:** *"No qualifying recent public reports were found near this route. That does not mean these species are absent."*
- **Provider unavailable:** *"Recent eBird reports could not be loaded. Habitat and historical evidence are still available."*
- **Only obscured evidence:** *"Public reports exist in the broader area, but their locations are intentionally generalized."*
- **Insufficient historical effort:** *"There are too few comparable complete checklists to summarize historical detection rates reliably."*
- **Sensitive evidence:** Silently omit location detail with generic note: *"Some evidence may be withheld or generalized to protect sensitive wildlife."*


## Sprint 14: First calibrated focal species & spatial holdouts

### Goal

Train and evaluate the first calibrated focal species model across multiple spatial holdouts to ensure models generalize beyond Kansas City.

### Deliverables

- single calibrated species model trained on complete-checklist effort data;
- spatial and temporal holdout evaluation matrix;
- empirical encounter probability vs provisional relative score language switch;
- model manifest and reproducibility card.

### Exit gate

- spatial holdout calibration metrics (Brier score, log-loss) reported;
- zero training/evaluation spatial leakage verified;
- fallback to provisional score surface remains seamless.

## National Bird Backbone Milestone (Post-Sprint 14)

### Goal

Establish a unified national backbone ensuring adding a new geographic region (e.g. Denver, St. Louis, Atlanta) requires only data/model coverage additions, not code rewrites.

### Deliverables

- full national taxonomy concept registry;
- national evidence ingestion contracts;
- environmental feature coverage (NLCD, USGS 3DEP, Hydrography);
- `CandidateTaxaIndex(coarse_cell, week)` serving lookup;
- model availability registry;
- single repeatable `train_species_model` CLI command.

---

# Phase 5 — Nature on the way and richer modes

## Sprint 15: Point-to-point baseline

### Goal

Plan a normal route between origin and destination.

### Deliverables

- point-to-point intent flow;
- departure time;
- baseline fastest route;
- segment field pack;
- privacy treatment for both endpoints.

## Sprint 16: Detour frontier

### Goal

Show how ecological value changes with added travel time.

### Deliverables

- 0/5/15/30 minute detour budgets;
- frontier and knee detection;
- route comparison;
- “what the detour adds” explanation;
- reproducible reward policy.

## Sprint 17: Species Search Lab productization

### Goal

Turn research surfaces into a responsible user flow.

### Deliverables

- likely encounter;
- under-documented;
- uncertainty;
- hard-to-detect;
- habitat analog;
- source evidence panel;
- sensitive-species policies;
- no promise language.

---

# Phase 6 — Comfort, research, and expansion

## Sprint 18: Accessibility and comfort

- slope, surface, steps, benches, restrooms, shade, and unknown states;
- comfort route option;
- field verification workflow.

## Sprint 19: Field Lab minimum

- study definition;
- route assignment;
- protocol;
- completion and failure logging;
- export.

## Sprint 20: Preference learning

- route pair choices;
- learned preferences;
- explanation and reset;
- no manipulative engagement objective.

## Sprint 21: Transit and car-free access

- GTFS ingestion;
- multimodal route provider;
- transit-plus-walk field pack;
- accessibility status.

## Sprint 22: Multi-taxon contract

- generic taxon and media interfaces;
- one pilot pack such as pollinators or amphibians;
- taxon-specific season/detectability rules.

---

# Branching and experiment strategy

Stable product work lives in product branches or small coherent changes. Experiments live under `experiments/` and may depend on `ovon_core`.

Suggested experimental branches:

```text
experiment/exact-route-duration
experiment/limited-adaptivity
experiment/platform-disagreement
experiment/radar-triggered-routing
experiment/field-pack-media-dosage
experiment/segment-cue-timing
```

An experiment graduates only after:

- a clear hypothesis;
- reproducible inputs;
- evaluation against a baseline;
- documented limitations;
- stable contract;
- product decision/ADR.

---

# Sprint review checklist

- [ ] Artifact is demonstrable locally.
- [ ] Exit gate is satisfied or exceptions are documented.
- [ ] Local `just check` passes.
- [ ] Data/model/media manifests verify.
- [ ] UI states include error and degraded paths.
- [ ] Probability and provenance language are correct.
- [ ] Privacy and sensitive-species behavior are reviewed.
- [ ] Media attribution and accessibility are complete.
- [ ] Relevant docs and ADRs are updated.
- [ ] Next sprint has not absorbed unresolved work from this one.
