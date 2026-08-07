# User Experience and Information Architecture

## Experience thesis

Sidetrack should feel like a calm, clever field guide that happens to understand routes. It should not feel like a routing dashboard with birds sprinkled on top, and it should not feel like a research interface disguised as a consumer app.

The public experience follows this order:

1. **Curiosity** — what kind of sidetrack do you want?
2. **Place** — where should it start?
3. **Time** — how long do you have?
4. **Choice** — which route tradeoff feels right?
5. **Preparation** — what should you look and listen for?
6. **Journey** — what is relevant on this segment?
7. **Reflection** — what did you notice, and was the route useful?

Research detail is available, but never the first thing a person has to decode.

---

## Voice and tone

### Canonical identity

**Sidetrack**  
**A Field Guide to Getting Sidetracked**

The name provides the wink. The interface should not turn every label into a joke.

### Tone rules

- Warm, observant, and slightly funny.
- Specific rather than breathless.
- Never childish by default.
- Never gamify rare species or exact locations.
- Be serious about safety, privacy, access, licenses, and uncertainty.
- Prefer “worth listening for” over “guaranteed sighting.”
- Prefer “relative opportunity” over fake probability.

A good screen may contain one playful phrase. A safety or provenance message should be plain.

---

## Public application map

```text
Home
├── Take a Loop from Here
├── Add Nature to a Trip          # later release
├── Find a Species                # Search Lab
├── Surprise Me                   # later release
├── Route Results
│   ├── Route comparison
│   ├── Route detail
│   ├── Before-you-go field pack
│   ├── In-route timeline
│   ├── Accessibility and comfort
│   └── Data and limitations
├── Species
│   ├── Species profile
│   ├── Photo and sound
│   └── Where to look and listen
├── After the Route
├── About the Science
└── Privacy, Data, and Limitations
```

Research, administration, and network-planning pages live behind separate navigation and should not crowd the public experience.

---

## Home screen

### Primary question

> **How do you want to get sidetracked?**

The full product supports four intent cards:

| Intent | User meaning | Release |
|---|---|---|
| **Take a loop from here** | “I have some time and want to end where I started.” | MVP |
| **Add nature to a trip** | “I am already going somewhere; show me worthwhile detours.” | P1 |
| **Find a species** | “Help me plan a responsible search.” | P1/Search Lab |
| **Surprise me** | “Take me through unfamiliar habitats and plausible discoveries.” | P1/LAB |

For the MVP, the loop is the only required active card. Future cards should be hidden or clearly labeled, not dead controls.

### Primary loop form

After selecting the loop:

1. **Where should we start?**
   - current location;
   - address;
   - map pin;
   - known public place.
2. **How long do you want to get sidetracked?**
   - 30, 45, 60, 90 minutes;
   - 45 minutes is the default.
3. **How are you going?**
   - walking default;
   - driving and cycling later.
4. **Anything we should know?**
   - collapsed optional accessibility and comfort settings.

The first screen should not expose lambda values, QBC, habitat kernels, model versions, or a dozen sliders.

### Privacy copy

Near the location control:

> Your starting address is used to plan this route and is not saved by default.

---

## Route results

Return up to three routes. Each needs a genuinely distinct tradeoff.

### Route names

- **The Easy One** — shortest, simplest, and lowest burden.
- **The Birdy One** — highest supported bird and habitat opportunity for the time.
- **The Weird One** — most unusual, novel, or serendipitous supported option.

The Weird One is conditional. When evidence cannot support a meaningful exploratory route, use a truthful alternative such as **The Scenic One**, or show only two routes.

### Route card anatomy

Each card includes:

- total time and distance;
- confirmation that it returns to the starting point;
- route difficulty and known accessibility status;
- habitats crossed;
- a few likely or interesting species;
- one or two thumbnail images;
- a short tradeoff explanation;
- provenance badge;
- primary action: **See this route**.

Example:

> **The Birdy One**  
> 47 min · 2.6 mi · returns to start  
> Mature canopy, creek edge, open lawn  
> Listen for Northern Cardinal and Carolina Wren  
> Nine minutes longer than The Easy One; crosses two additional habitat types.

### Comparability

All cards use the same units, evidence window, travel assumptions, and supported species set. Do not compare one route’s modeled count with another route’s raw occurrence count.

---

## Route detail

The route detail page is organized into an explicit three-way evidence hierarchy:

1. **Route summary**
2. **Before-you-go field pack**
3. **Habitat Radar** (*What habitat suggests*)
4. **Reports Near This Walk** (*What people/data sources have reported*)
5. **Map and text route timeline**
6. **Segment cards**
7. **Comfort, access, and safety**
8. **Why this route**
9. **Data and limitations**
10. **Start route**

