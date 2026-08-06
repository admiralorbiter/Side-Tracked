# Privacy, Safety, and Ethics

## Purpose

Sidetrack plans real-world movement and describes living organisms. That creates risks ordinary content sites do not have: exact home locations, physical route hazards, sensitive species, media rights, ecological disturbance, and false confidence.

The application should be useful without requiring an account or permanent location history.

---

# 1. Address and location privacy

## Default rule

Raw addresses are transient. They are used for geocoding and route planning and are not persisted by default.

Do not store raw addresses in:

- route request tables;
- ordinary logs;
- analytics events;
- error reports;
- share links;
- browser local storage.

Store only what is necessary:

- geocoded coordinate for the active request;
- coarse origin cell when needed for caching/analysis;
- short-lived session ID;
- route ID and manifest versions.

## Current location

- permission is optional;
- explain why it is requested;
- provide address/map pin alternatives;
- do not continuously track outside an active route need;
- do not retain a route trace by default.

## Share links

A share link uses an opaque route artifact ID. It must not contain the raw address or a user identity.

---

# 2. Safety and access

Sidetrack cannot guarantee that a route is safe, open, legal, or accessible at all times.

## Access states

```text
verified_public
likely_public
unknown
seasonal
restricted
excluded
```

Unknown is not treated as public.

## Safety states

```text
reviewed
unknown
seasonal_hazard
temporary_issue
excluded
```

## Product behavior

- exclude restricted/excluded candidates;
- display unknowns;
- show daylight or seasonal warnings;
- allow route problem reports;
- avoid absolute safety claims;
- provide a route-ending option;
- distinguish official closures from user reports;
- timestamp access information.

## Accessibility

The application must not infer wheelchair access from the absence of steps data. Accessibility claims include confidence and source.

---

# 3. Sensitive species

## Risks

Precise route guidance can contribute to disturbance, harassment, nest pressure, collection, or location disclosure.

## Controls

- sensitivity flag in canonical taxonomy;
- species/season/region-specific display policy;
- coordinate generalization;
- exclusion from target search;
- delayed or aggregated evidence;
- no exact nesting locations;
- no competitive rare-species mechanics;
- no route explanation that reveals a suppressed point indirectly;
- review of media and field cues for location hints.

## Messaging

Use ethical guidance without lecturing:

> Observe from a respectful distance. Avoid broadcasting calls or approaching nesting birds.

---

# 4. Audio ethics

Bird sounds in Sidetrack are educational references, not tools for attracting wildlife.

- no autoplay;
- encourage headphones or pre-trip listening;
- discourage broadcast playback in habitat;
- stronger warnings for sensitive/breeding species;
- research playback only under explicit approved protocols;
- no repeated prompts to play a call in the field.

---

# 5. Evidence and model ethics

## Source-role separation

- recent occurrence: presence-only context;
- complete checklist: detection/non-detection with effort;
- photo observation: presence-only with media evidence;
- environmental raster: covariate;
- route graph: mobility constraint.

Do not combine these as if they have identical meaning.

## False precision

A relative index is labeled as an index. Probability language requires calibration.

## Geographic bias

Citizen-science evidence reflects access, popularity, observer skill, and platform behavior. The product must not equate low record density with ecological absence.

## Recommendation harms

Avoid repeatedly routing people to the same under-documented site until it becomes overused. Later route policies should account for visitation and disturbance burden.

---

# 6. Media rights and attribution

- media licenses are per asset;
- observation license does not automatically apply to photo/sound;
- creator attribution is visible;
- no all-rights-reserved reuse without permission;
- derivative restrictions honored;
- revocation/unavailability operationally handled;
- audit record retained;
- media provider terms reviewed before production use.

---

# 7. Children, schools, and groups

The MVP does not require profiles for minors.

For future school/group use:

- coordinator-owned sessions;
- minimal participant data;
- no public exact participant locations;
- parental/institutional consent where required;
- group-safe route and access review;
- data retention policy specific to studies.

---

# 8. Research participation

Field Lab studies require:

- clear study purpose;
- voluntary participation;
- consent language appropriate to the study;
- route burden and risk disclosure;
- assignment/randomization transparency where necessary;
- withdrawal process;
- data retention/export/deletion rules;
- ethics review when applicable;
- separation of product analytics from research data.

---

# 9. Data retention

## Anonymous planning session

- raw address: not retained;
- geocoded coordinate: session lifetime or route artifact need;
- coarse cell: permitted for aggregate metrics;
- route artifact: retention defined by product policy;
- audio usage: aggregate event only unless user opts into research;
- feedback: minimal and deletable.

## Accounts later

Exact home address remains unnecessary. Store an approximate home zone or user-chosen public origin.

---

# 10. Transparency panel

Every route can expose:

- route provider/version;
- data window;
- environmental package;
- model/provisional status;
- evidence sources;
- media manifest;
- access data date;
- sensitive-species treatment;
- known limitations.

---

# 11. Incident response

Create a simple documented process for:

- unsafe route report;
- private-property report;
- sensitive-species exposure;
- incorrect media/taxon;
- copyright/license complaint;
- privacy/logging issue;
- model/provenance mislabeling.

A reported blocker can disable a route candidate or media asset without requiring a full release.
