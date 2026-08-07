# Glossary

## Sidetrack

The public route-first biodiversity discovery application.

## OVON

Optimal Volunteer Observation Network. The research and optimization engine/laboratory beneath Sidetrack.

## Journey intent

The user's high-level goal: loop from here, nature on the way, find a species, or surprise me.

## The Easy One

The route option with the lowest supported burden while remaining useful.

## The Birdy One

The route option with the strongest supported bird/habitat opportunity for the budget.

## The Weird One

An exploratory/serendipitous route option shown only when the evidence supports a meaningful alternative.

## Field pack

A route-specific set of species images, sounds, field marks, where-to-look/listen guidance, and attribution.

## Field cue

Structured educational guidance for one taxon and audience: what to look for, what to listen for, where, confusion species, and ethics note.

## Media manifest

Versioned list of approved media assets, licenses, attribution, checksums, and selections used by a release or route artifact.

## Canonical taxon ID

Stable internal identifier used across data sources. Common names are display labels, not analytical keys.

## Occurrence evidence

A record indicating that a taxon was reported present at some time and spatial resolution. Occurrence evidence can be presence-only (eBird Recent, GBIF, iNaturalist) and does not imply a complete checklist survey or nondetection.

## Checklist location

The published coordinate associated with an eBird checklist. Sidetrack describes these as *"reported from a checklist location near this walk"* rather than assuming the animal was located at that exact coordinate.

## Observation point

A source coordinate intended to represent an occurrence location, accompanied by whatever positional uncertainty the provider supplies.

## Coordinate uncertainty

The radius around a published point that contains the actual occurrence location (e.g. GBIF `coordinateUncertaintyInMeters`).

## Geoprivacy

The privacy level assigned by a provider (`open`, `obscured`, `private`). Obscured records use randomized coordinates within a coarse cell (~0.2° × 0.2°) and cannot support precise route-distance claims.

## Recent evidence

Occurrence records close in time to the planned walk (typically from the last 30 days via eBird Recent or iNaturalist APIs). Recent evidence is an empirical report index, not an encounter probability.

## Seasonal evidence

Older historical occurrences weighted according to how close their cyclic week is to the planned walk date ($d_T(w_1, w_2)$).

## Evidence coverage

The density of qualifying observation effort near a location and time. Coverage is not species occurrence probability.

## Observation effort

Where and how intensively people looked. Citizen-science data are strongly biased by observer travel choices.

## Route evidence

The normalized set of biodiversity occurrence reports near a route corridor, maintained as a distinct product layer ("Reports Near This Walk") separate from Habitat Radar and empirical models.

## Evidence ribbon

A subtle visual or text-equivalent timeline representation showing relative occurrence report intensity along a route corridor without scattering raw map points.

## Model–evidence disagreement

A standardized comparison between empirical model predictions and recent/historical evidence ($D_s(x,t) = z(E_s^{\text{recent}}) - z(P_s^{\text{model}})$), used to highlight ecological surprises or data gaps.

## Under-documentation

A measure of locations where Sidetrack predicts high ecological opportunity but observation coverage is low ($U_{\text{gap}}(R)$).

## Duplicate lineage

A provenance record (`duplicate_cluster_id`) linking the same real-world observation imported across multiple platforms (e.g., an iNaturalist research-grade observation exported to GBIF).

## Complete checklist


A structured survey event where the observer indicated that all detected species were reported and effort metadata are available/eligible.

## Non-detection

A zero for a focal taxon on an eligible complete checklist. Absence from a presence-only source is not a non-detection.

## Evidence provenance

Where an evidence record came from, its source ID, date, license/terms, processing, and analytical role.

## Prediction provenance

The model or prior that produced a prediction/score, including version, training data, status, and calibration.

## Relative opportunity score

A ranking/index that is not necessarily a calibrated probability.

## Encounter probability

Estimated probability of observing a taxon under specified route, timing, observer, and effort conditions. This term is reserved for evaluated/calibrated models.

## Ecological presence

Latent suitability or presence state of a species at a location/time, distinct from the chance an observer detects it.

## Detectability

Probability of detecting a species given that it is present and given effort, observer, protocol, habitat, time, and conditions.

## Phenology

Seasonal pattern of presence, abundance, migration, or detectability across the year.

## QBC

Query by Committee. Disagreement among a set of models or bootstrap predictions, used as one uncertainty measure.

## Epistemic uncertainty

Uncertainty caused by limited data or model knowledge, as opposed to inherent randomness.

## Redundancy

Similarity of a candidate observation to existing evidence or other selected route elements.

## Spatial cell

Stable geographic unit used for environmental data, evidence aggregation, prediction, and privacy generalization.

## Environmental schema

Named, ordered set of environmental features including units, sources, vintages, scaling, and buffer methods.

## Candidate location

Potential place/entrance/observation point considered by the route optimizer.

## Route segment

Ordered part of route geometry with consistent navigation or environmental context.

## Corridor value

Ecological opportunity accumulated while moving along a route edge, rather than only at stops.

## Route artifact

Immutable planned result containing request, route geometry, segments, stops, totals, objective, and provenance versions.

## Detour frontier

Relationship between extra travel time and ecological/experiential value for point-to-point trips.

## Pareto route menu

Small set of routes where no option is strictly better on every important dimension.

## Calibration

Agreement between predicted probabilities and observed frequencies on held-out data.

## Historical replay

Evaluation where models train on past data, policies select future candidate observations without seeing outcomes, then outcomes are revealed and performance measured on untouched data.

## Presence-only

Data that record detected presences but do not provide meaningful absences/non-detections.

## Data manifest

Versioned metadata record for a data artifact: source, release, schema, checksum, transformations, intended role, and restrictions.

## Model card

Document describing model purpose, data, features, evaluation, limitations, intended use, and provenance.

## ADR

Architecture Decision Record. A durable record of an important project decision and its consequences.

## Release gate

Explicit criteria that must pass before a sprint or release is considered complete.

## Degraded state

Visible mode where a provider/data/model/media feature is unavailable or provisional. It is never silently presented as normal exact output.

## Quiet mode

User preference disabling optional prompts and audio suggestions while preserving route navigation and text guidance.

## Sensitive taxon

Taxon whose location or targeting is generalized, suppressed, delayed, or excluded to reduce ecological harm.
