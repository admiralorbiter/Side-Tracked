# Experiment and Innovation Backlog

## Purpose

This is a research backlog, not a product commitment. Experiments live under `experiments/`, use stable core contracts, and graduate only after evaluation and an explicit product decision.

Each experiment should have:

- a question;
- falsifiable hypothesis;
- baseline;
- data requirements;
- evaluation method;
- risks and ethics;
- compute estimate;
- expected reusable artifact;
- stop condition.

Use `templates/EXPERIMENT_TEMPLATE.md`.

---

# Near-term computational experiments

## E-01 — Exact versus greedy loop optimization

**Question:** How far is the greedy route/duration heuristic from the exact optimum on small instances?

Compare:

- exact CP-SAT/MIP;
- greedy insertion;
- greedy plus local search;
- adaptive large-neighborhood search.

Vary:

- candidate count;
- route budget;
- clustering;
- habitat redundancy;
- duration choices;
- route objective.

Outputs:

- optimality gap;
- runtime;
- failure cases;
- recommendation for when Rust or a stronger heuristic is worthwhile.

## E-02 — Edge-valued versus stop-valued routes

**Question:** How much ecological value is missed when only stops receive reward?

Add route-segment intensity and habitat-transition reward. Evaluate whether routes change and whether field users notice more species along moving segments.

## E-03 — Detour frontier and knee detection

**Question:** Which algorithm best identifies the useful point where additional detour time has diminishing ecological returns?

Compare curvature, marginal-gain thresholds, and user-chosen route behavior.

## E-04 — Route menu diversity

**Question:** How different should Easy, Birdy, and Weird be before a route menu is meaningful?

Study route overlap, habitat overlap, opportunity difference, and explanation comprehension.

## E-05 — Robust route duration

Model travel duration uncertainty and compare expected-time routes with chance-constrained or CVaR routes.

---

# Ecological and evidence experiments

## E-06 — Habitat analog search

Train a habitat signature from known occurrences and evaluate held-out occurrence ranking. Compare:

- nearest-neighbor kernel;
- one-class model;
- presence-background classifier;
- community-level embedding.

## E-07 — Expected richness debt

Replace the demonstration heuristic with an effort-aware model of expected versus observed richness. Evaluate through checklist rarefaction or matched-habitat references.

## E-08 — Platform disagreement atlas

Compare eBird, GBIF, and iNaturalist surfaces by species, week, and habitat. Test whether disagreement predicts future error or data gaps.

## E-09 — Source-aware integrated distribution model

Separate complete-checklist likelihood from presence-only point processes and test whether integrated models improve spatial holdouts.

## E-10 — Credible absence

Estimate when repeated eligible non-detections create meaningful evidence of absence versus simple lack of effort.

## E-11 — Community matrix completion

Predict missing species-cell combinations using low-rank/community factors with spatial and environmental regularization.

## E-12 — Time-to-detection and variable duration

Estimate species/observer/habitat-specific detection curves from interval data. Test when variable-duration routes outperform fixed counts.

---

# Human-centered and UI experiments

## E-13 — Intent-first versus address-first home

Compare comprehension, completion, and configuration burden.

Hypothesis: intent-first improves understanding and reduces the feeling of entering a complex planning tool.

## E-14 — Route naming

Compare:

- Easy/Birdy/Weird;
- Shortest/Nature/Discovery;
- metric-only labels.

Measure comprehension, trust, choice, and expectation mismatch.

## E-15 — Field-pack media dosage

Conditions:

1. text only;
2. image plus one field mark;
3. image plus audio;
4. full card.

Measure recall, overload, playback, and route enjoyment.

## E-16 — Segment cue timing

Compare pre-trip-only cues with segment-triggered cues and one midpoint summary.

## E-17 — Audio description styles

Compare mnemonic, acoustic description, spectrogram, and call-type labels for beginner learning.

## E-18 — Route explanation formats

Compare numeric score, plain-language tradeoff, habitat additions, and species examples.

## E-19 — Preference learning

Use pairwise route choices to learn user tradeoffs without asking for many sliders. Evaluate stability, reset, and explanation quality.

---

# Dynamic and environmental experiments

## E-20 — Radar-triggered morning routes

Use BirdCast or NEXRAD migration intensity to adjust morning stopover routes. Compare static and radar-responsive recommendations.

## E-21 — Heat-safe biodiversity routes

Optimize ecological opportunity and thermal exposure using canopy, shade, temperature, or ECOSTRESS/local heat layers.

## E-22 — Weather-aware detectability

Test wind, rain, temperature, and cloud effects on observed encounter rates and route guidance.

## E-23 — Noise-aware listening routes

Use traffic/noise estimates to favor segments where auditory observation is practical.

## E-24 — Night nature routes

Later multi-taxon pack for owls, frogs, moths, and bats with strict safety and timing constraints.

---

# Accessibility and equity experiments

## E-25 — Car-free nature opportunity frontier

Compare walking, driving, transit-plus-walking, and wheelchair-accessible opportunity from neighborhood origins.

