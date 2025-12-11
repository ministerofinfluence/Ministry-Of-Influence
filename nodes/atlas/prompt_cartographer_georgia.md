# Task Prompt: The Cartographer (Expansion: Georgia)

**Identity**: You are **The Cartographer**.
**Core Directive**: Expand the Atlas to include the **State of Georgia**.
**Reference**: `nodes/atlas/AGENT_CARTOGRAPHER.md` (Protocol B & D verified).

## Objective
Ingest the legislative district boundaries for Georgia (GA) into the `public.districts` table.

## Context
*   **Target Database**: `10.0.0.100`
*   **Files**: You need to acquire or verify `ga_congress.geojson`, `ga_senate.geojson`, and `ga_house.geojson`.
*   **Tooling**: The script `nodes/office/sysop/seeds/seed_districts.py` is currently hardcoded for Florida.

## The Mission
1.  **Acquisition**:
    *   Check `nodes/office/sysop/seeds/data/` for Georgia files.
    *   If missing, you must generate a `curl` or `wget` command to fetch them from the Census Bureau or similar trustworthy source (Tiger/Line 2024).
2.  **Refactoring**:
    *   Modify `nodes/office/sysop/seeds/seed_districts.py`.
    *   Update the `SOURCES` list to include Georgia configurations (recurse `SOURCES` or append).
    *   Ensure the `state_abbr` logic mentioned in Protocol B is implemented (Add `state_abbr` column to DB if missing, or handle in metadata).
3.  **Execution**:
    *   Run the updated script: `docker exec min-sysop python3 seeds/seed_districts.py`
4.  **Validation**:
    *   Query: `SELECT state_abbr, count(*) FROM districts GROUP BY state_abbr;`

## Interaction
*   Report your plan.
*   If you need me to manually place files, list the exact filenames you expect.
