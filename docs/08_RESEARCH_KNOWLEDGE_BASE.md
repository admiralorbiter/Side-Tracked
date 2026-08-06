# Research Knowledge Base

## Purpose

Sidetrack sits at the intersection of ecology, routing, citizen science, human-computer interaction, recommendation systems, environmental exposure, and operations research. This document summarizes the research ideas that should shape product and experiment design.

---

# 1. Adaptive citizen-science sampling

Citizen-science data are spatially and temporally uneven because volunteers choose where and when to observe. Adaptive sampling directs a subset of effort toward informative locations.

Mondain-Monval et al. (2024) simulated adaptive citizen-science sampling and found that model-based strategies improved species-distribution model performance, with meaningful gains even at low uptake. This supports a crucial Sidetrack hypothesis:

> Small, feasible changes to journeys people already take may improve ecological coverage without requiring dedicated expeditions.

Product implication:

- scientific-value routes should remain optional;
- a small fraction of users can matter;
- completion and uptake are part of the objective;
- “least sampled” alone is a weak baseline compared with model-informed policies.

---

# 2. Informative path planning

Informative path planning studies routes that gather useful information under travel constraints. Most literature concerns robots, but the mathematical structure applies to human observers.

Transferable concepts:

- reward for visiting locations;
- diminishing returns;
- submodular coverage;
- travel budgets;
- adaptive replanning;
- uncertainty maps;
- route versus point selection;
- multiple sensing modes.

Human differences:

- users may decline routes;
- safety, comfort, and accessibility are hard constraints;
- observers have variable skill;
- travel has independent personal value;
- explanations and trust influence completion;
- a route can be scientifically good but experientially poor.

Sidetrack’s contribution is therefore not a direct copy of robotic IPP. It is **human-feasible ecological path planning**.

---

# 3. Limited adaptivity

Tan, Ghuge, and Nagarajan study informative path planning with a limited number of adaptive rounds. Their results support testing whether one or two replans capture much of the value of continuous replanning.

Sidetrack application:

- plan route at start;
- optionally update after midpoint evidence or a closure;
- avoid interrupting the observer at every stop.

Research question:

> How much ecological or discovery value is retained by one midpoint replan compared with full adaptivity?

---

# 4. Exposure-optimized routing

Green Paths demonstrates that route costs can include greenery, traffic noise, and air quality rather than distance alone. Environmental impedance can be assigned to network edges and included in shortest-path algorithms.

Sidetrack extends this:

- environmental exposure is partly a benefit: greenery, water, habitat;
- partly a cost: heat, noise, air pollution, unsafe roads;
- route edges themselves have ecological value.

Research question:

> Can a route simultaneously improve biodiversity opportunity and human environmental exposure without excessive detour?

---

# 5. Preference learning and route menus

Learning Submodular Objectives for Team Environmental Monitoring studies learning subjective reward functions from user comparisons among solutions.

Sidetrack application:

- show two or three route alternatives;
- observe which tradeoff a user selects;
- learn preferences for time, shade, novelty, species, accessibility, and scientific value.

Guardrail:

- learned preferences cannot override explicit accessibility or safety constraints.

Research question:

> Does a small route menu improve realized ecological value by increasing acceptance compared with one assigned “optimal” route?

---

# 6. Serendipity and recommendation

Conventional recommendation emphasizes relevance. Nature discovery also benefits from productive surprise.

A good serendipity target is:

- plausible enough to encounter;
- unfamiliar enough to be interesting;
- learnable enough to recognize;
- not so rare that the route becomes misleading or harmful.

Possible score:

\[
Serendipity(s,R,u)
=
P_s(R)
[1-Familiarity(s,u)]
Learnability(s,u).
\]

Research question:

> Which balance of familiar and novel species produces the most satisfying and educational route?

---

# 7. Citizen-science motivation and choice architecture

Volunteers may be motivated by:

- learning;
- place attachment;
- contribution;
- community;
- species interest;
- enjoyment;
- convenience.

Recommendations must not assume scientific contribution is the only value. Route explanations can vary:

- “See more habitat variety”
- “Help fill an observation gap”
- “Learn three common songs”
- “Take a shaded route”
- “Search for spring migrants”

Study design should record route acceptance and non-completion, not only completed observations.

