# UI Workflows and Screen States

## Purpose

This document describes the actual public interaction, screen transitions, required states, and acceptance criteria. It complements the higher-level UX document.

The first implementation is a mobile-first web application. Every core workflow must remain usable with server-rendered HTML. HTMX and the map improve the experience but do not own the domain state.

---

# 1. Global shell

## Header

- Sidetrack wordmark
- tagline on home only: **A Field Guide to Getting Sidetracked**
- compact navigation:
  - Plan a route
  - Species
  - About
- research/admin links separated from public navigation

## Footer

- data and limitations
- privacy
- media credits
- source attribution
- build/data/model/media manifest versions

## Global controls

- quiet mode
- text size/browser-native zoom support
- reduced motion respected
- no global audio autoplay

---

# 2. Home and intent selection

## Screen: Home

### Heading

> How do you want to get sidetracked?

### Intent cards

#### Take a loop from here

Description:

> Pick a starting place and an amount of time. We will bring you back with a route and a small field guide.

Primary action for MVP.

#### Add nature to a trip

Description:

> See what a five- or fifteen-minute detour could add to a trip you are already making.

Hidden or clearly marked “coming later” until complete.

#### Find a species

Description:

> Plan a responsible search using season, habitat, evidence, and uncertainty.

Links to Search Lab when available.

#### Surprise me

Description:

> Favor unfamiliar habitats and plausible discoveries.

Hidden or experimental until the objective is trustworthy.

### Home acceptance criteria

- first interaction is intent, not a technical form;
- only available flows are actionable;
- no dead controls;
- keyboard focus order is logical;
- screen reader labels explain the intent cards;
- no map is required on the first screen.

---

# 3. Loop planner workflow

## State 3.1: Choose origin

### Heading

> Where should we start?

### Options

1. Use current location
2. Enter an address
3. Drop a pin
4. Choose a known public place

### Privacy copy

> We use the location to plan the route. The raw address is not saved by default.

### Validation

- supported-region check;
- coordinate presence;
- geocoder confidence;
- public-place selection has valid entrance coordinate;
- origin is not stored before user continues unless needed for a short-lived planning session.

### Error states

- permission denied;
- geocoder unavailable;
- address ambiguous;
- outside pilot region;
- location lacks a feasible walking graph connection.

## State 3.2: Choose budget

### Heading

> How long do you want to get sidetracked?

Controls:

- 30 minutes
- 45 minutes — default
- 60 minutes
- 90 minutes
- custom, within supported limits

Display a rough walking-distance estimate only as an estimate.

## State 3.3: Optional preferences

### Heading

> Anything we should know?

Collapsed by default:

- step-free preference;
- maximum slope;
- paved or firm surface;
- shorter/easier;
- more shade;
- avoid unverified access;
- beginner/intermediate/advanced field guide;
- quiet mode.

Unknown data must be visible. Do not represent missing accessibility information as accessible.

## State 3.4: Review request

Compact summary:

```text
Loop from: Loose Park
Time: 45 minutes
Mode: walking
Field guide: beginner
Preferences: more shade, avoid unverified access
```

Primary action:

> Find my routes

---

# 4. Planning and loading

## Loading screen

Do not show a blank spinner. Explain the stages in plain language:

1. finding paths that return to the start;
2. checking time and access;
3. comparing habitat and bird opportunities;
4. building the field guide.

Stages are descriptive, not fake progress percentages.

### Timeout state

> Route planning is taking longer than expected.

Options:

- keep waiting;
- try fewer constraints;
- return to planner.

### Provider failure

> The walking-route service is unavailable, so we have not generated a route.

Do not substitute a straight line.

---

# 5. Route comparison

## Screen anatomy

- request summary;
- up to three route cards;
- optional comparison map;
- edit request;
- data/provenance note.

## Route cards

### The Easy One

Primary goal: lowest burden among useful routes.

Show:

- duration;
- distance;
- surface/slope/access confidence;
- habitat count;
- two or three focal species;
- why it is easy.

### The Birdy One

Primary goal: strongest supported ecological opportunity.

Show:

- additional time versus Easy;
- added habitat transitions;
- focal species opportunity;
- one representative image;
- why the detour is useful.

### The Weird One

Primary goal: supported novelty or exploration.

Show:

- unusual habitat or route feature;
- uncertainty/provisional status;
- potential discoveries;
- why the route is different.

The route is omitted when its objective cannot be supported.

## Card actions

- See this route
- Compare details
- Change preferences

## No-alternative state

> The path network produces one feasible loop for this budget and set of constraints.

Show the one route without pretending alternatives exist.

---

# 6. Route detail

## Top summary

- route name;
- duration and distance;
- return-to-start confirmation;
- access and comfort summary;
- primary action: **Get ready** or **Start route**.

## Section order

1. Before-you-go field pack
2. Route map and timeline
3. Segment detail
4. Why this route
5. Comfort/access/safety
6. Data and limitations

## Why field pack comes first

