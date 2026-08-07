# Product Vision and Scope

> **Sidetrack — A Field Guide to Getting Sidetracked.**

## Working product statement

**Sidetrack is an ecological navigation application that helps people discover birds and other living things along routes they already want to travel.**

It combines routing, seasonal biodiversity expectations, environmental context, personal preferences, accessibility constraints, and optional citizen-science value.

The underlying OVON engine answers a research question:

> How should limited human travel and observation time be allocated across routes, species, habitats, and survey durations to maximize useful ecological encounters or information?

The product answers a user question:

> Where should I go, what might I encounter, and why is this route worth my time?

### Core Principle

> **Sidetrack combines habitat, community evidence, scientific models, and personal discovery—but never pretends those are the same kind of knowledge.**

The public product maintains an explicit three-way distinction across information types:

1. **HABITAT RADAR** — What habitat suggests based on environmental context and structure.
2. **REPORTS NEAR THIS WALK** — What people and data sources have actually reported in the surrounding area (Route Evidence Layer).
3. **MODEL** — What Sidetrack's empirical models estimate.

These three layers answer separate questions and are **never merged into a single arbitrary score**.

---



## First-use product promise

The public experience begins with a simple question:

> **How do you want to get sidetracked?**

The complete product supports four intents: take a loop from here, add nature to a trip, find a species, and surprise me. The MVP implements the first intent exceptionally well and keeps the others out of the critical path until they are ready.

After choosing a loop, the person supplies a starting place and time budget. The product returns up to three humanly named routes:

- **The Easy One** — shortest and simplest;
- **The Birdy One** — strongest supported bird and habitat opportunity;
- **The Weird One** — exploratory and serendipitous only when the evidence supports a real difference.

Every route is paired with a visual and listenable field guide: representative images, tap-to-play calls or songs, where-to-look guidance, where-to-listen guidance, habitat transitions, and clear uncertainty/provenance language.

## Problem

Existing products solve important adjacent problems:

- Navigation products optimize time, distance, or traffic.
- Birding products show hotspots, sightings, lists, and species information.
- Identification products classify photos and sounds.
- Citizen-science platforms collect observations.
- Conservation tools analyze monitoring gaps.

The gap is a system that treats a journey itself as an ecological experience and scientific opportunity.

A user may want to:

- take a 45-minute walk and see more birds;
- make a small detour on the way to work;
- find a shaded, accessible route with nature;
- learn what to listen for in the next ten minutes;
- search for a plausible but under-documented species;
- contribute a useful checklist without making a separate trip;
- compare the biodiversity value of several routes;
- understand how the environment changes along a commute or vacation.

---

## Core product jobs

### Job 1: Plan a nature loop

> “I have 60 minutes. Start and end here. Give me a pleasant route and tell me what birds I may encounter.”

### Job 2: Discover nature on the way

> “I am going from A to B. Show what I might encounter on the normal route and what I gain with a 5-, 15-, or 30-minute detour.”

### Job 3: Search intelligently

> “Where is this species plausible this week, but not already over-observed?”

### Job 4: Learn before and during a route

> “Show the likely species, calls, habitat clues, look-alikes, and where along the route each becomes relevant.”

### Job 5: Contribute useful observations

> “Help me complete a feasible protocol that adds scientific value without turning the trip into work.”

### Job 6: Design a monitoring campaign

> “Given volunteer origins, time budgets, accessibility, and target species, where should the organization assign routes?”

---

## Product hierarchy

### Sidetrack

The public-facing route planner. It should be understandable without ecology or optimization vocabulary.

### Species Search Lab

A transparent specialist interface that exposes habitat match, evidence coverage, uncertainty, seasonality, and model provenance. It may show more technical detail and stricter warnings.

### Field Lab

A structured route and protocol tool for studies, schools, volunteer events, and pilot programs. It includes assignment, completion, failure logging, and randomized conditions.

### Network Planner

An organization-level planning tool for multiple observers, routes, time windows, and coverage targets.

---

## Initial audiences

### Casual walker

Wants a pleasant local walk and a short list of birds to notice. Does not want to configure models.

### Beginning birder

Wants achievable species, identification preparation, and a route that will not be discouraging.

### Experienced birder

Wants date-specific targets, unusual habitat combinations, under-documented locations, and transparent evidence.

### Traveler

Wants nature on an existing trip, not a separate expedition.

### Family or school group

Needs short routes, safety, bathrooms, rest points, accessible language, and educational prompts.

### Volunteer coordinator

Needs repeatable routes, protocol validity, completion estimates, and coverage across people.

### Researcher

Needs frozen data/model versions, treatment assignment, route logs, negative outcomes, and exportable analysis data.

### City or conservation planner

Needs aggregate accessibility, opportunity, heat, land-cover, and monitoring-gap maps.

---

## Differentiators

