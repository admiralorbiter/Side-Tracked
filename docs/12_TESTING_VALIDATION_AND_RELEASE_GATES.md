# Testing, Validation, and Release Gates

## Purpose

Sidetrack combines routing, ecological models, addresses, media, and field guidance. A page can render successfully while still being scientifically wrong, geographically wrong, inaccessible, or legally unusable. Testing therefore covers more than code execution.

The project uses a **local-first quality workflow**. One command should run the standard gate:

```bash
just check
```

No hosted automation service is required by this plan.

---

# 1. Local command set

```bash
just format
just lint
just typecheck
just test
just smoke
just data-verify
just media-verify
just check
just release-candidate
```

## `just check`

Runs:

1. formatting check;
2. lint;
3. static type check;
4. unit tests;
5. contract tests;
6. deterministic route smoke tests;
7. database migration test;
8. data-manifest validation;
9. media-manifest validation.

## `just release-candidate`

Adds:

- browser workflow smoke tests;
- accessibility checklist;
- route-provider integration checks;
- visual/manual route review;
- privacy/log inspection;
- media playback and attribution review;
- frozen artifact checksums.

---

# 2. Test layers

## Unit tests

Cover:

- domain validation;
- canonical taxonomy;
- cyclic weeks;
- evidence-type rules;
- environmental schema compatibility;
- route time decomposition;
- opportunity/reward functions;
- license allowlist;
- attribution rendering;
- privacy redaction;
- sensitive-species suppression.

## Contract tests

Every infrastructure adapter has fixture-based contract tests:

- geocoder;
- routing provider;
- environmental provider;
- GBIF/iNaturalist/eBird adapters;
- media providers;
- artifact repositories.

Fixtures are frozen, small, and legally shareable.

## Integration tests

Cover:

- intent → origin → budget → route menu;
- route selection → field pack;
- route detail → timeline/map agreement;
- media selection → attribution;
- data/model/media provenance summary;
- SQLite migrations and repository queries;
- route feedback persistence.

## Browser workflow tests

Required MVP flows:

1. loop from known public place;
2. address failure and map-pin recovery;
3. current-location permission denial;
4. one-route-only result;
5. route provider unavailable;
6. image missing;
7. audio missing;
8. quiet mode;
9. no-JavaScript form flow;
10. after-route feedback.

## Scientific validation tests

- no presence-only record becomes a non-detection;
- complete-checklist coverage counts unique eligible events;
- evidence dates and weeks are preserved;
- species IDs normalize across sources;
- geographic cell assignment is invariant to record order;
- uncertainty is not substituted for encounter probability;
- simulated data cannot produce an empirical status;
- model calibration controls probability wording;
- train/evaluation data remain separated.

## Routing validation

- route returns to origin;
- matrix and geometry provider/version match;
- declared duration reconciles with provider and buffers;
- route stays within budget;
- route option names match objectives;
- options are materially distinct or omitted;
- restricted candidates excluded;
- route segments cover geometry without gaps or inversions.

## Media validation

- asset has creator, source, ID, license, and attribution;
- license appears in allowlist;
- cached checksum matches;
- revoked asset not selected;
- audio duration and MIME type valid;
- no autoplay;
- one clip at a time;
- alt text and sound description present;
- media taxon matches card taxon;
- missing media has a useful fallback.

---

# 3. Deterministic golden fixtures

Maintain a small frozen Kansas City package with:

- 10–20 candidate locations;
- one routing matrix and geometry fixture;
- 10–15 supported taxa;
- a fixed environmental schema;
- a provisional ecological surface;
- a media manifest;
- access/safety states;
- known route requests and expected invariants.

Do not assert an exact route sequence unless the sequence is part of the contract. Prefer invariants:

- within budget;
- returns to origin;
- includes high-reward site when feasible;
- avoids restricted site;
- route names/objectives behave correctly;
- field pack contains relevant taxa;
- result reproducible for manifest version.

---

# 4. Property and metamorphic tests

Useful properties:

- increasing a time budget cannot make all previous feasible routes infeasible;
- changing candidate list order does not change scores;
- raising one site's reward can change selection in the expected direction;
- disabling media does not change route geometry;
- changing a media license does not change ecological predictions;
- a species evidence record for another taxon does not increase target-species coverage;
- week 52 and week 1 are temporally adjacent;
- route total equals travel + observation + access + return + wait;
- raw address never appears in persisted request rows.

---

# 5. UX and accessibility validation

## Manual first-use script

Ask a reviewer to:

1. describe what Sidetrack does from the home screen;
2. create a 45-minute loop;
3. explain the difference between Easy, Birdy, and Weird;
4. find a photo and play a call;
5. identify where along the route a species is relevant;
6. locate limitations/provenance;
7. enable quiet mode;
8. report a blocked path.

Record confusion, not just success/failure.

## Accessibility checks

- keyboard-only flow;
- screen reader labels;
- semantic heading order;
- focus after HTMX swaps;
- image alt text;
- audio controls;
- sound descriptions;
- no autoplay;
- reduced motion;
- contrast;
- large targets;
- route usable without map;
- no color-only status.

---

# 6. Data validation

Each data package verifies:

- source and release;
- checksum;
- schema;
- coordinate reference system;
- geographic bounds;
- dates and temporal coverage;
- taxonomy version;
- duplicate rules;
- missingness summary;
- restricted-data handling;
- derivation steps;
- intended analytical role.

A source is rejected when its analytical role is ambiguous.

---

# 7. Model validation

Before a model can display probabilities:

- held-out evaluation exists;
- spatial/temporal leakage is considered;
- Brier score and log loss reported;
- calibration curve reported;
- baseline comparison included;
- model card completed;
- supported taxa/region/time documented;
- uncertainty method documented;
- out-of-domain behavior tested;
- fallback behavior defined.

Otherwise, use relative score/index language.

---

# 8. Privacy and security checks

- raw addresses absent from database;
- raw addresses absent from ordinary logs;
- location permission optional;
- session expiration works;
- share links contain opaque IDs;
- debug pages disabled outside development;
- database query parameters bound;
- media URLs escaped and validated;
- file uploads disabled or isolated until designed;
- sensitive species generalized;
- error messages reveal no secrets or paths.

---

# 9. Release gates

## Foundation gate

- Flask shell works;
- local quality command passes;
- domain contracts validated;
- documentation current;
- no experiment imports in web layer.

## UX prototype gate

- complete loop workflow renders;
- all states present;
- route names understandable;
- field pack placement tested;
- no dead controls.

## Media gate

- curated pack passes verification;
- attribution visible;
- audio accessible/user-controlled;
- fallback states work;
- media manifest frozen.

## Routing gate

- provider consistency;
- return and budget validation;
- no misleading fallback;
- route timeline reconciles.

## MVP gate

- several known origins manually reviewed;
- Easy/Birdy/Weird behavior truthful;
- route detail and field pack complete;
- privacy checks pass;
- provenance complete;
- no unsupported probability claims;
- release manifests frozen;
- known limitations documented.

---

# 10. Defect severity

## Blocker

- unsafe/restricted route included;
- raw address retained unexpectedly;
- sensitive species exposed;
- unlicensed media displayed;
- route does not return or exceeds budget;
- simulated output labeled empirical;
- recent occurrence treated as complete checklist.

## High

- wrong taxon media;
- route names do not match objectives;
- map and timeline disagree;
- inaccessible audio control;
- attribution missing;
- provider fallback mislabeled.

## Medium

- missing optional media;
- unclear explanation;
- noncritical visual issue;
- stale optional layer.

## Low

- copy polish;
- minor spacing;
- nonblocking editorial improvement.
