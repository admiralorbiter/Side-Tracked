# Startup Checklist

Use this checklist to begin Sidetrack in large, deliberate pieces.

---

## 1. Product identity

- [ ] Use **Sidetrack** as the working name.
- [ ] Use **A Field Guide to Getting Sidetracked** as the tagline.
- [ ] Add product tone rules to design/CSS copy notes.
- [ ] Confirm The Easy One, The Birdy One, and conditional The Weird One.
- [ ] Keep OVON named as the research/optimization engine.

## 2. Repository

- [ ] Choose new repository versus monorepo folder.
- [ ] Copy this final documentation set.
- [ ] Add `apps/web`, `packages/ovon_core`, `experiments`, `data`, and `media` directories.
- [ ] Ignore raw addresses, secrets, local databases, restricted data, cached media, and model artifacts unless intentionally versioned.
- [ ] Add project license decision.
- [ ] Add `pyproject.toml`.
- [ ] Add `justfile`.
- [ ] Add changelog/release-note convention.

## 3. Local quality workflow

- [ ] `just format`
- [ ] `just lint`
- [ ] `just typecheck`
- [ ] `just test`
- [ ] `just smoke`
- [ ] `just data-verify`
- [ ] `just media-verify`
- [ ] `just check`
- [ ] Tests run offline with frozen fixtures.
- [ ] No GitHub Actions configuration is added.

## 4. Flask application skeleton

- [ ] Application factory.
- [ ] Extension objects without global binding.
- [ ] Home/planner blueprint.
- [ ] Route blueprint.
- [ ] Species blueprint.
- [ ] Search Lab blueprint placeholder.
- [ ] Admin/manifest blueprint restricted to local/admin use.
- [ ] Base template and error pages.
- [ ] CSS design tokens.
- [ ] One HTMX partial with no-JavaScript fallback.
- [ ] Placeholder map adapter with no ecological business logic.

## 5. Intent-first UI prototype

- [ ] Home asks “How do you want to get sidetracked?”
- [ ] Loop from here is the only required active MVP intent.
- [ ] Origin screen supports address, current location, pin, and public place.
- [ ] Time screen defaults to 45 minutes.
- [ ] Optional preferences are collapsed.
- [ ] Planning state explains stages.
- [ ] Route comparison shows Easy/Birdy/Weird fixtures.
- [ ] Route detail shows field pack before dense map controls.
- [ ] In-route and after-route fixture screens exist.
- [ ] All error/degraded states exist.

## 6. Stable web domain contracts (Sprint 1A)

- [ ] Canonical `TaxonRef` and species code mapping.
- [ ] `Coordinate` and `BoundingBox` with distance validation (disallow `0,0`).
- [ ] `JourneyIntent` Enum and `LoopRequest`.
- [ ] `RouteOption`, `RouteSegment`, and `RouteStopAction`.
- [ ] `MediaAsset` with mandatory license allowlist & attribution enforcement.
- [ ] `FieldCue` and `RouteFieldPack`.
- [ ] Typed domain errors (`InvalidCoordinateError`, `MissingAttributionError`, etc.).
- [ ] Core package imports zero Flask or presentation code.
- [ ] Dataset schemas (`ObservationEvent`, `EnvironmentalVector`, `SpatialCellId`) explicitly deferred to Sprints 5 & 6 (D-017).

## 7. Species media foundation

- [ ] Record media license allowlist ADR.
- [ ] Create media tables and manifest schema.
- [ ] Implement attribution renderer.
- [ ] Implement accessible audio component.
- [ ] Enforce no autoplay and one clip at a time.
- [ ] Implement quiet mode.
- [ ] Add image and audio missing states.
- [ ] Curate first 10–15 common Kansas City species.
- [ ] Add image alt text and sound descriptions.
- [ ] Add where-to-look/listen cues.
- [ ] `just media-verify` passes.

## 8. Privacy

- [ ] Raw address is not persisted.
- [ ] Raw address is not logged.
- [ ] Current-location permission is optional.
- [ ] Share link uses opaque route ID.
- [ ] Session expiration defined.
- [ ] Sensitive-taxon fixture is suppressed/generalized.
- [ ] Unknown accessibility represented as unknown.

## 9. Routing foundation

- [ ] Select native `OSMnx` + `igraph` spatial solver ADR (D-015).
- [ ] Load and cache OpenStreetMap pedestrian graph for Greater KC locally.
- [ ] Matrix, pathfinding, and geometry use same OSM graph snapshot/version.
- [ ] Closed loop returns to origin.
- [ ] Exact route fits time budget.
- [ ] Route total reconciles.
- [ ] Straight-line fallback is never labeled exact.
- [ ] Graph loading failure state renders.

## 10. Regional data package

- [ ] Freeze candidate entrances/locations.
- [ ] Give every candidate a real spatial cell.
- [ ] Attach access/safety status.
- [ ] Attach named environmental vector.
- [ ] Freeze taxonomy.
- [ ] Freeze route graph/version.
- [ ] Separate live occurrence context from model inputs.
- [ ] Add checksums/manifests.
- [ ] Verify deterministic output.

## 11. First release UX gate

- [ ] A first-time user can explain Sidetrack.
- [ ] A user creates a 45-minute loop.
- [ ] Route choices are understandable.
- [ ] Route timeline works without map interaction.
- [ ] Field pack teaches where to look/listen.
- [ ] Images and sounds are attributed.
- [ ] Audio is optional and accessible.
- [ ] No unsupported probability language.
- [ ] No dead future-feature controls.

## 12. Initial ADRs

- [ ] Repository placement.
- [ ] Flask database/repository approach.
- [ ] Map library.
- [ ] Geocoder.
- [ ] Routing deployment.
- [ ] Canonical taxonomy.
- [ ] Spatial grid.
- [ ] Environmental schema v1.
- [ ] Media license allowlist.
- [ ] Sensitive-species policy.
- [ ] Local quality toolchain.

## 13. First usability questions

- [ ] Do people understand the intent-first home?
- [ ] Are Easy/Birdy/Weird clear or too cute?
- [ ] Does the field pack appear at the right time?
- [ ] How many species are useful before overload?
- [ ] Do images and sounds improve preparedness?
- [ ] Are where-to-look/listen cues actionable?
- [ ] Can a person use the route without the map?
- [ ] Are uncertainty and provenance understandable?
- [ ] Does quiet mode feel complete?
- [ ] What happens when media is missing?
