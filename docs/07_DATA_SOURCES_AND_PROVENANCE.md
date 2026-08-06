# Data Sources and Provenance

## Purpose

Sidetrack combines sources with different scientific meaning, spatial precision, licenses, update schedules, and restrictions. A source may be useful for visualization but inappropriate for detection/non-detection modeling.

The application must answer three questions for every value:

1. Where did the data come from?
2. What transformation produced the displayed value?
3. What claims are valid from that source?

---

# 1. Source-role matrix

| Source | Primary role | Can support non-detection? | Public-app concerns |
|---|---|---:|---|
| eBird EBD + SED | Complete-checklist encounter modeling | Yes, after complete-checklist validation and zero filling | Raw-data and derived-product terms |
| eBird recent API | Recent occurrence map | No | API key, rate limits, occurrence-only semantics |
| eBird Status and Trends | Strong prior/range/abundance research layer | Not directly | Web/app and decision-support terms require review/permission |
| GBIF | Presence-only occurrences and source comparison | No | Dataset-specific licenses and coordinate quality |
| iNaturalist | Photo-supported presence-only occurrences | No | Observation licenses, obscured coordinates, attribution |
| OpenStreetMap | Route graph, access, POIs | No | ODbL attribution and data provenance |
| Valhalla | Routing service using OSM/GTFS | N/A | deployment and data freshness |
| KCATA GTFS | Transit schedules and accessibility fields | N/A | feed update and attribution |
| Annual NLCD | Land cover, imperviousness, change | N/A | public-domain data, versioning |
| PAD-US | Protected lands and access context | N/A | access is not guaranteed by polygon membership |
| NWI | Wetland polygons/class | N/A | spatial update and classification |
| NHDPlus | Water and hydrology | N/A | spatial resolution and nearest-feature method |
| Daymet/weather | Weather covariates | N/A | temporal resolution and forecast versus historical distinction |
| BirdCast/NEXRAD | Migration intensity and future dynamic routes | N/A | product terms, temporal/spatial scale |
| Local municipal data | trails, closures, trees, heat, facilities | N/A | jurisdiction-specific quality and update cadence |

---

# 2. eBird

## 2.1 eBird Basic Dataset and Sampling Event Data

The EBD contains observations and the SED contains checklist-level information such as date, location, protocol, duration, distance, observer count, and completeness. The two must be joined by sampling event identifiers.

Use cases:

- complete-checklist detection and non-detection;
- effort-aware encounter models;
- phenology;
- spatial and temporal coverage;
- historical replay;
- observer and protocol effects.

Required processing:

1. freeze a data release;
2. parse named columns, never positional guesses;
3. filter the pilot region and date range;
4. collapse or identify shared checklists;
5. validate complete checklists;
6. filter unreasonable effort;
7. build event and species-outcome tables;
8. zero-fill focal species only on eligible complete checklists;
9. preserve provider IDs and raw taxonomy;
10. retain a transformation manifest.

Do not redistribute raw EBD/SED files.

## 2.2 Recent eBird API

Use only as recent occurrence evidence and map context. The recent-observation endpoint is not a complete-checklist and effort endpoint. Records must remain:

```text
evidence_type = presence_only
```

Do not generate non-detections or checklist coverage from these records.

## 2.3 Status and Trends

Status and Trends products can provide ranges, abundance, and environmental associations and are valuable as internal priors or independent comparison layers.

Before placing these products or derivatives inside a public website, mobile application, or decision-support tool, review the current products terms and request written permission when required.

Recommended early use:

- internal validation;
- model comparison;
- research figures;
- cold-start prior;
- not a public production dependency until terms are resolved.

---

# 3. GBIF

Use cases:

- presence-only occurrence layer;
- habitat analog seed data;
- source-disagreement analysis;
- supplementary historical context;
- public demonstration.

Store:

- GBIF occurrence key;
- dataset key;
- scientific name;
- taxon key;
- event date;
- coordinates;
- coordinate uncertainty;
- basis of record;
- occurrence status;
- license;
- source institution.

Filtering:

- valid coordinates;
- plausible dates;
- appropriate basis of record;
- remove obvious fossil/captive records where relevant;
- inspect coordinate uncertainty;
- preserve flagged records rather than silently accepting them.

GBIF records may originate from eBird. Source-level deduplication is necessary before treating platforms as independent evidence.

---

# 4. iNaturalist

Use cases:

- research-grade photo-supported presence;
- educational images when licenses permit;
- urban and accessible occurrence context;
- platform-disagreement analysis.

Store:

- observation ID;
- taxon ID;
- scientific/common name;
- observed date;
- coordinates;
- positional accuracy;
- quality grade;
- geoprivacy;
- observation license;
- photo license and creator;
- URI.

Obscured or private coordinates must remain obscured. Do not reverse-engineer sensitive locations.

Research-grade is a community-identification state, not proof of a flawless record.

---

# 5. Taxonomy

Create a frozen project taxonomy version and provider crosswalks.

Required fields:

- project taxon ID;
- scientific name;
- common name;
- rank;
- parent;
- provider IDs;
- valid-from/version;
- sensitive status;
- display policy.

