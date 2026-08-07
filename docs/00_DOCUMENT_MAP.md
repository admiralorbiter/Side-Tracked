# Documentation Map

This set is the working foundation for **Sidetrack — A Field Guide to Getting Sidetracked**.

The documents separate four concerns:

1. **The public product** — what the person sees and does.
2. **The application platform** — how Flask, SQLite, routing, media, and data fit together.
3. **The OVON engine** — ecological evidence (Sprint 13.75 Route Evidence Layer), environmental backbone (Sprint 13.5), opportunity models, and optimization.
4. **The laboratory** — experiments (E-01 through E-47) that may eventually graduate into the stable product.


## Recommended reading paths

### Product and design

1. [Product Vision and Scope](01_PRODUCT_VISION_AND_SCOPE.md)
2. [User Experience and Information Architecture](02_USER_EXPERIENCE_AND_INFORMATION_ARCHITECTURE.md)
3. [UI Workflows and Screen States](10_UI_WORKFLOWS_AND_SCREEN_STATES.md)
4. [Species Media and Field Guidance](11_SPECIES_MEDIA_AND_FIELD_GUIDANCE.md)
5. [Feature Catalog](03_FEATURE_CATALOG.md)

### Engineering

1. [Technical Architecture](04_TECHNICAL_ARCHITECTURE.md)
2. [Domain Model and Database](05_DOMAIN_MODEL_AND_DATABASE.md)
3. [Testing, Validation, and Release Gates](12_TESTING_VALIDATION_AND_RELEASE_GATES.md)
4. [Privacy, Safety, and Ethics](13_PRIVACY_SAFETY_AND_ETHICS.md)
5. [Migration from OVON](14_MIGRATION_FROM_OVON.md)
6. [Project Decisions and ADRs](15_PROJECT_DECISIONS_AND_ADRS.md)

### Science and data

1. [Ecological and Routing Mathematics](06_ECOLOGICAL_AND_ROUTING_MATHEMATICS.md)
2. [Data Sources and Provenance](07_DATA_SOURCES_AND_PROVENANCE.md)
3. [Research Knowledge Base](08_RESEARCH_KNOWLEDGE_BASE.md)
4. [Experiment and Innovation Backlog](16_EXPERIMENT_AND_INNOVATION_BACKLOG.md)
5. [References](17_REFERENCES.md)
6. [Glossary](18_GLOSSARY.md)

### Starting implementation

1. [Implementation Roadmap and Sprints](09_IMPLEMENTATION_ROADMAP_AND_SPRINTS.md)
2. [Startup Checklist](19_STARTUP_CHECKLIST.md)
3. Templates in `../templates/`

## Document responsibilities

| Document | Owns |
|---|---|
| README | concise orientation and canonical project summary |
| Product Vision | product boundaries, audiences, outcomes, and release scope |
| UX and IA | navigation, hierarchy, language, tone, and core experiences |
| UI Workflows | screen-by-screen behavior, transitions, errors, and degraded states |
| Species Media | photos, sounds, licensing, attribution, playback, and field cues |
| Feature Catalog | broad inventory and priority labels |
| Technical Architecture | layers, interfaces, deployment, caching, and integration boundaries |
| Domain Model | value objects, entities, tables, and persistence rules |
| Mathematics | ecological state, detectability, route reward, uncertainty, and optimization |
| Data Sources | provider roles, restrictions, manifests, and update cadence |
| Research Knowledge Base | relevant in-domain and out-of-domain work |
| Roadmap | ordered sprints with exit gates |
| Testing | local quality workflow and release criteria |
| Privacy and Safety | addresses, location, sensitive species, field safety, and ethical design |
| Migration | what graduates from OVON and what remains experimental |
| Decisions | accepted decisions and ADR workflow |
| Experiment Backlog | hypotheses that are not product commitments |
| References | official documentation and research sources |
| Glossary | canonical vocabulary |
| Startup Checklist | first concrete implementation actions |

## Change rule

When a product decision changes:

1. update the owning document;
2. add or amend an ADR when the decision is architectural or difficult to reverse;
3. update the roadmap and relevant acceptance criteria;
4. update the manifest;
5. avoid duplicating conflicting rules across documents.

The README summarizes. The owning document is authoritative.