---

# 8. Observation-process modeling

Different sources represent different processes:

- complete checklists;
- structured point counts;
- presence-only records;
- photo-supported records;
- acoustic detections.

Naive pooling can create false non-detections or overconfidence. Integrated models may share a latent ecological process while retaining source-specific likelihoods and sampling bias.

Research direction:

- eBird checklist model;
- GBIF/iNaturalist point-process component;
- shared habitat/seasonal surface;
- source-specific bias;
- platform disagreement.

---

# 9. Detectability and survey duration

Longer surveys increase detection but with diminishing returns. The rate differs by species, observer, habitat, and protocol.

Field design:

- record first detection in intervals;
- fit time-to-detection or removal models;
- estimate species-specific curves;
- compare fixed and variable-duration routes.

Research question:

> When should a volunteer visit one more site versus spend five more minutes at the current site?

---

# 10. Occupancy versus encounter rate

Repeated structured visits can support occupancy models that separate presence and detection. Semi-structured eBird data more naturally support standardized encounter-rate modeling after effort control.

Product language should distinguish:

- suitability;
- relative presence;
- standardized encounter;
- occupancy;
- probability of user detection.

Do not use occupancy as a generic synonym for any map score.

---

# 11. Human feasibility frontier

Start with an unconstrained ecological optimum and add constraints:

\[
U_{unconstrained}
\rightarrow
U_{route}
\rightarrow
U_{return}
\rightarrow
U_{public}
\rightarrow
U_{access}
\rightarrow
U_{observer}
\rightarrow
U_{completed}.
\]

Measure the price of each constraint:

\[
Price(c)
=
1-\frac{U_c}{U_{unconstrained}}.
\]

Research questions:

- How much scientific value is lost by route connectivity?
- What is the cost of car-free participation?
- Does offering route choices recover accessibility costs?
- Which constraints produce smooth tradeoffs versus sharp infeasibility?

---

# 12. Ecological access equity

Define maximum reachable nature value from origin zone \(z\) under budget \(B\):

\[
A_z(B)
=
\max_{R\in\mathcal R(z,B)} U(R).
\]

Compare:

- walking;
- driving;
- transit;
- wheelchair-accessible;
- low-walking routes.

Research questions:

- Which neighborhoods have low access to varied nature?
- Is low access caused by habitat, routing barriers, transit, or missing data?
- Can public monitoring routes also identify investment opportunities?

Avoid interpreting missing accessibility metadata as true inaccessibility.

---

# 13. Route resilience

Routes and monitoring networks can fail through:

- closures;
- flooding;
- heat;
- transit disruption;
- observer attrition;
- loss of major hotspots.

A multilayer network connects observers, routes, sites, weeks, and species. Resilience analysis can identify:

- critical sites;
- substitute routes;
- minimum monitoring backbone;
- vulnerable seasons;
- overdependence on a few volunteers.

---

# 14. Migration-responsive routes

BirdCast radar products describe nocturnal migration intensity. A future route can respond to an overnight migration pulse:

\[
U_t(R)
=
U_{base}(R)
+
\gamma M_t StopoverSuitability(R).
\]

Research questions:

- Do radar-triggered routes increase migrant detections?
- Which urban canopy or riparian areas matter after migration nights?
- Does dynamic routing improve arrival-date estimation?
- How much spatial precision can radar legitimately support?

Do not infer neighborhood-level species identity directly from radar.

---

# 15. Platform disagreement

Estimate separate surfaces for:

- complete-checklist model;
- GBIF presence-only;
- iNaturalist;
- external range/abundance prior.

Disagreement:

\[
D_{s,i,t}
=
Var_p[\hat p_{s,i,t}^{(p)}].
\]

High disagreement may reflect:

- habitat change;
- platform bias;
- identification difficulty;
- range edge;
- sparse data;
- source duplication.

This can become both a research target and a transparent uncertainty layer.

---

# 16. Edge-valued ecology

Traditional sampling selects points. A nature route also traverses corridors.

Potential edge features:

- canopy continuity;
- riparian adjacency;
- habitat transitions;
- imperviousness;
- building edges;
- streetlights;
- traffic;
- noise;
- heat;
- elevation.

Research question:

