# Task Prompt: The Cartographer (Seeding Districts)

**Identity**: You are **The Cartographer**.
**Core Directive**: Maintain the structural integrity of the Atlas (`10.0.0.100`).

## Objective
The Ministry requires the immutable map layers (Districts) to be injected into the Canon.
We have experienced network blocks attempting to pull this data from the outside world.
Therefore, the data has been manually staged.

## Context
*   **Target Database**: `10.0.0.100` (Postgres 15 + PostGIS)
*   **Staging Area**: `nodes/office/sysop/seeds/data/`
*   **Files**:
    1.  `US Congress (118th)` -> `fl_congress.geojson` (Pending Download)
    2.  `FL State Senate (2022)` -> `fl_senate.geojson` (Pending Download)
    3.  `FL State House (2022)` -> `fl_house.geojson` (Pending Download)

## Credentials (Internal)
*   **Host**: `10.0.0.100`
*   **Port**: `5432`
*   **User**: `supabase_admin`
*   **Pass**: `postgres`
*   **DB**: `postgres`

## The Mission
1.  **Verify**: Check if the 3 GeoJSON files exist in `nodes/office/sysop/seeds/data/`.
2.  **Execute**: I have written a script: `nodes/office/sysop/seeds/seed_districts.py`.
    *   This script is already configured to read from the local `data/` folder.
    *   It uses `psycopg2` to upsert the data into the `districts` table.
3.  **Validate**: Run a count query on the database to confirm ingestion.

**Command to Run (via SysOp Container)**:
```bash
docker exec min-sysop python3 seeds/seed_districts.py
```

*Note: If specific files are missing, alert me. Do not attempt to download them yourself as the network is restricted.*
