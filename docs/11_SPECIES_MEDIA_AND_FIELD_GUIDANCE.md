# Species Media and Field Guidance

## Purpose

Photos and sounds are part of Sidetrack's central promise. The product should help someone know:

- what a species looks like;
- what it sounds like;
- where along the route to look;
- where and when to listen;
- what it may be confused with;
- how confident the route guidance is.

This document defines the media strategy, licensing rules, editorial workflow, user experience, accessibility requirements, and MVP media pack.

---

# 1. Product role of media

Sidetrack is not trying to replace a full identification application or build a new recognition model in the MVP.

Media serves four narrower jobs:

1. **Preparation** — create a compact mental image and sound before leaving.
2. **Attention** — tell the person what is relevant in the current habitat segment.
3. **Learning** — connect visual/audio cues with habitat and season.
4. **Reflection** — help the person review what they may have noticed.

More media is not automatically better. The field pack should be small, route-specific, and appropriate to the observer's experience.

---

# 2. MVP content pack

## Initial target

Create a curated pack for 25–50 common or educationally useful Greater Kansas City bird species.

Every supported taxon should aim for:

- one primary representative image;
- one primary song or call recording;
- one alternate call/song when it has clear educational value;
- common and scientific name;
- short field description;
- two or three field marks;
- where to look;
- what to listen for;
- where/when to listen;
- one common confusion species when relevant;
- seasonal status;
- ethical note;
- source/license/creator attribution;
- content version and reviewer.

### Decoupling Scientific Support from Media Completeness

A species being scientifically supported and a species being media-complete are distinct concepts in Sidetrack. The taxonomy catalog and ecological models can know about thousands of species nationwide even if curated photos or audio clips are not yet available for all of them.

```python
@dataclass(frozen=True)
class TaxonSupport:
    taxonomy_known: bool = True
    occurrence_data_available: bool = False
    effort_model_available: bool = False
    calibrated_model_available: bool = False
    field_cue_reviewed: bool = False
    photo_available: bool = False
    audio_available: bool = False
    sensitive: bool = False
```

Example: **Black-billed Cuckoo** — taxonomically known, occurrence-supported, provisional ecological guidance, but no approved audio clip yet. The system includes the species in ecological scoring rather than excluding it.

### Region and Season Aware Field Cues

Field cues are structured via `FieldCueProfile` and attached by region, season, and target audience rather than static global text.

```python
@dataclass(frozen=True)
class FieldCueProfile:
    taxon_id: str  # Sidetrack UUID
    region_scope: str  # e.g., "US-MO-KC", "US-CO"
    season_scope: str  # e.g., "spring_migration", "breeding", "all_year"
    audience: str  # e.g., "beginner", "intermediate"
    where_to_look: str
    listen_for: str
    confusion_taxa: tuple[str, ...]
    source: str
    reviewer: str
    version: str
```


Prioritize species that are:

- common enough to produce rewarding experiences;
- distinctive visually or acoustically;
- associated with different route habitats;
- seasonally informative;
- appropriate for beginners;
- available under usable media licenses;
- not sensitive in a way that makes route targeting harmful.

---

# 3. Media source hierarchy

## 3.1 Wikimedia Commons

Preferred for openly licensed representative images and some audio.

Advantages:

- broad reuse-friendly collection;
- structured file pages;
- individual license and author information;
- API access;
- stable identifiers.

Requirements:

- verify every file's license;
- store the file description page;
- credit the creator, not merely the uploader or Wikimedia;
- honor share-alike and other conditions;
- record retrieval and verification dates;
- do not assume metadata is infallible.

## 3.2 iNaturalist

Useful for supplementary open-licensed images and sounds connected to real observations.

Important rule:

> Observation data, photos, and sounds can have different licenses.

Requirements:

- use the media-level license;
- store observation and media IDs;
- store creator and original URI;
- do not use all-rights-reserved media;
- do not equate Research Grade with reuse permission;
- preserve obscured-location handling;
- avoid relying on a transient image URL without source metadata.

## 3.3 xeno-canto

Useful for curated bird calls and songs.

Requirements:

- use approved API/access patterns;
- preserve XC recording ID and recordist;
- store the individual recording license;
- identify song/call type and region;
- avoid unidentified or disputed recordings in the primary pack;
- document whether cropping or editing is allowed;
- do not scrape the collection;
- use a small curated pack rather than request-time searching.

