# Sidetrack

> **A Field Guide to Getting Sidetracked.**

Sidetrack is a route-first biodiversity discovery application. It helps someone turn an ordinary walk or trip into a guided nature experience: where to go, what birds may be encountered along the way, where to look, what to listen for, and why a slightly different route may be worth the extra time.

**Project status:** product foundation and architecture planning  
**Initial region:** Greater Kansas City  
**Initial taxon:** birds  
**Initial journey:** walking loops that return to the starting point  
**Product stack:** Flask, Jinja, HTMX, Alpine.js, HTML/CSS, SQLite, Leaflet map client, and Python ecological/routing services (`OSMnx` + `igraph`)  
**Research engine:** OVON  
**Document set version:** 1.1 — August 6, 2026

---

## The product in one sentence

> Sidetrack plans a route and gives you a small, visual, listenable field guide for the living things you may encounter on it.

Most navigation tools ask for the shortest or fastest path. Sidetrack asks a second question:

> What could I notice on the way, and what route gives me the best nature experience for the time, comfort, accessibility, and curiosity I have today?

---

## The first screen

The first interaction is about **intent**, not a blank address field.

### Full product home

**How do you want to get sidetracked?**

1. **Take a loop from here** — start somewhere, walk for a chosen amount of time, and return.
2. **Add nature to a trip** — compare the normal route with small ecological detours.
3. **Find a species** — plan a thoughtful search without promising a sighting.
4. **Surprise me** — favor unfamiliar habitats and plausible discoveries.

### First release

Only **Take a loop from here** needs to be fully active. The other intents may be hidden or clearly labeled as future work. After choosing the loop:

1. **Where should we start?** Current location, address, map pin, or known public place.
2. **How long do you want to get sidetracked?** Default: 45 minutes.
3. **Anything we should know?** Optional comfort and accessibility preferences.
4. **Show me three ways to go.**

The route cards use human names rather than mathematical parameter labels:

- **The Easy One** — shortest, simplest, and lowest burden.
- **The Birdy One** — strongest bird and habitat opportunity for the budget.
- **The Weird One** — the most unusual or serendipitous route that the evidence can support.

“The Weird One” must disappear or be renamed when the data do not support a genuinely different exploratory route.

---

## What the user gets

Each route includes:

- a map and text-equivalent timeline;
- total time, distance, return-to-origin confirmation, and route tradeoffs;
- habitat transitions by segment;
- a short list of likely or interesting species by segment;
- representative bird photographs;
- tap-to-play calls or songs;
- **where to look** and **what to listen for** guidance;
- look-alikes and simple field marks;
- access, comfort, and uncertainty notes;
- clear labels for observed, modeled, provisional, simulated, and unavailable information.

Audio never starts automatically. Media must carry creator, source, license, and attribution information.

---

## Product surfaces

Sidetrack is the public product. OVON remains the replaceable ecological research and optimization engine.

| Surface | Audience | Main job |
|---|---|---|
| **Sidetrack** | walkers, travelers, families, beginning and experienced naturalists | discover nature along real journeys |
| **Species Search Lab** | birders and naturalists | find likely, overlooked, uncertain, or difficult search opportunities |
| **Field Lab** | researchers, schools, and volunteer groups | run structured observation routes and studies |
| **Network Planner** | nonprofits, conservation groups, and cities | design monitoring networks and equitable coverage |

The public application should not look like a research dashboard. Research details are available through progressive disclosure.

---

## First meaningful release

The first release is intentionally narrow:

- Greater Kansas City only;
- birds only;
- walking loops only;
- one starting location;
- 30–90 minute budgets;
- three valid route choices when meaningful alternatives exist;
- route timeline and habitat segments;
- a curated media pack for common focal species;
- one representative image and at least one useful call/song clip per supported species when licensing permits;
- no account required;
- no raw-address retention;
- no public observation submission;
- no exact sensitive-species locations;
- no unsupported probability language.

The first release proves that the route, field guide, and media experience work together. It does not need a nationwide empirical model.

---

## Product principles

1. **The route is the product.** Species cards and maps support a real journey.
2. **Start with curiosity.** Ask how the person wants to get sidetracked before asking for configuration.
3. **Show, then explain.** Photos, sound, habitat clues, and route timelines come before research jargon.
4. **Offer choices, not an oracle.** Three routes with clear tradeoffs are better than one “optimal” answer.
5. **Do not overstate evidence.** A relative score is not a calibrated probability.
6. **No automatic audio.** Playback is initiated and controlled by the user.
7. **Media rights are data.** License and attribution are required fields, not footer cleanup.
8. **Unknown means unknown.** Missing access or accessibility data are never converted into confident claims.
9. **Privacy is the default.** Raw home addresses are transient.
10. **Sensitive species are protected.** The product avoids precise public chasing incentives.
11. **The core remains replaceable.** New models and optimizers plug into stable contracts.
12. **Move slowly through large, testable pieces.** A sprint ends at an exit gate, not on a calendar date.

