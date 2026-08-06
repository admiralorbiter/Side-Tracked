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

## Sprint 1: Domain contracts

### Goal

Freeze the first stable contracts before building screens around experimental objects.

### Deliverables

- `TaxonRef` and canonical taxon ID;
- `Coordinate` and `SpatialCellId`;
- named `EnvironmentalSchema` and `EnvironmentalVector`;
- observation event and species outcome models;
- provenance types;
- `JourneyIntent`;
- `LoopRequest`;
- `RouteOption`, `RouteSegment`, and `RouteStopAction`;
- `MediaAsset`, `FieldCue`, and `RouteFieldPack`;
- typed domain errors.

### Exit gate

- common and scientific names resolve to one key;
- recent occurrences cannot be represented as complete checklists;
- missing coordinates cannot default to zero;
- feature schemas compare names and units;
- media assets cannot exist without source/license/creator/attribution;
- route and media domain objects are immutable.

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

## Sprint 6: Frozen regional route package

### Goal

Create a deterministic Kansas City package independent of live API variability.

### Deliverables

- candidate entrances/locations;
- candidate cell IDs;
- access and safety status;
- named environmental vectors;
- deterministic provisional species surfaces;
- taxonomy version;
- route graph version;
- data/model/media manifests;
- verification CLI.

### Exit gate

- same request and manifests produce the same result;
- no random ecological values at request time;
- all candidates have provenance;
- sensitive and restricted candidates are filtered;
- package verifies offline.

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

## Sprint 10: Media-complete field pack

### Goal

Expand the curated media pack and make the field guide feel complete.

### Deliverables

- 25–50 supported Kansas City species;
- primary image per species when available;
- song/call clip per supported species when available;
- field mark, vocalization description, look/listen location, confusion species, and ethics note;
- beginner and advanced variants;
- route-specific pack selection;
- low-bandwidth and missing-media states.

### Exit gate

- media and cue coverage reported in manifest;
- no species card silently lacks attribution;
- field pack is not overwhelming in usability review;
- audio and image accessibility checks pass.

## Sprint 11: In-route and after-route experience

### Goal

Support the actual walk, not only planning.

### Deliverables

- current segment view;
- route progress;
- quiet mode;
- tap-to-play cues;
- no overlapping audio;
- closure/access report;
- completion/abandonment recap;
- seen/heard/unsure feedback;
- actual duration;
- field-pack helpfulness prompt.

### Exit gate

- in-route screen works one-handed on a small screen;
- route remains usable with audio disabled;
- completion and failure outcomes are distinct;
- no continuous background location retention beyond the active need.

---

# Phase 4 — Stronger ecological evidence

## Sprint 12: Source-normalized evidence

### Goal

Build a clean evidence pipeline while keeping source roles separate.

### Deliverables

- canonical taxonomy crosswalk;
- GBIF presence-only ingestion;
- iNaturalist presence-only ingestion with media licenses separate;
- eBird recent occurrence ingestion as presence-only;
- event date and cyclic week parsing;
- coordinate-to-grid mapping;
- duplicate/provider-lineage handling;
- source provenance.

### Exit gate

- no occurrence endpoint generates non-detections;
- common/scientific names use one taxon key;
- dates are preserved;
- cell assignment depends on geography, not list order;
- evidence status is not confused with prediction status.

## Sprint 13: EBD/SED complete-checklist pipeline

### Goal

Create the first true effort-aware dataset.

### Deliverables

- named-column parsers;
- sampling-event and detection tables;
- complete-checklist filtering;
- shared-checklist handling;
- effort bounds;
- focal-species zero filling;
- release manifest;
- restricted raw-data boundary.

### Exit gate

- event counts reconcile;
- zeros exist only for eligible complete checklists;
- raw restricted files are not redistributed;
- transformations are reproducible.

## Sprint 14: First calibrated focal species

### Goal

Replace one provisional score with one validated encounter model.

### Deliverables

- frozen species;
- training feature schema;
- spatial/temporal holdout;
- calibration evaluation;
- model artifact and card;
- uncertainty surface;
- app adapter;
- relative/probability language switch based on model status.

### Exit gate

- held-out Brier/log-loss/calibration reported;
- training and evaluation leakage checks pass;
- app clearly identifies empirical versus provisional outputs;
- fallback remains available.

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
