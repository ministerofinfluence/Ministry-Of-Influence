# Atlas Strategy: The Pure Knowledge Base

**Target**: `10.0.0.100` (VM)
**Tech**: Supabase (Postgres + PostGIS + Vector)
**Role**: **The Ministry's Mind**, not its plumbing.

## 1. The Separation of Powers
**Correction**: The Atlas should **NOT** host the operational databases for tools like n8n or WordPress.
*   **n8n** needs its own internal Postgres (in the Office).
*   **WordPress** needs its own internal MySQL (in the Office).

**Why?**
*   **Decoupling**: If Atlas goes down for maintenance, n8n workflows (that don't touch Atlas) should still run.
*   **Purity**: The Atlas schema remains clean, focused solely on *Influence Data* (`candidates`, `districts`, `vectors`).

## 2. The Atlas Data Model (The Canon)
**Philosophy**: "Supabase-backed Postgres with Escape Hatches."
We use the Supabase features (Auth, API) for speed, but the **Data Schema** must remain portable plain SQL.

### The Ministry Canon rules:
1.  **No Vendor Lock-in Logic**: Do not use Supabase-specific triggers if standard Postgres triggers work.
2.  **API First**: n8n, WP, and Minister App talk to Atlas via REST (`/rest/v1`), not direct DB connection (unless for bulk read).
3.  **One Dashboard to Rule Them All**: Supabase Studio is for *Maintenance*. The Minister App is for *Analysis*. Do not mix them.

## 3. Strategic Analysis (Why V1.0?)
*   **Portability**: Zero Supabase-specific bloat. Migratable to bare metal via `pg_dump`.
*   **Agility**: Usage of `jsonb` for Demographics/Socials allowing API changes without DB migration.
*   **Readiness**: Native `vector(1536)` columns enable immediate "Resonance Checks" via Ollama.

### A. The Geospatial Core (`districts`)
*   **PostGIS Enabled**.
*   Stores Congressional, Senate, House boundaries.
*   Power: "Find all candidates within 50km of Orlando."

### B. The Entity Core (`candidates`)
*   Profiles, Biographies (Vectorized).
*   Social Handles.

### C. The Cortex (`vectors`)
*   All text data (News, Tweets, bios) is embedded here.
*   Ollama queries this to "think."

## 3. Revised Deployment
We only need to deploy the **Supabase Stack** to `10.0.0.100`.
No external `init.sql` scripts for other apps are needed.