The person needs a compact mental model before leaving. A large map does not teach what to notice.

---

# 7. Before-you-go field pack

## Default card count

- 4–6 focal species for beginner mode;
- up to 8 for advanced mode;
- one plausible surprise separated from likely species;
- no rare-species promise.

## Species card

Required fields:

- common and scientific name;
- representative image or missing-image state;
- field marks;
- where to look;
- sound description;
- tap-to-play clip or missing-audio state;
- where/when to listen;
- route segment(s) where relevant;
- media attribution;
- evidence/provisional badge.

## Media controls

- play button has species and clip type in accessible name;
- pause/stop available;
- only one clip plays at a time;
- no autoplay;
- visible duration;
- quiet mode disables prompts but does not remove text;
- keyboard operable.

## Field-pack actions

- Start route
- Print/save lightweight field pack
- Turn on quiet mode
- View all media credits

---

# 8. Route timeline and map

## Timeline structure

Each segment card includes:

- segment number and time/distance range;
- habitat label;
- path/navigation note;
- look cue;
- listen cue;
- supported species;
- uncertainty or coverage note;
- map focus action.

## Map behavior

- selected segment highlighted when timeline card receives focus;
- map selection updates timeline without trapping keyboard focus;
- route remains understandable without map;
- evidence layers are off by default;
- map controls use plain labels.

## Text alternative

A complete ordered route description is available as HTML, including turns or major landmarks as permitted by the routing provider.

---

# 9. In-route mode

## Screen priorities

1. stay on route;
2. understand current habitat;
3. receive one or two relevant cues;
4. keep audio optional;
5. report a route problem.

## Current segment screen

- progress indicator;
- next major turn or habitat transition;
- one visual cue;
- one listening cue;
- tap-to-play sound;
- “I noticed this” optional action;
- quiet mode;
- end route.

## Location behavior

The active route may use location to show progress. The product does not retain a continuous trail by default. A research protocol may use different retention rules with explicit consent.

## Off-route state

> You appear to be off the planned loop.

Options:

- return to route;
- rejoin ahead;
- stop route.

Do not silently rewrite the ecological claims after re-routing without regenerating the route artifact and field pack.

## Closure or access problem

Allow:

- blocked path;
- private/restricted access;
- construction;
- unsafe condition;
- inaccessible surface;
- other.

The app may offer a basic return route or end the session. Full adaptive ecological replanning is later work.

---

# 10. After-route workflow

## Completion screen

### First question

> How did the sidetrack go?

Options:

- completed;
- partly completed;
- stopped early;
- route was not usable.

### Minimal feedback

- actual duration;
- route problem;
- field pack helpfulness;
- species noticed, heard, unsure, or skipped;
- one free-text note.

### Recap

- habitats crossed;
- field-pack species reviewed;
- media clips used;
- route choice tradeoff;
- optional external checklist link;
- data retention explanation.

The recap rewards observation and learning, not the raw number of species.

---

# 11. Search Lab workflow

## Search input

- species/bundle autocomplete using canonical taxonomy;
- date/week;
- starting place;
- time budget;
- objective;
- observer profile;
- access constraints.

## Search result

- ranked locations/routes;
- relative opportunity or calibrated probability label;
- evidence by source;
- complete-checklist effort;
- habitat/season match;
- uncertainty;
- sensitive-species treatment;
- why this is ranked;
- suggested observation duration;
- photo and sound field cue.

## No-evidence state

> We do not have enough matching evidence for a species-specific search. This result uses a broader habitat and seasonal prior.

The result status must change accordingly.

---

# 12. Media states

## Image available

Render image, alt text, creator, source, and license.

## Image missing

Render a consistent placeholder and retain all textual field cues.

## Audio available

Render user-controlled playback, duration, sound description, recordist, source, and license.

## Audio missing

Render the vocalization description and link to an approved external source if permitted.

## Asset revoked or unavailable

Do not display stale cached media. Mark the asset inactive and fall back immediately.

## Low bandwidth

- no automatic image loading beyond thumbnails;
- audio preload disabled;
- user may request the route pack explicitly.

---

# 13. Provenance states

Every route and field pack has a concise badge:

- Empirical model
- Provisional model
- Simulated demonstration
- Live occurrence context
- Curated media
- Missing/limited data

The details panel lists:

- route provider and graph version;
- ecological model version;
- evidence window;
- environmental artifact version;
- taxonomy version;
- media manifest version;
- known limitations.

---

# 14. Screen-level acceptance checklist

For every public screen:

- [ ] clear primary action;
- [ ] useful heading;
- [ ] keyboard navigation;
- [ ] loading state;
- [ ] empty state;
- [ ] error state;
- [ ] degraded state when relevant;
- [ ] mobile layout;
- [ ] no unsupported certainty;
- [ ] no inaccessible audio behavior;
- [ ] no raw-address leakage;
- [ ] media attribution adjacent or one click away;
- [ ] text representation of map-dependent information.
