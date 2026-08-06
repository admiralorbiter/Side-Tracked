# Migration from OVON

## Purpose

OVON is the research and optimization laboratory that taught the project how to represent routes, evidence, species opportunity, uncertainty, survey duration, and provenance. Sidetrack is the stable product surface.

The migration should extract stable contracts and tested behavior. It should not copy the Streamlit application or move every experiment into the product.

---

# 1. What graduates

Candidates for the stable core:

- canonical species/taxon contracts;
- species-aware evidence model;
- route cost breakdown;
- closed-loop validation;
- opportunity/reward interfaces;
- routing provider interface;
- cyclic week utilities;
- environmental feature schema;
- data/model provenance types;
- QBC/uncertainty utilities;
- route evaluation fixtures;
- source-role guardrails;
- deterministic synthetic benchmark tools.

Each item graduates only after its interface is cleaned of Streamlit and experimental assumptions.

---

# 2. What remains in experiments

- simulated historical replay results;
- arbitrary duration curves;
- provisional phenology curves;
- random geographic encounter surfaces;
- experimental objective functions;
- exact/heuristic benchmark comparisons;
- platform-integration models;
- radar-triggered routing;
- adaptive replanning;
- prototype dashboards;
- exploratory research manuscripts.

Experiments may import the stable core. The public app does not import experiments.

---

# 3. What is retired

Do not migrate:

- dynamic attributes on candidate objects;
- generic existing-observation lists that erase species/source semantics;
- live API calls inside page rendering;
- silent exception handling;
- simulated values labeled as predictions;
- common names as analytical IDs;
- index-based spatial cell assignment;
- route optimization and display using different travel models;
- direct mutation of cached candidate data;
- media URLs without license metadata.

---

# 4. Proposed package extraction

```text
packages/ovon_core/
├── taxonomy/
├── evidence/
├── environmental/
├── ecology/
├── opportunity/
├── routing/
├── media/
├── provenance/
├── evaluation/
└── errors.py
```

The stable core imports no Flask and no Streamlit.

---

# 5. Migration sequence

## Step 1: Contract inventory

For every OVON module, classify:

```text
stable candidate
experiment
UI-specific
data adapter
retire
```

## Step 2: Freeze tests

Before moving logic, create tests for the behavior that must survive:

- route returns to origin;
- cost decomposition reconciles;
- evidence types remain distinct;
- candidate data are not mutated;
- week distance is cyclic;
- uncertainty derives from the correct source;
- opportunity surfaces affect route selection;
- provenance survives serialization.

## Step 3: Extract domain objects

Move domain types first. Do not move application code before their contracts are stable.

## Step 4: Extract pure functions

Move:

- time/distance calculations;
- kernels;
- QBC;
- route feasibility;
- taxonomy normalization;
- evidence aggregation.

## Step 5: Build adapters

Wrap existing OVON providers behind stable interfaces. Adapter output must use canonical domain models.

## Step 6: Build Flask application services

The web layer calls application services, not OVON modules directly.

## Step 7: Keep Streamlit as a lab

The current interface may remain useful for research and diagnostics. It should use the stable core where practical, but it is not the product UI.

---

# 6. Compatibility strategy

Avoid maintaining a long-lived compatibility layer for every old object. Prefer explicit conversion functions at boundaries:

```python
def candidate_site_from_ovon(old: OvonCandidateSite) -> CandidateLocation:
    ...
```

Conversion functions should be temporary and covered by tests.

---

# 7. Data migration

## Taxonomy

- freeze canonical taxonomy;
- build common/scientific/provider crosswalks;
- replace common-name keys.

## Evidence

- split event and species outcome;
- preserve source IDs/dates/coordinates;
- distinguish presence-only and complete checklists;
- map to real spatial cells.

## Environmental data

- replace anonymous arrays with named schemas;
- store source/vintage/method;
- remove L1 normalization for independent variables unless justified.

## Routing

- generate matrix and geometry from one provider/version;
- store route artifact provenance.

## Media

- do not migrate image/audio URLs unless creator/license/source are complete;
- establish a new curated media manifest.

---

# 8. Migration exit gate

Migration foundation is complete when:

- Flask app imports only stable packages;
- experiments run against stable contracts;
- old Streamlit UI remains optional;
- no random ecological values enter public requests;
- canonical taxonomy works across sources;
- route/evidence/media manifests are reproducible;
- local test and verification commands pass;
- migration decisions are documented in ADRs.