> Does valuing route edges identify meaningful urban ecological corridors missed by park-centered point selection?

---

# 17. Community-level modeling

Species-by-species models can be sparse. Latent factors or joint species models can represent assemblages:

- wetland birds;
- canopy insectivores;
- urban generalists;
- migrants;
- open-country species.

Benefits:

- information sharing;
- more stable multi-species rewards;
- route bundles;
- ecological interpretation.

Risk:

- a latent community score may be less intuitive than species-level predictions.

---

# 18. Product research questions

1. Does the detour frontier change route choice?
2. Do explanations improve trust and completion?
3. Are users more satisfied with route menus?
4. Does a segment timeline improve species recall?
5. What level of uncertainty detail is understandable?
6. Do beginner and advanced users need different route objectives?
7. Does personal novelty improve learning without encouraging chasing?
8. Do heat-safe routes increase completion?
9. Does one midpoint replan add value or annoyance?
10. Can meaningful scientific data be collected on journeys users already planned?

---

# 19. Research design principles

- preregister primary outcomes for formal studies;
- log routes offered, not only routes chosen;
- preserve assignment probabilities;
- separate model-selection data from evaluation data;
- use spatial and temporal holdouts;
- report uncertainty and failures;
- compare against operationally equivalent baselines;
- evaluate realized value, not only theoretical utility;
- protect participant location privacy;
- avoid sensitive-species exposure;
- distinguish simulation from field evidence.

---

# 20. Near-term publishable branches

### Computational

Joint route and observation-duration optimization with exact small-instance benchmarks.

### Ecological methods

Source-aware species opportunity surfaces from complete checklists and presence-only records.

### Human-centered

Route menu versus single recommendation under completion and satisfaction outcomes.

### Transportation equity

The price of car-free and accessible biodiversity participation.

### Dynamic ecology

Migration-triggered route recommendations using radar and habitat.

These branches should remain experiments until their contracts and evidence are stable enough for product use.

---

# 21. Field-guide media and perceptual learning

Sidetrack is not primarily an identification model. Its educational contribution is **attention guidance**: helping a person know where to look, what to listen for, and which features matter before and during a route.

Useful research questions include:

- Does seeing one representative photo before a walk improve later recognition?
- Does a short call/song example increase auditory detections or only confidence?
- Are segment-specific cues more useful than one route-wide species list?
- How many focal species can a beginner absorb before the field pack becomes overwhelming?
- Do look-alike comparisons reduce false positive identifications?
- Is “listen for this pattern” more useful than phonetic mnemonics?
- Does media use change route choice or route completion?

The first product should treat these as testable design hypotheses, not assume that more media always improves learning.

## Media dosage experiment

Compare:

1. names only;
2. image plus one field mark;
3. image, field mark, and audio;
4. full card with look-alikes and habitat cue.

Outcomes:

- recall;
- correct identification in a controlled quiz;
- route completion;
- perceived overload;
- field-pack helpfulness;
- audio playback rate.

## Segment cue experiment

Compare a route-wide field pack with cues delivered at habitat transitions. Hypothesis: segment-specific cues improve relevance and reduce cognitive load, but too many prompts reduce enjoyment.

# 22. Human-centered route choice

The route menu itself is a behavioral research surface. The names **Easy**, **Birdy**, and **Weird** communicate intent more quickly than mathematical metrics, but they also shape expectations.

Questions:

- Do playful route names increase engagement without reducing trust?
- Does the Weird route attract exploration or create an expectation of rare species?
- Which explanation format best communicates a detour tradeoff?
- Are people more willing to take a longer route when the additional habitat is shown visually?
- Does an image of a plausible species bias route choice more strongly than a numeric score?

The product should separate route explanation from persuasion. The goal is informed choice, not maximizing time in the app.

# 23. Audio ethics and field behavior

Playing recordings in the app for learning is different from broadcasting playback to attract wildlife. The interface should explicitly discourage using speaker playback to provoke territorial or breeding responses, especially around sensitive species and nesting periods.

Research and product design should distinguish:

- headphones or quiet personal listening;
- pre-trip learning;
- low-volume reference listening;
- broadcasting in habitat;
- research playback under an approved protocol.

The consumer app should not encourage broadcast playback in the field.
