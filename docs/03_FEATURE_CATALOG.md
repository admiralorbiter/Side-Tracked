# Feature Catalog

This is an intentionally broad catalog. It is not a commitment to build everything. Priorities:

- **P0** — required for the first usable loop product
- **P1** — likely Version 1
- **P2** — later product expansion
- **LAB** — experimental or research-only until validated
- **BLOCKED** — permission, data, or partnership required
- **DEFERRED** — deliberately not part of the current plan

---

# A. Planning and routing

## A1. Origin selection

- **P0** Address entry with explicit privacy statement
- **P0** Map-pin origin
- **P0** Known public-place selector
- **P1** Browser geolocation
- **P1** Transit-stop origin
- **P1** “Start one block away” privacy option
- **P2** Saved approximate home zone
- **P2** Multiple starting group locations
- **DEFERRED** Persistent exact home address

## A2. Nature Loop

- **P0** Closed walking loop
- **P0** 30–90 minute budget
- **P0** Return-to-origin verification
- **P0** Three route alternatives
- **P0** route-cost decomposition
- **P1** driving loop
- **P1** cycling loop
- **P1** distance budget in addition to time
- **P1** sunrise/sunset constraint
- **P2** transit plus walking loop
- **P2** one-way “meet me there” route
- **LAB** route with one midpoint adaptive replan

## A3. Nature on the Way

- **P1** origin–destination route
- **P1** maximum detour control
- **P1** baseline fastest route
- **P1** detour frontier
- **P1** route opportunity comparison
- **P2** scheduled departure time
- **P2** arrive-by constraint
- **P2** transit itinerary
- **P2** road-trip stops
- **P2** hotel-to-attraction travel mode
- **LAB** multi-day trip opportunity planner

## A4. Route alternatives

- **P0** The Easy One — lowest burden and simplest feasible loop
- **P0** The Birdy One — strongest supported bird and habitat opportunity
- **P0** The Weird One — exploratory/serendipitous route only when evidence supports a meaningful difference
- **P0** truthful reduction to one or two options when alternatives are not meaningful
- **P1** Most Likely Species
- **P1** Most Variety
- **P1** Most Scientifically Useful
- **P1** Beginner Route
- **P1** Accessible Route
- **P2** Quiet Route
- **P2** Shaded Route
- **P2** Heat-Safe Route
- **P2** Best Photography Route
- **LAB** Serendipity Route
- **LAB** Model-Disagreement Route

## A5. Route mechanics

- **P0** routing-provider abstraction
- **P0** matrix and geometry from consistent provider
- **P0** closed-loop cost check
- **P0** observation and access buffers
- **P0** route artifact version
- **P1** isochrone candidate generation
- **P1** corridor-edge rewards
- **P1** route simplification and segment generation
- **P1** slope/elevation
- **P1** opening hours
- **P2** time-dependent traffic/transit
- **P2** closure and weather risk
- **LAB** chance-constrained route duration
- **LAB** CVaR route-risk optimization
- **LAB** exact solver for small route instances
- **LAB** Rust heuristic engine

---

# B. Ecological opportunity

## B1. Species expectation

- **P0** route-wide relative species opportunity list
- **P0** segment-level habitat–season match
- **P0** clear provisional/model status
- **P1** recent route occurrence context ("Reports Near This Walk", up to 30 days)
- **P1** historical seasonal evidence (cyclic-week matched EBD/SED, GBIF)
- **P1** complete-checklist coverage context
- **P1** source-aware occurrence display & geoprivacy aggregation
- **P1** calibrated focal-species encounter model
- **P1** expected encounter by observation duration
- **P1** species-specific uncertainty
- **P2** community-level latent assemblage
- **P2** personal novelty
- **LAB** observer-effort corrected presence-only surface ($E_s^{\text{relative}}$)
- **LAB** model–evidence disagreement frontier ($D_s(x,t)$)
- **LAB** under-documented route gap search ($U_{\text{gap}}(R)$)
- **LAB** integrated presence-only and checklist model
- **BLOCKED** public use of restricted products without permission

## B2. Search modes

- **P1** Likely Encounter
- **P1** Expected but Under-Documented
- **P1** Scientific Uncertainty
- **P1** Difficult-to-Detect Opportunity
- **P1** Exploratory Habitat Analog
- **P2** credible absence
- **P2** arrival-front search
- **P2** personal target list
- **LAB** platform-disagreement frontier
- **LAB** model–evidence surprise frontier
- **LAB** static versus radar-triggered opportunity
- **DEFERRED** public exact rare-species chase map


## B3. Species bundles

- **P1** beginner-friendly residents
- **P1** spring migrants
- **P1** wetland birds
- **P1** urban aerial insectivores
- **P2** raptors
- **P2** sound-first species
- **P2** route habitat guilds
- **P2** custom bundle
- **LAB** learned community factors