The field pack and habitat radar appear before dense evidence maps to prepare the user for the actual walking experience.

---

## Reports Near This Walk (Route Evidence Layer)

The **Reports Near This Walk** section displays normalized biodiversity occurrence reports near the route without implying current presence, abundance, or exact organism positions.

### User Filters & Tabs

- **Recent** (up to 30 days ago, e.g., eBird Recent, iNaturalist)
- **Seasonal History** (historical occurrences weighted by cyclic-week closeness from EBD/SED, GBIF)
- **My Sightings** (private personal `DiscoveryRecord` items)

### Sample Evidence Presentation Cards

> **Northern Flicker**  
> Reported from 3 nearby public checklist locations in the last 14 days.  
> Nearest displayable report location: about 480 m from this route.  
> Most recent: 2 days ago. Source: eBird.

> **Baltimore Oriole**  
> Regularly reported in this area during early May in previous years.  
> No qualifying recent public report found.

> **Obscured Record (iNaturalist)**  
> Reported in the broader area. *(No precise route distance claims calculated from randomized coordinates).*

### In-Route Non-Chasing Rules

- Evidence map layers are **OFF by default** to minimize map clutter and screen distraction.
- Walk mode strictly avoids "Pokémon radar" chasing alerts (e.g. *"Northern Flicker 132 m ahead!"*).
- In-route guidance presents calm contextual notes: *"Recent context: Northern Flickers have public reports from this broader area recently."*


## Before-you-go field pack

The field pack is a core MVP feature, not decoration.

It contains:

- five likely or useful focal species;
- representative photograph for each supported species;
- one tap-to-play call or song when licensed media is available;
- “look here” guidance;
- “listen for” guidance;
- one or two simple visual marks;
- similar species or common confusion;
- seasonal note;
- media attribution;
- uncertainty or provisional label.

Example species card:

> **Northern Cardinal**  
> Look: dense shrubs and lower branches along the canopy segment.  
> Listen: clear repeated whistles; often heard before seen.  
> [Play example call]  
> Common confusion: Summer Tanager from a distance.  
> Photo and audio credits.

### Audio behavior

- Never autoplay.
- One explicit play button per clip.
- Pause/stop control always visible.
- Remember a user’s mute/quiet choice for the current session.
- Provide a text description of the vocalization.
- Avoid overlapping playback.
- Use short educational excerpts or source-approved clips.

### Beginner and advanced variants

**Beginner**

- fewer species;
- conspicuous species;
- plain field marks;
- “unsure” is a valid answer;
- simple look/listen locations.

**Advanced**

- time-specific vocalizations;
- sex/age distinctions when relevant;
- uncertainty and evidence notes;
- under-documented segments;
- optional count protocol.

---

## Route timeline

The route timeline is the text-equivalent and explanatory spine of the journey.

Example:

### 0–8 minutes — plaza and open urban edge

**Look up:** Chimney Swifts may circle above tall buildings.  
**Likely:** House Sparrow, European Starling.  
**Listen:** short, rapid twittering overhead.  
**Media:** one image and tap-to-play example for the focal species.

### 8–21 minutes — mature street canopy

**Look:** lower branches, shrubs, and trunks.  
**Listen:** Northern Cardinal, Carolina Wren, Red-bellied Woodpecker.  
**Why this segment matters:** shade and mature canopy create a different assemblage from the plaza.

### 21–35 minutes — creek and riparian edge

**Look:** exposed branches over water and slow-moving edges.  
**Possible:** Belted Kingfisher, Great Blue Heron.  
**Uncertainty:** local complete-checklist coverage is limited for the selected week.

The route should explain *where along the route* a species becomes relevant rather than present one undifferentiated list.

---

## In-route mode

The in-route page is deliberately quiet.

Show:

- current segment;
- distance or time to the next transition;
- one or two relevant species cues;
- where to look;
- tap-to-play sound;
- route progress;
- return-to-start assurance;
- access or closure alert.

Do not show:

- continuous notification streams;
- automatic audio;
- a dense research dashboard;
- pressure to record every species;
- precise sensitive-species targets.

### Quiet mode

A single **Quiet mode** control disables all optional prompts and audio suggestions while retaining route directions.

### Midpoint adaptation

A later version may offer one optional midpoint update when a route segment is closed or a meaningful condition changes. The MVP is static.

---

## After-route experience

The first release may keep this lightweight, but it should be designed now.

### Minimal recap