## 3.4 Macaulay Library / Cornell Lab

Useful as an authoritative external reference and discovery source.

Default policy:

- deep-link to source pages;
- do not cache or redistribute media unless explicit terms or permission support that use;
- do not infer public reuse rights merely because media is viewable online.

## 3.5 Project-owned or permissioned media

The most stable long-term option may be a small pack donated or licensed directly to the project.

Store:

- contributor agreement or permission record;
- allowed uses;
- attribution preference;
- modification permission;
- expiration/revocation terms when applicable.

---

# 4. License policy

## 4.1 Per-asset validation

Every displayed or cached media asset requires:

- source name;
- source asset ID;
- original source URL;
- creator;
- license code;
- license URL;
- attribution text;
- retrieval date;
- status.

No asset is accepted on the basis of a provider-level assumption.

## 4.2 Conservative public allowlist

Record the final decision in an ADR. A conservative starting set is:

- CC0;
- public domain;
- CC BY;
- CC BY-SA after documenting share-alike implications.

CC BY-NC, CC BY-ND, custom licenses, and all-rights-reserved assets require an explicit decision or direct permission.

The initial prototype may be noncommercial, but the data model should not make future product options dependent on a large corpus of noncommercial-only assets without a deliberate choice.

## 4.3 Derivatives

Potential transformations include:

- image thumbnailing;
- crop/resize;
- audio normalization;
- audio excerpting;
- format conversion;
- sonogram creation.

Store each transformation. Do not create derivatives when the license forbids them. An unmodified embed or source link may have different conditions from a cached edited asset.

## 4.4 Revocation and change

Open licenses generally cannot be retroactively revoked for copies already used under those terms, but source availability and metadata can change. The product still needs an operational policy:

- reverify assets on a schedule;
- disable assets whose status is uncertain;
- preserve an audit record;
- update taxon selections without changing old route facts silently;
- identify the media manifest used by each route artifact.

---

# 5. Media domain model

## MediaAsset

```python
@dataclass(frozen=True)
class MediaAsset:
    media_asset_id: str
    taxon_id: str
    media_type: Literal["image", "audio", "sonogram"]
    role: Literal[
        "primary_image",
        "alternate_image",
        "primary_song",
        "primary_call",
        "alternate_audio",
        "sonogram",
    ]
    source_name: str
    source_asset_id: str
    original_url: str
    creator_name: str
    license_code: str
    license_url: str
    attribution_text: str
    mime_type: str | None
    duration_seconds: float | None
    cached_path: str | None
    checksum_sha256: str | None
    retrieved_at: datetime
    verified_at: datetime
    status: Literal["active", "unavailable", "replaced", "revoked"]
```

## AudioMetadata

```python
@dataclass(frozen=True)
class AudioMetadata:
    media_asset_id: str
    vocalization_type: Literal[
        "song", "call", "alarm", "flight_call", "drumming", "other"
    ]
    sex: str | None
    life_stage: str | None
    region: str | None
    recording_date: date | None
    quality_label: str | None
    duration_seconds: float
    sound_description: str
```

## FieldCue

```python
@dataclass(frozen=True)
class FieldCue:
    taxon_id: str
    audience: Literal["beginner", "intermediate", "advanced"]
    look_for: tuple[str, ...]
    where_to_look: str | None
    listen_for: str | None
    where_to_listen: str | None
    confusion_taxon_ids: tuple[str, ...]
    ethics_note: str | None
    source: str
    reviewer: str | None
    version: str
```

---

# 6. Editorial selection

Algorithms may find candidate media, but primary field-guide assets require editorial selection.

## Image criteria

- correctly identified taxon;
- representative field appearance;
- useful crop at small size;
- no misleading captive/domestic context unless labeled;
- reasonable background;
- age/sex noted when not generally representative;
- geographic relevance preferred but not required;
- valid license and attribution.

## Audio criteria

- accepted identification;
- clear focal species;
- useful vocalization type;
- moderate length;
- minimal confusing background species for beginner clips;
- regionally appropriate when calls vary;
- no playback artifacts that create a misleading example;
- valid license and attribution.

## Content review

Every focal species should have a checklist:

