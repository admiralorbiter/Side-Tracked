# Sidetrack Master Roadmap & Innovation Backlog

## Revised Product Strategy: "Discover the Living World, One Walk at a Time"

Sidetrack connects nature routing with personal ecological discovery. Rather than presenting generic species checklists or competitive leaderboards, Sidetrack focuses on **Discovery Deck** collection, **Personal Novelty Routing**, **Eyes-Up Field Modes**, and **Playful Sidequests**.

---

## 🗺️ Master Release Sequence

| Milestone | Target Scope | Core Deliverables |
| :--- | :--- | :--- |
| **Sprint 11.6** | **Product Hardening & Life Cycle** | `WalkSession` lifecycle, plan provenance logging, typed `RouteSegment.habitat_type`, dynamic calendar week, `TaxonSupportBuilder` import fix, outcome-aware blocked route flow. |
| **Sprint 12** | **Taxon Concept Registry** | Sidetrack UUID `concept_id` crosswalking eBird, GBIF, iNaturalist; durable identity preventing taxonomy lumping/splitting breaks. |
| **Sprint 13** | **EBD/SED Checklist Pipeline** | Effort-based complete checklist ingestion, observer effort normalization, presence-only vs complete checklist evidence separation. |
| **Sprint 13.5** | **Environmental Feature Backbone** | Real environmental extraction (NLCD canopy, hydrography water edge, USGS 3DEP elevation) replacing string label inference. |
| **Sprint 14** | **Calibrated Species Model** | First calibrated species occupancy model, repeatable model contract, seasonal candidate index $CandidateTaxaIndex(cell, week)$. |
| **National Backbone** | **National Expansion Foundations** | Scalable spatial cell matrix, national taxonomy crosswalk, regional candidate indices. |
| **Sprint 15** | **My Local Birds / Discovery Deck** | Visual photo cards ("Regular birds around you this month"), "Saw / Heard / Listen" interactions, personal novelty routing persona (*The New Bird One*). |
| **Sprint 16** | **Eyes-Up Field Mode** | Spoken contextual guidance ("This stretch is canopy..."), audio clip playback, optional push-to-talk logging. |
| **Sprint 17** | **Nature on the Way** | Point-to-point routing optimizing nature exposure along commutes. |
| **Sprint 18** | **Detour Frontier** | Dynamic detour budget time-cost tradeoffs. |
| **Sprint 19** | **Search Lab Productization** | Production-ready Search Lab exploration interface. |
| **Sprint 20+** | **Advanced Capabilities** | Multi-taxa support (plants, trees, insects), transit routing, personalized preference learning. |

---

## 🔬 Innovation Backlog: Personal Discovery & Engagement Experiments

### 1. Discovery Deck vs Checklist
- **Concept**: Present photo cards rather than tabular form rows.
- **Evaluation Metrics**: Visual recognition speed, accidental logging rate, user enjoyment, cognitive load during walk recap.

### 2. Personal Novelty Routing
- **Concept**: Route persona (*The New Bird One*) optimizing expected uncollected species:
  $$U_{\text{new}}(R \mid H_u) = \sum_{s \notin H_u} w_s P_s(R)$$
  where $H_u$ is the user's personal discovery history.
- **Evaluation Metrics**: Rate of new species encounters per walk, user motivation to repeat walks.

### 3. Eyes-Up Field Guide
- **Concept**: Audio-first spoken guidance ("Watch trunks for Downy Woodpecker") combined with giant single-tap actions during active walks.
- **Evaluation Metrics**: Screen time during walk, heads-up engagement, user safety and navigation confidence.

### 4. Habitat Sidequests
- **Concept**: Personal non-competitive habitat missions (e.g. "Find 1 bird in 3 different habitat guilds this week") instead of rare-species chasing.
- **Evaluation Metrics**: Habitat exploration breadth, sustained weekly engagement without competitive anxiety.

### 5. Confusion Pair Mode
- **Concept**: When a user marks "Not Sure / Maybe", present side-by-side photo cards, key field marks, and vocalization clips of the 2-3 locally plausible look-alikes.
- **Evaluation Metrics**: Identification resolution accuracy, self-reported confidence.

### 6. "What's New This Week?" Phenology Surfaces
- **Concept**: Highlight seasonal arrivals and departures relative to the user's local discovery set as migration progresses.
- **Evaluation Metrics**: Seasonal re-engagement, anticipation of seasonal walks.