Do not use common names as analytical keys.

---

# 6. OpenStreetMap and route data

OpenStreetMap supplies:

- road and path graph;
- access tags;
- surfaces;
- footways;
- crossings;
- bicycle routes;
- parks and POIs;
- benches/restrooms when mapped;
- barriers and steps;
- opening-hours tags.

Limitations:

- missing tags do not mean absence;
- accessibility data may be incomplete;
- public access can change;
- park centroids are not necessarily valid entrances;
- a way is not an observation point.

Maintain OSM attribution and ODbL compliance.

---

# 7. Valhalla

Use Valhalla for:

- pedestrian route geometry;
- time-distance matrices;
- isochrones;
- cycling and driving;
- later multimodal routes;
- elevation and map matching.

The same provider and graph version should generate:

- optimization matrix;
- displayed route;
- route duration;
- directions.

Store the Valhalla graph build/version or data timestamp in route provenance.

---

# 8. Geocoding

The public Nominatim server has strict usage limits, prohibits client-side autocomplete, requires identifying headers and attribution, and asks applications to cache results. It should not be treated as an unrestricted production geocoder.

Options:

- deliberate low-volume compliant use during local development;
- third-party provider;
- self-hosted Nominatim;
- map pin and public-place selection.

Privacy:

- do not submit confidential material to external geocoders;
- do not persist raw user address by default;
- offer map-pin alternatives.

---

# 9. Transit and GTFS

KCATA publishes a GTFS feed. GTFS can provide:

- stops;
- trips;
- stop times;
- routes;
- service calendars;
- wheelchair boarding status;
- wheelchair-accessible trip status;
- pathways where available.

Unknown accessibility fields must remain unknown.

Initial product use:

- known transit-stop origin;
- access to a nature loop;
- later transit plus walking.

Full multimodal routing is not an MVP requirement.

---

# 10. Annual NLCD

The USGS Annual NLCD product suite supplies annual 30-meter land-cover and related products. The current Collection 1.2 release adds 2025 to the time series and includes land cover, change, confidence, fractional impervious surface, impervious descriptor, and spectral change day of year.

Recommended regional extraction:

- one Kansas City GeoTIFF/window per selected product/year;
- common projected CRS;
- point samples and 100/250/500/1000-meter buffer summaries;
- artifact checksum and release ID;
- no hard-coded class values.

Candidate features:

- land-cover class proportions;
- fractional imperviousness;
- land-cover diversity;
- edge density;
- recent land-cover change;
- confidence.

Annual NLCD is public domain, but cite the release.

---

# 11. Water, wetlands, and protected lands

## NWI

Use:

- wetland class;
- distance to wetland;
- percent wetland within buffers;
- wetland diversity.

Do not infer wetland distance from location names.

## NHDPlus

Use:

- distance to river, stream, lake;
- stream order;
- riparian proximity;
- waterbody type.

## PAD-US

Use:

- management agency;
- protection designation;
- public-access metadata where provided;
- distance to protected land.

A protected-area polygon does not guarantee that every location is open, safe, or accessible.

---

# 12. Weather and migration

## Weather

Potential features:

- temperature;
- precipitation;
- wind;
- cloud;
- sunrise/sunset;
- recent rainfall;
- heat index.

Separate historical observations from forecasts.

## BirdCast and NEXRAD

BirdCast uses weather-surveillance radar to describe nocturnal migration. A future dynamic route could combine overnight migration intensity with stopover habitat.

Possible stages:

1. county-level or radar-level migration summary;
2. morning route multiplier;
3. historical validation;
4. raw radar research branch.

Do not imply BirdCast identifies species at neighborhood resolution.

---

# 13. Data pipeline

```text
Raw source
    ↓
Immutable download / API snapshot
    ↓
Schema validation
    ↓
Provider-normalized staging
    ↓
Canonical taxonomy and spatial grid
    ↓
Quality filters
    ↓
Source-aware evidence tables
    ↓
Derived environmental and ecological features
    ↓
Model artifacts
    ↓
Application cache / route request
```

Each arrow is a named transformation with version and parameters.

---

# 14. Proposed regional data package

```text
data/derived/kc_v1/
├── manifest.yaml
├── taxonomy.parquet
├── spatial_cells.parquet
├── candidate_locations.parquet
├── environmental_vectors.parquet
├── occurrence_evidence.parquet
├── complete_checklist_events.parquet
├── complete_checklist_outcomes.parquet
├── route_graph_manifest.json
├── species_models/
├── rasters/
└── reports/
```

Raw restricted files remain in `data/private/` and are ignored by version control.

---

# 15. Update cadence

| Source | Suggested cadence |
|---|---|
| Route graph | quarterly or before regional release |
| GTFS | weekly/monthly check |
| eBird recent | hourly/day cache for display only |
| EBD/SED | monthly or frozen research releases |
| GBIF | monthly snapshot |
| iNaturalist | daily/weekly cache |
| Annual NLCD | annual |
| PAD-US/NWI | on source release |
| species metadata | monthly/quarterly |
| model artifacts | deliberate release, never silent |
| sensitive policy | review each release |