## B4. Segment and corridor ecology

- **P0** route split into ecological segments
- **P0** habitat label per segment
- **P1** species list per segment
- **P1** edge-level canopy/impervious/water features
- **P1** habitat-transition reward
- **P2** corridor continuity
- **P2** streetlight and collision-risk context
- **P2** noise and air-quality exposure
- **LAB** line-integral encounter intensity
- **LAB** moving versus stationary observation model

## B5. Season and time

- **P0** target date/week
- **P0** provisional annual phenology
- **P1** date-derived week
- **P1** time-of-day field guidance
- **P1** dawn/dusk constraints
- **P2** weather adjustment
- **P2** migration-night adjustment
- **LAB** dynamic arrival-front model
- **LAB** radar-informed morning route

---

# C. Species learning

## C1. Species profiles

- **P0** common and scientific name
- **P0** canonical taxon ID
- **P0** representative image with source, creator, license, and attribution
- **P0** short field description
- **P0** habitat
- **P0** seasonal status
- **P0** provenance
- **P0** at least one useful call or song clip when licensed media is available
- **P0** text description of the sound
- **P0** where-to-look and where-to-listen guidance
- **P0** explicit missing-media fallback
- **P1** look-alikes
- **P1** ethical observation note
- **P2** life history
- **P2** conservation context
- **P2** local trend summary

## C2. Pre-trip field pack

- **P0** likely species
- **P0** listen-for species with tap-to-play examples
- **P0** habitat clues
- **P0** one plausible surprise
- **P1** beginner/advanced variants
- **P1** printable page
- **P1** route-specific offline media cache
- **P1** optional audio playlist with user-controlled playback
- **P2** quiz mode
- **DEFERRED** custom identification model

## C3. In-route guidance

- **P0** current segment
- **P0** next habitat transition
- **P0** one or two relevant species cues
- **P0** where to look and what to listen for
- **P0** tap-to-play sound with pause/stop controls
- **P0** quiet mode
- **P0** route progress
- **P1** optional user-initiated audio sequence
- **P2** uncertainty-aware prompt
- **P2** one midpoint replan
- **DEFERRED** continuous notification stream

---

# D. Observation and citizen science

## D1. Simple route feedback

- **P1** route completed
- **P1** route abandoned
- **P1** duration
- **P1** access issue
- **P1** route quality
- **P1** species seen/not seen/unsure
- **P1** anonymous session identifier
- **P2** photo or sound attachment
- **P2** checklist link
- **P2** corrected route geometry

## D2. Structured Field Lab

- **P2** study definition
- **P2** participant eligibility
- **P2** assigned route
- **P2** randomized condition
- **P2** protocol timer
- **P2** required stop outcomes
- **P2** failure categories
- **P2** assignment probability logging
- **P2** export
- **LAB** adaptive study policy
- **LAB** off-policy evaluation

## D3. Scientific quality

- **P1** source-aware evidence model
- **P1** complete-checklist distinction
- **P1** duplicate event handling
- **P1** contradictory evidence quarantine
- **P1** observer-effort fields
- **P1** shared-checklist handling
- **P1** provenance and release version
- **P2** acoustic validation
- **P2** expert review queue
- **LAB** observer-aware detectability

---

# E. Personalization

## E1. Anonymous preferences

- **P1** route priority selection
- **P1** observer experience
- **P1** walking comfort
- **P1** accessibility needs
- **P1** time budget
- **P1** taxon interest
- **P2** session preference cookie

## E2. Accounts

- **P2** account registration
- **P2** saved routes
- **P2** approximate home zone
- **P2** seen-species history
- **P2** personal novelty
- **P2** route preference learning
- **P2** data export and deletion
- **DEFERRED** exact home address profile

## E3. Preference learning

- **LAB** pairwise route comparison
- **LAB** route-menu choice model
- **LAB** noisy preference learning
- **LAB** learned tradeoff weights
- **LAB** completion-aware recommendation
- **LAB** counterfactual route explanation

---

# F. Accessibility, comfort, and safety

## F1. Accessibility

- **P0** unknown access state
- **P0** no automatic “accessible” default
- **P1** step-free
- **P1** wheelchair transit fields
- **P1** slope
- **P1** surface
- **P1** maximum continuous walking distance
- **P1** bench/rest point
- **P1** restroom
- **P2** curb cuts
- **P2** sensory-friendly guidance
- **P2** low-vision route instructions
- **P2** verified accessibility feedback

## F2. Comfort

- **P1** shade
- **P1** tree canopy
- **P1** route steepness
- **P1** path versus roadside
- **P2** heat exposure
- **P2** air quality
- **P2** noise
- **P2** lighting
- **P2** weather exposure
- **P2** crowding

## F3. Safety and access