1. **Route-first ecological discovery**
2. **Nature opportunity per detour minute**
3. **Segment-level species expectations**
4. **Joint stop and corridor value**
5. **Personal novelty without rare-species gamification**
6. **Scientific-value mode for existing journeys**
7. **Human-feasible adaptive sampling**
8. **Accessibility and environmental-exposure routing**
9. **Explicit evidence and model provenance**
10. **One engine supporting consumer, research, and organizational tools**

---

## Product principles

### Explain why

Every route option should include a concise decomposition:

- additional travel;
- habitat transitions;
- likely species;
- new or unusual species opportunities;
- uncertainty;
- comfort/accessibility;
- scientific contribution.

### Offer choices, not an oracle

A menu of meaningfully different routes is more honest and usable than one “optimal” route.

### Preserve serendipity

The application should not reduce nature to a guaranteed checklist. It should communicate likelihood, uncertainty, and surprise.

### Avoid false precision

Use “relative opportunity” or “habitat–season match” until probabilities are calibrated.

### Never reward harmful chasing

Sensitive species may be excluded, generalized, delayed, or bundled into broader habitat guidance.

### Minimize setup

The first screen asks about intent, not technical configuration. Address, time budget, and optional constraints arrive in a natural sequence.

### Media teaches attention

Images and sounds are part of the core field-guide experience. Media is user-controlled, accessible, licensed per asset, and accompanied by practical look/listen guidance.


The default flow should require only:

- origin;
- route type;
- time budget;
- travel mode.

Everything else is optional or learned later.

### Design for failure

Routes can be closed, unsafe, hot, noisy, flooded, or inaccessible. The product must let users report a problem and recover gracefully.

---

## Scope by release

### Foundation release

- Flask skeleton
- SQLite schema
- routing and ecological provider contracts
- one frozen demonstration dataset
- route-request and provenance persistence
- local quality command
- no public launch

### MVP

- Kansas City walking loops
- address or map-pin origin
- 30–90 minute budgets
- three route options
- route map and timeline
- species opportunity by segment
- pre-trip field pack
- no accounts
- no observation submission
- demonstration/provisional labels

### Version 1

- point-to-point journeys
- detour frontier
- saved route link
- accessibility and comfort preferences
- optional anonymous route feedback
- improved environmental data
- empirical model for a small focal-species set
- researcher export of frozen route requests

### Version 2

- accounts and personal novelty
- observation logging
- route recap
- one midpoint adaptive replan
- transit-aware routes
- school/group mode
- researcher study configuration

### Moonshot suite

- multiple taxa
- migration-triggered routes
- heat and air-quality-aware routes
- organizational network optimization
- neighborhood nature-access equity
- longitudinal ecological change
- APIs for third-party navigation and travel products

---

## Explicit boundaries

The public app is not:

- a safety guarantee;
- a guarantee that a species will be detected;
- an exact rare-species chase map or live tracking radar;
- a raw occurrence-dot dump;
- a tool that equates report density with species abundance or current presence;
- a tool that treats lack of reports as species absence;
- a tool that treats presence-only records as nondetection-capable surveys;
- a tool that treats an obscured or sensitive location as more precise than the source permits;
- a replacement for official trail or transit information;
- a source of exact sensitive-species locations;
- a field-identification classifier;
- an authoritative occupancy product before validation;
- an eBird submission client unless an approved integration is developed.


---

## Success metrics

### Product metrics

- Route generation success rate
- Route completion rate
- Route acceptance by option
- Difference between predicted and actual duration
- User-reported usefulness
- Percent of routes with understandable explanations
- Repeat route planning without compulsive engagement mechanics

### Ecological metrics

- Calibration of encounter estimates
- Held-out ranking performance
- Habitat and seasonal coverage
- New valid complete checklists in low-coverage strata
- Information gain per volunteer minute
- Fraction of recommendations with stable provenance

### Accessibility metrics

- Share of users receiving at least one feasible route
- Route utility under wheelchair, low-walking, or transit constraints
- Missing-accessibility-metadata rate
- Opportunity differences across neighborhoods

### Trust metrics

- Percent of outputs with explicit provenance
- Rate of data-source or model-version mismatches
- Sensitive-location leakage incidents
- User comprehension of probability versus uncertainty
- Frequency of invalid or closed-route reports

---

## Open product questions

1. Is “Sidetrack” the final public name?
2. Should the first route mode be walking only or walking plus driving?
3. Should origin–destination trips enter Version 1 or the MVP?
4. Is the first public audience casual walkers or birders?
5. Should anonymous route feedback be stored before accounts exist?
6. Which species portfolio is safe and useful for the first calibrated model?
7. What partnership or permission is needed for eBird-derived public products?
8. Which Kansas City organization could support field validation?


### Learning and media metrics

- percentage of route users who open the field pack;
- percentage who use at least one audio example;
- whether people can recall a look/listen cue after the route;
- missing-media rate for supported focal species;
- attribution completeness rate;
- field-pack helpfulness without overwhelming the user.
