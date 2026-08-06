# Project Decisions and ADRs

## Purpose

This document records accepted direction and identifies decisions that deserve formal Architecture Decision Records.

An ADR is used when a choice is important, difficult to reverse, or likely to be questioned later. It is not required for ordinary implementation detail.

---

# Accepted decisions

## D-001 — Product name

**Decision:** The working product name is **Sidetrack**.  
**Tagline:** **A Field Guide to Getting Sidetracked.**

The public product name is separate from OVON, which remains the research and optimization engine.

## D-002 — Intent-first home

The first screen asks:

> How do you want to get sidetracked?

The MVP implements **Take a loop from here**. Location and time budget follow intent selection.

## D-003 — First-release scope

- Greater Kansas City;
- birds;
- walking loops;
- no account;
- no raw-address retention;
- curated species media pack;
- up to three route choices.

## D-004 — Route names

Public route labels are:

- The Easy One;
- The Birdy One;
- The Weird One when supported.

Technical objective names remain internal. The Weird route is omitted or renamed when the evidence does not support it.

## D-005 — Technology

Use Flask, Jinja, HTMX, HTML/CSS, SQLite, and a small map JavaScript module. Python remains the initial ecological and optimization language. Rust is introduced only after profiling.

## D-006 — Product/core/experiment boundary

- Sidetrack web app depends on stable `ovon_core` contracts.
- Experiments may depend on the core.
- Product code does not import experiment modules.

## D-007 — Media is P0

Representative images, user-controlled bird sounds, attribution, and where-to-look/listen guidance are core field-guide features.

## D-008 — No autoplay

Bird sounds never start automatically. Playback is explicit, accessible, and one clip at a time.

## D-009 — Media license is a required domain field

No displayed/cached media asset is valid without source asset ID, creator, license, attribution, and source URL.

## D-010 — Local-first quality workflow

The project uses `just check` or an equivalent local command for the standard development gate. The project does not adopt GitHub Actions. Any future hosted automation choice requires a new explicit decision.

## D-011 — SQLite first

SQLite is the initial application database. Large raster/model artifacts remain files with manifests. Database migration is considered only when measured needs justify it.

## D-012 — Probability language is gated

Only evaluated/calibrated model output is labeled probability. Provisional outputs use score/index/match language.

## D-013 — Raw addresses are transient

Raw address text is not persisted or logged by default.

## D-014 — Sensitive species protection

Precise public guidance can be suppressed, generalized, delayed, or excluded based on taxon, place, and season.

---

# ADR process

1. Copy `templates/ADR_TEMPLATE.md`.
2. Assign the next number.
3. State context, decision, alternatives, consequences, and review trigger.
4. Mark status: proposed, accepted, superseded, or rejected.
5. Link related code and documents.
6. Update this index.

---

# Initial ADR backlog

## ADR-001 — Repository placement

New repository versus top-level folder in the current repository.

## ADR-002 — Flask data-access approach

SQLAlchemy, SQLModel, raw SQL/repository layer, and migration tool.

## ADR-003 — Map library

Leaflet versus MapLibre, including accessibility and offline considerations.

## ADR-004 — Geocoder

Development and production provider, caching, privacy, and usage policy.

## ADR-005 — Routing deployment

Valhalla local/container/hosted provider and graph update process.

## ADR-006 — Canonical taxonomy

Taxonomy authority/version and provider crosswalk policy.

## ADR-007 — Spatial cell system

Projected grid versus H3 or another index; reproducibility and regional boundaries.

## ADR-008 — Environmental feature schema v1

Feature names, units, scales, buffers, source versions, and missingness.

## ADR-009 — Species media license allowlist

Allowed licenses, NC/SA/ND policy, caching, derivatives, and attribution.

## ADR-010 — Sensitive species display policy

Suppression, aggregation, exceptions, and review ownership.

## ADR-011 — Local quality toolchain

Formatter, linter, type checker, test runner, browser smoke tool, and `just` commands.

## ADR-012 — Route artifact retention

Anonymous route storage, share links, expiration, and deletion.

---

# Decision review triggers

Review a decision when:

- the MVP region expands;
- accounts are introduced;
- the application becomes commercial;
- media licenses become incompatible with intended use;
- SQLite contention or size becomes a measured issue;
- optimization latency becomes a measured bottleneck;
- transit becomes a core mode;
- public field observations are accepted;
- sensitive-species policy changes;
- model output becomes calibrated enough for probability language.