- route completed, partly completed, or abandoned;
- actual duration;
- access or route problems;
- species seen, heard, unsure, or not recorded;
- route rating;
- whether the field pack helped.

### Future recap

- habitats crossed;
- species expected versus noticed;
- personal discoveries;
- nature opportunity added over the shortest route;
- optional link to an external checklist;
- saved field pack;
- recommendation preference learning.

The recap should celebrate attention, not species count alone.

---

## Nature on the Way

Later point-to-point workflow:

1. Choose **Add nature to a trip**.
2. Enter origin and destination.
3. Select travel mode and departure time.
4. Select acceptable detour: 0, 5, 15, or 30 minutes.
5. Compare fastest, best-value, and discovery routes.
6. Show the detour frontier and its knee.

Example:

> The 12-minute detour crosses a creek corridor and adds six plausible species opportunities. The next 15 minutes add little additional value.

---

## Species Search Lab

Inputs:

- canonical species or bundle;
- date/week;
- time and travel mode;
- objective;
- observer profile;
- access constraints.

Objectives:

- likely encounter;
- expected but under-documented;
- scientific uncertainty;
- difficult-to-detect opportunity;
- exploratory habitat analog.

Each result must expose:

- evidence sources and counts;
- complete-checklist coverage separately from presence-only evidence;
- habitat–season match;
- uncertainty;
- calibrated versus relative status;
- sensitive-location policy;
- why the location is ranked.

Search is guidance, never a promise.

---

## Empty, error, and degraded states

### No feasible loop

> No verified loop fits 30 minutes with the selected step-free constraint. At 45 minutes, two options are available.

Offer one controlled relaxation at a time.

### Address not found

Offer map pin and public-place search. Do not repeatedly retry automatically.

### Location permission denied

Keep address and map-pin options fully usable.

### Routing unavailable

Do not draw a straight line and label it a walking route. Show a visible degraded state and allow retry.

### Ecological model unavailable

Generate the route only if useful, but remove or label ecological scores. Do not substitute random values.

### No evidence for a species

> There is not enough matching evidence for a species-specific route. This result uses a general seasonal habitat prior.

### Media unavailable

Show text field guidance and an external source link where permitted. The route remains usable without media.

### License no longer valid

Hide the cached asset immediately; keep attribution history in the audit record.

### No meaningful route alternatives

Show one route and explain why:

> The available path network produces one feasible loop within this budget.

---

## Information hierarchy and provenance

Every value belongs to one class:

1. **Measured** — route geometry or direct environmental data.
2. **Observed** — occurrence or checklist evidence.
3. **Modeled** — habitat, season, encounter, or uncertainty.
4. **Assumed** — buffers, observer multipliers, or provisional access rules.
5. **Simulated** — research/demo output.
6. **Unavailable** — missing or unsupported.

The public explanation is brief. A details panel contains the full provenance.

---

## Map design

The map is an enhancement, not the only representation.

Narrow map adapter:

```text
renderRoute(routeGeoJSON)
renderSegments(segmentGeoJSON)
renderEvidenceLayer(features, source)
renderOpportunitySurface(features)
focusSegment(segmentId)
setSelectedRoute(routeId)
```

Default layers:

- selected route;
- route segments;
- current location when permission is granted;
- optional evidence and habitat layers.

Never show every layer at once.

---

## Accessibility

- full keyboard operation outside the map;
- semantic headings and landmarks;
- route timeline sufficient without map use;
- text alternatives for informative images;
- transcript or vocalization description for audio;
- no audio autoplay;
- no color-only meaning;
- visible focus;
- reduced motion;
- large targets;
- accessible audio controls;
- unknown accessibility explicitly shown;
- quiet mode available.

---

## Visual direction

The visual system should feel like:

- a field notebook;
- a trustworthy map;
- a slightly funny guide who knows when to be serious.

Potential visual elements:

- warm paper-like neutrals;
- ink and habitat accent colors;
- clear sans-serif body type;
- restrained field-note annotations;
- species photography with consistent crops;
- waveform or sonogram used sparingly;
- route cards that read like choices, not KPI panels.

Avoid crowded dashboard grids on the public route page.

---

## First prototype screens

1. Intent-first home
2. Loop location and budget form
3. Route-loading/progress state
4. Route comparison: Easy, Birdy, Weird/Scenic
5. Route detail
6. Before-you-go field pack
7. In-route segment view
8. After-route recap
9. Species profile with photo and sound
10. Data and limitations panel
11. Search Lab list view
12. Local admin manifest view

The detailed state machine is in [UI Workflows and Screen States](10_UI_WORKFLOWS_AND_SCREEN_STATES.md).