```text
[ ] taxon identity verified
[ ] image license verified
[ ] audio license verified
[ ] creator attribution verified
[ ] field marks reviewed
[ ] sound description reviewed
[ ] where-to-look/listen cue reviewed
[ ] confusion species reviewed
[ ] sensitive-species note reviewed
[ ] beginner readability reviewed
```

---

# 7. User interface requirements

## Species card

Order:

1. image;
2. common/scientific name;
3. route/segment relevance;
4. field marks;
5. where to look;
6. audio control;
7. sound description;
8. where to listen;
9. confusion species;
10. source/credit/license.

## Audio interaction

- no autoplay;
- only one clip plays at a time;
- play/pause/stop controls;
- accessible label includes species and clip type;
- show duration;
- preload metadata or nothing;
- quiet mode;
- no use of audio as a required navigation signal;
- no repeated prompting after the user declines audio.

## Image interaction

- meaningful alt text;
- do not embed the species name in an image as the only text label;
- image opens a larger view only when useful;
- source and attribution remain accessible;
- low-bandwidth mode uses thumbnails or placeholders.

## Field cue wording

Good:

> Look low in dense shrubs along the creek edge.

> Listen for a repeated clear whistle; this species is often heard before seen.

Avoid:

> Search optimal habitat coordinates.

> Guaranteed near stop 3.

---

# 8. Route and segment selection

A route may contain dozens of plausible species. The field pack needs ranking and diversity rules.

## Pack selection goals

- likely/common species to create rewarding recognition;
- one or two species that teach habitat differences;
- a mix of visual and auditory opportunities;
- no more than the audience can reasonably absorb;
- avoid duplicate cues that teach the same thing;
- one plausible surprise separated from likely species;
- exclude sensitive targets when precise guidance is inappropriate.

## Example heuristic

```text
score =
    route_relevance
  + educational_distinctiveness
  + media_completeness
  + beginner_suitability
  + habitat_representation
  - cognitive_overlap
  - sensitivity_penalty
```

This score selects field-guide content. It does not change ecological encounter probability.

---

# 9. Ethical audio guidance

The app's audio is for learning and personal reference. It should not encourage broadcasting recordings to attract or provoke birds.

Field guidance should say, when appropriate:

> Use headphones or listen quietly before the route. Avoid broadcasting calls in habitat, especially during nesting season or around sensitive species.

Research playback belongs in an approved Field Lab protocol and is not a general consumer feature.

---

# 10. Accessibility

- no autoplay;
- visible audio controls;
- keyboard operable;
- sound description available in text;
- informative image alt text;
- high-contrast focus;
- quiet mode;
- no essential information available only through sound or color;
- field pack printable/readable without media;
- large touch targets;
- audio player tested with screen readers.

---

# 11. Caching and offline use

## MVP

- cache only reviewed assets with compatible terms;
- use thumbnails for route results;
- load audio on demand;
- preserve a manifest and checksum;
- allow text-only operation.

## Later route pack

A user may choose **Save field guide for this route**. The offline pack contains:

- route summary;
- route timeline;
- selected images;
- selected audio clips;
- field cues;
- attribution page;
- manifest version.

The offline package must honor the same licenses as the online version.

---

# 12. Missing and degraded states

## No image

Show a consistent silhouette/placeholder and the full text field cue.

## No audio

Show the sound description and a source link when permitted.

## License uncertain

Do not display or cache the asset.

## Source unavailable

Use the cached asset only if the license and caching policy permit it and the manifest is valid.

## Taxon mismatch

Quarantine the asset; do not guess based on common-name text.

---

# 13. Verification command

`just media-verify` should check:

- file existence and checksum;
- taxon identity exists;
- source asset ID uniqueness;
- required metadata;
- allowed license;
- attribution text;
- original URL;
- MIME type;
- duration for audio;
- image dimensions;
- no revoked asset selected;
- every supported field-pack taxon has a valid fallback state;
- no audio autoplay in template smoke checks.

---

# 14. MVP acceptance gate

The species media foundation is ready when:

- at least 10–15 common focal species have reviewed cards;
- every displayed image and sound has visible attribution;
- each sound has a text description;
- no clip starts automatically;
- quiet mode works;
- one clip at a time is enforced;
- missing media does not break a route;
- license verification passes locally;
- media/source version appears in route provenance;
- the field pack is understandable in a short beginner usability review.