---

## Recommended technology direction

### Web application

- Flask application factory and blueprints
- Jinja templates
- HTMX for partial-page interactions
- Alpine.js for lightweight client-side UI state (zero build step)
- semantic HTML and CSS
- Leaflet map module for route rendering
- standard HTML audio controls or a small accessible audio component

### Application data

- SQLite for app state, taxonomy, media metadata, route requests, and manifests
- RTree indexes for spatial lookups
- Parquet and GeoTIFF for large derived ecological and environmental data
- filesystem or object storage for permitted cached media and model artifacts

### Ecological and routing core

- Python first (100% native execution, no external Docker services required)
- `OSMnx` + `igraph` for pedestrian matrix, isochrone, open-street-network graph loading, and custom ecological loop routing
- Rust through PyO3 only after profiling finds a stable, meaningful bottleneck

A complete Rust rewrite is not part of the initial plan.

---

## Repository shape

```text
sidetrack/
├── apps/
│   └── web/
│       ├── app/
│       │   ├── blueprints/
│       │   │   ├── planner/
│       │   │   ├── routes/
│       │   │   ├── species/
│       │   │   ├── search_lab/
│       │   │   ├── research/
│       │   │   └── admin/
│       │   ├── templates/
│       │   └── static/
│       └── tests/
├── packages/
│   ├── ovon_core/
│   │   ├── evidence/
│   │   ├── ecology/
│   │   ├── opportunity/
│   │   ├── routing/
│   │   ├── media/
│   │   ├── provenance/
│   │   └── evaluation/
│   └── environmental_data/
├── experiments/
├── data/
│   ├── private/
│   ├── derived/
│   └── public/
├── media/
│   ├── cached/
│   └── manifests/
├── docs/
├── templates/
├── pyproject.toml
├── justfile
└── README.md
```

The web application may depend on `ovon_core`. It must not import directly from `experiments`.

---

## Local development philosophy

The project uses a local-first quality workflow. One command should run formatting, linting, type checks, tests, data-manifest validation, and a deterministic route smoke test:

```bash
just check
```

Additional useful commands:

```bash
just smoke
just data-verify
just media-verify
just release-candidate
```

No hosted automation service is required by this plan.

---

## Documentation map

Read these first:

1. [`docs/00_DOCUMENT_MAP.md`](docs/00_DOCUMENT_MAP.md)
2. [`docs/01_PRODUCT_VISION_AND_SCOPE.md`](docs/01_PRODUCT_VISION_AND_SCOPE.md)
3. [`docs/02_USER_EXPERIENCE_AND_INFORMATION_ARCHITECTURE.md`](docs/02_USER_EXPERIENCE_AND_INFORMATION_ARCHITECTURE.md)
4. [`docs/10_UI_WORKFLOWS_AND_SCREEN_STATES.md`](docs/10_UI_WORKFLOWS_AND_SCREEN_STATES.md)
5. [`docs/11_SPECIES_MEDIA_AND_FIELD_GUIDANCE.md`](docs/11_SPECIES_MEDIA_AND_FIELD_GUIDANCE.md)
6. [`docs/03_FEATURE_CATALOG.md`](docs/03_FEATURE_CATALOG.md)
7. [`docs/04_TECHNICAL_ARCHITECTURE.md`](docs/04_TECHNICAL_ARCHITECTURE.md)
8. [`docs/09_IMPLEMENTATION_ROADMAP_AND_SPRINTS.md`](docs/09_IMPLEMENTATION_ROADMAP_AND_SPRINTS.md)
9. [`docs/19_STARTUP_CHECKLIST.md`](docs/19_STARTUP_CHECKLIST.md)

The remaining documents cover domain models, mathematics, data, research, testing, privacy, migration, decisions, experiments, references, and vocabulary.

---

## Non-goals for the first release

- building a new photo or sound identification model;
- replacing Merlin or eBird;
- a social feed;
- engagement streaks or rare-species leaderboards;
- nationwide coverage;
- native mobile applications;
- continuous location tracking;
- automatic playback of bird sounds;
- automatic observation submission;
- public exact sensitive-species coordinates;
- a complete Rust rewrite;
- unsupported claims of empirical encounter probability.

---

## Product disclaimer

Early versions will combine live occurrence context, curated media, provisional phenology, proxy environmental data, simulated or provisional uncertainty, and incomplete coverage. The interface must state those conditions clearly. A value is called a **probability** only after calibration has been evaluated on held-out observations.

---

## Definition of the first successful milestone

A person can choose **Take a loop from here**, enter or pin a starting location, select 45 minutes, and receive up to three valid closed walking loops.

For each route, they can:

- understand the tradeoff without reading research terminology;
- read a timeline without using the map;
- see representative images for supported species;
- play a bird call or song on demand;
- learn where to look and what to listen for;
- understand the evidence and limitations;
- confirm that the route returns to the start and fits the budget.

The raw address is not retained, media attribution is complete, and the result is deterministic for a frozen data/model/media manifest.