---

# 16. Provenance requirements

Every application route must expose:

- route provider and graph version;
- geocoder provider;
- environmental schema and releases;
- occurrence source states;
- checklist release;
- prediction model;
- calibration state;
- taxonomy version;
- sensitive-location policy version;
- route-generation code version.

---

# 17. Data acceptance gate

A source cannot enter an empirical product layer until:

- license/terms reviewed;
- schema validated;
- provider IDs preserved;
- dates parsed;
- coordinates validated;
- taxonomy normalized;
- source role documented;
- fallback/demo records separated;
- quality report produced;
- sensitive records handled;
- local reproducibility command documented.

---

# 18. Species media sources

Media sources are evaluated separately from biodiversity observation sources. A valid occurrence record does not grant permission to reuse its photograph or sound.

## Source strategy for the first release

| Source | Preferred role | Default handling |
|---|---|---|
| Wikimedia Commons | openly licensed representative images and some audio | retrieve metadata through Wikimedia APIs; cache only with complete attribution and license compliance |
| iNaturalist | supplementary open-licensed photos and sounds tied to observations | accept only assets whose individual media license is compatible; preserve creator and observation link |
| xeno-canto | curated bird songs and calls | use API/approved access patterns; validate the license on each recording; preserve recordist and recording ID |
| Macaulay Library / Cornell Lab | authoritative discovery and deep links | link by default; do not cache or redistribute unless explicit terms or permission allow it |
| Project-curated media | stable MVP pack | use only assets with written permission or a compatible open license |

## License allowlist decision

Before public release, record an ADR defining the allowlist. A conservative product-friendly initial allowlist is:

- CC0;
- CC BY;
- CC BY-SA, with share-alike obligations reviewed and documented;
- public-domain assets whose status has been checked.

Assets containing `NC`, `ND`, custom terms, or all-rights-reserved status require an explicit product/legal decision. Do not assume that a noncommercial prototype will remain noncommercial forever.

## Wikimedia Commons

Use the MediaWiki Action or REST APIs to locate file pages and retrieve:

- canonical file title;
- original and thumbnail URL;
- author/creator;
- license template and URL;
- file description page;
- MIME type and dimensions;
- structured media information when available.

Reuse conditions are attached to each file. The application must retain the author and license information from the file description page. A generic “from Wikimedia” credit is insufficient.

## iNaturalist media

Observation metadata, photographs, and sounds have separate licenses. Store the media-level license rather than copying the observation license.

Required fields:

- observation ID;
- media ID;
- taxon ID;
- creator;
- media URL;
- media license;
- attribution;
- original observation URI;
- retrieval date.

Assets on open-data domains may be easier to reuse, but the license still needs to be recorded and checked. Research Grade is an identification/quality state, not a media license.

## xeno-canto audio

Each recording has a recordist, recording ID, citation form, vocalization type, quality information, and individual Creative Commons license.

For a curated clip, store:

- XC recording ID;
- scientific taxon;
- recordist;
- recording date and region;
- song/call type;
- quality rating when available;
- audio URL or cached path;
- exact license;
- attribution/citation;
- whether editing or excerpting is allowed under that license.

Respect request limits and avoid scraping. Prefer a small reviewed media pack to repeated live searches during route requests.

## Macaulay Library and Cornell media

Treat media discovery and reuse as separate activities. The contributor generally retains copyright, and the Cornell Lab has its own contributor and educational-use arrangements. The MVP should deep-link to authoritative pages unless the project has explicit reuse permission for the chosen asset.

## Media manifest

Every release has a media manifest:

```yaml
media_manifest_id: kc-birds-media-2026-08-v1
created_at: 2026-08-06
license_policy_version: media-policy-v1
assets:
  - taxon_id: taxon:cardinalis-cardinalis
    role: primary_image
    source: wikimedia_commons
    source_asset_id: File:Example.jpg
    creator: Example Creator
    license: CC-BY-4.0
    license_url: https://creativecommons.org/licenses/by/4.0/
    attribution: Example Creator / CC BY 4.0
    cached_path: media/cached/...
    sha256: ...
```

The verification command fails when:

- an asset lacks a creator;
- the license is absent or not allowed;
- attribution is empty;
- a cached file checksum differs;
- the taxon does not exist in the frozen taxonomy;
- a revoked asset remains selected.

# 19. Field-guide content data

Media alone does not tell a user what to do. Sidetrack also maintains versioned field cues:

- visual field marks;
- vocalization description;
- where to look;
- where and when to listen;
- similar species;
- habitat context;
- ethical guidance;
- beginner/advanced variants;
- content source and reviewer.

These cues should begin as a small curated Kansas City bird pack. They are reviewed content artifacts, not generated facts.

# 20. Media accessibility data

For every image:

- informative alt text;
- species name not used as the only description when the image teaches a field mark.

For every sound:

- vocalization type;
- short text description;
- duration;
- user-controlled playback;
- no autoplay;
- optional transcript-like description of non-speech audio.