- **P0** public/unknown/restricted
- **P0** reviewed/unknown/seasonal/excluded
- **P0** daylight warning
- **P0** route-provider failure warning
- **P1** opening hours
- **P1** temporary closure report
- **P1** flood or construction warning
- **P2** official closure feed
- **P2** group route preference
- **DEFERRED** claim that a route is guaranteed safe

---

# G. Maps and visualization

- **P0** route map
- **P0** text-equivalent timeline
- **P0** selected stops
- **P0** habitat segments
- **P0** provenance panel
- **P1** occurrence-source layers
- **P1** complete-checklist coverage
- **P1** opportunity layer
- **P1** uncertainty layer
- **P1** accessibility layer
- **P1** detour frontier chart
- **P1** route-value waterfall
- **P2** migration layer
- **P2** heat layer
- **P2** neighborhood nature-access map
- **LAB** model-disagreement atlas

---

# H. Research and organization suite

## H1. Network Planner

- **P2** multiple volunteer origins
- **P2** route portfolio
- **P2** species and habitat coverage targets
- **P2** fairness constraints
- **P2** participant capability
- **P2** route assignment
- **P2** monitoring calendar
- **LAB** stochastic completion
- **LAB** resilience analysis
- **LAB** minimum monitoring backbone

## H2. Research dashboard

- **P2** data/model manifest
- **P2** replay experiment
- **P2** policy benchmark
- **P2** calibration
- **P2** spatial holdouts
- **P2** ablation
- **P2** route feasibility frontier
- **P2** export
- **LAB** limited-adaptivity study
- **LAB** source-integration study
- **LAB** car-free opportunity frontier

---

# I. Multi-taxon expansion

- **P2** generic taxon contract
- **P2** taxon-specific phenology contract
- **P2** taxon-specific detectability
- **P2** pollinator pack
- **P2** native plant pack
- **P2** amphibian-after-rain pack
- **P2** fungi pack
- **P2** urban tree pack
- **P2** night nature pack
- **LAB** multimodal sensing and taxon bundles

---

# J. Platform and operations

- **P0** app factory
- **P0** blueprints
- **P0** environment-based configuration
- **P0** SQLite migrations
- **P0** local quality command
- **P0** structured logging
- **P0** data/model manifest
- **P0** deterministic demo mode
- **P1** background data refresh CLI
- **P1** artifact registry
- **P1** request cache
- **P1** rate limiting
- **P1** health page
- **P1** backup procedure
- **P1** privacy deletion tool
- **P2** worker process
- **P2** PostgreSQL migration option
- **P2** Rust extension
- **DEFERRED** microservice architecture before scale requires it

---

# K. Explicitly rejected or deferred features

- Rare-species competitive leaderboard
- Public exact nesting or sensitive-species locations
- Infinite social feed
- Engagement streaks as a primary mechanic
- Unverified automated species identification
- Automatic eBird submission without approved integration
- Full national deployment before one regional model is validated
- Exact-address retention by default
- Multiple routing engines inside views
- Experiment modules imported directly by the public app


# L. Species media, attribution, and field guidance

## L1. Media inventory

- **P0** canonical media asset record
- **P0** photo, audio, and optional sonogram asset types
- **P0** source asset ID and original source URL
- **P0** creator and attribution string
- **P0** license identifier and license URL
- **P0** cached-file checksum when caching is permitted
- **P0** taxon ID and media role
- **P0** active, unavailable, replaced, and revoked states
- **P1** locale, region, sex, age, and vocalization type
- **P1** quality/editorial ranking
- **P1** multiple images and calls per taxon

## L2. Media source policy

- **P0** per-asset license validation
- **P0** no all-rights-reserved caching without explicit permission
- **P0** no assumption that observation license equals photo or sound license
- **P0** attribution rendered wherever media is shown
- **P0** provider terms and retrieval date in manifest
- **P0** license allowlist documented before public release
- **P1** automated media-manifest verification
- **P1** relinking or disabling assets when provider state changes
- **BLOCKED** Macaulay/Cornell media caching without explicit permitted use

## L3. Playback and accessibility

- **P0** no autoplay
- **P0** user-controlled play, pause, stop, and volume
- **P0** only one clip plays at a time
- **P0** text description or transcript-like vocalization note
- **P0** image alt text
- **P0** keyboard-operable controls
- **P0** quiet mode
- **P1** preload metadata only
- **P1** low-bandwidth media mode
- **P1** offline route pack

## L4. Field cue content

- **P0** look-for field marks
- **P0** where-to-look location guidance
- **P0** listen-for phrase
- **P0** where/when-to-listen context
- **P0** common confusion species
- **P0** ethical observation note
- **P1** beginner and advanced versions
- **P1** route-segment-specific cue selection
- **P2** multilingual field cues
