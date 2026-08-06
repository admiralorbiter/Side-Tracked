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

A record that a taxon was reported present. It does not imply a complete checklist or non-detection information.

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