## E-26 — Nature access index

Measure maximum reachable ecological opportunity within 15/30/60 minutes by origin zone.

## E-27 — Price of accessibility

Estimate ecological opportunity lost under step-free, slope, surface, and rest constraints, and identify recovery through alternate hubs.

## E-28 — School and older-adult route design

Study burden, cue complexity, rest spacing, and group-safe route selection.

---

# Adaptive and research-operation experiments

## E-29 — Limited adaptivity

Compare static route, one midpoint replan, two replans, and fully adaptive policy.

## E-30 — Completion-aware route menus

Optimize expected realized value using route choice and completion probability rather than theoretical utility alone.

## E-31 — Observation network resilience

Simulate closures, observer loss, weather disruption, and transit failure in a multilayer observer-site-week-species network.

## E-32 — Multiple volunteer coordination

Allocate route portfolios across volunteers with coverage, fairness, and capability constraints.

---

# Multi-taxon experiments

## E-33 — Pollinator route pack

Use flowering plants, temperature, daylight, and habitat.

## E-34 — Amphibians after rain

Use precipitation, wetlands, temperature, time of day, and sound guidance.

## E-35 — Native plant phenology

Use bloom calendars and route-segment habitat.

## E-36 — Fungi after weather events

Use rain, humidity, substrate, canopy, and season.

---

# Route Evidence Experiments

## E-37 — Route evidence distance kernel

**Question:** At what spatial scale do nearby occurrence reports meaningfully predict later route-level detections?  
**Compare:** $100\text{ m}, 250\text{ m}, 500\text{ m}, 1000\text{ m}$ spatial bandwidths $\sigma_0$.  
**Evaluation:** Held-out complete checklists along route corridors.

## E-38 — Recent evidence temporal decay

**Question:** How quickly does the usefulness of recent occurrence evidence decay?  
**Compare:** 3-day, 7-day, 14-day, 30-day temporal decay kernels $\tau$.  
**Evaluation:** Evaluated separately for resident species, migrants, eruptive species, and waterbirds.

## E-39 — Seasonal historical evidence

**Question:** Does cyclic-week weighting outperform calendar-month aggregation?  
**Hypothesis:** Cyclic-week distance $d_T(w_1, w_2)$ better distinguishes rapid spring migration arrivals than monthly counts.

## E-40 — Observation-effort corrected route evidence

**Question:** Does target-group background (TGB) effort normalization mitigate popular-park observer bias?  
**Compare:** Raw species occurrence count versus relative effort ratio $E_s^{\text{relative}}(x) = \frac{\operatorname{KDE}_s(x)}{\operatorname{KDE}_{\text{all records}}(x) + \epsilon}$.

## E-41 — Model–evidence disagreement

**Question:** Does divergence between model prediction and recent reports identify ecological events?  
**Formula:** $D_s(x,t) = z(E_s^{\text{recent}}) - z(P_s^{\text{model}})$.  
**Study:** Whether high disagreement predicts migration pulses, novel habitat colonization, or model miss.

## E-42 — Under-documented route objective

**Question:** Can Sidetrack identify high-opportunity, low-coverage routes for field survey effort?  
**Formula:** $U_{\text{gap}}(R) = \frac{1}{L(R)} \int_R \text{Opportunity}_s(x,t) \, [1 - C(x,t)] \, dl$.

## E-43 — Evidence ribbon visualization

**Question:** Which UI representation minimizes map clutter and species-chasing behavior?  
**Compare:** Raw occurrence points vs clustered points vs corridor heat ribbon vs text-only summaries.

## E-44 — Provider disagreement

**Question:** How do eBird, iNaturalist, and GBIF occurrence surfaces diverge spatially?  
**Metrics:** Rank correlation, spatial overlap, and Jensen-Shannon divergence across urban vs rural strata.

## E-45 — Coordinate uncertainty propagation

**Question:** Does incorporating source uncertainty $u_i$ into $\sigma_i^2 = \sigma_0^2 + u_i^2$ improve spatial reliability?  
**Compare:** Ignoring uncertainty vs hard cutoff vs uncertainty-weighted decay kernels.

## E-46 — Evidence freshness explanation

**Question:** Which provenance text yields the highest user trust without false expectations?  
**Compare:** *"3 reports nearby"* vs *"3 reports in last 7 days"* vs *"3 reports nearby; most recent yesterday; 18 historical May checklists"*.

## E-47 — Evidence-driven route optimization (Field Lab Only)

**Question:** Does routing users toward recent public reports improve encounter rates without causing hotspot crowding?  
**Compare:** Habitat-driven route vs recent-evidence-driven route vs hybrid route.

---

# Graduation gate


An experiment may enter the stable product when:

- results are reproducible;
- baseline comparison exists;
- limitations are documented;
- data rights permit product use;
- privacy/safety/sensitive-species effects are reviewed;
- latency and operational cost are acceptable;
- stable API/domain contracts are defined;
- tests and fallback state exist;
- product value is clearer than added complexity;
- an ADR records the decision.
