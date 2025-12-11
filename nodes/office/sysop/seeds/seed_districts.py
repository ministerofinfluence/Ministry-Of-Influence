import requests
import psycopg2
import json
import os

# Configuration
DB_HOST = "10.0.0.100"
DB_NAME = "postgres"
DB_USER = "supabase_admin"
DB_PASS = "postgres"
DB_PORT = "5432"

SOURCES = [
    {
        "type": "state_senate",
        "name": "FL State Senate (2022)",
        "filename": "fl_senate.geojson",
        "name_field": "District", 
        "id_field": "District"
    },
    {
        "type": "state_house",
        "name": "FL State House (2022)",
        "filename": "fl_house.geojson",
        "name_field": "DISTRICT", 
        "id_field": "DISTRICT"
    }
]

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )

def seed_districts():
    conn = get_db_connection()
    cur = conn.cursor()
    
    print(f"Connected to Atlas ({DB_HOST})")

    for source in SOURCES:
        print(f"Processing {source['name']}...")
        try:
            # check for local file first
            # The Dockerfile copies . to /app, so data/ is at /app/seeds/data/
            # and this script is at /app/seeds/seed_districts.py
            # So data is at ./data relative to this script
            
            local_path = os.path.join(os.path.dirname(__file__), "data", source['filename'])
            
            if os.path.exists(local_path):
                print(f"Loading local file: {local_path}")
                with open(local_path, "r") as f:
                    data = json.load(f)
            else:
                 print(f"File not found: {local_path}. Skipping.")
                 continue

            features = data.get("features", [])
            print(f"Found {len(features)} features.")
            
            for feat in features:
                props = feat["properties"]
                # Normalize Name
                # For Congress: BASENAME="1" -> "FL-1"
                # For State: DISTRICT="1" -> "SD-1" or "HD-1"
                
                raw_id = str(props.get(source['name_field'], "0"))
                
                if source["type"] == "federal_house":
                    district_name = f"FL-{raw_id}"
                    display_name = f"Congressional District {raw_id}"
                elif source["type"] == "state_senate":
                    district_name = f"SD-{raw_id}"
                    display_name = f"State Senate District {raw_id}"
                elif source["type"] == "state_house":
                    district_name = f"HD-{raw_id}"
                    display_name = f"State House District {raw_id}"
                
                geom = json.dumps(feat["geometry"])
                
                # UPSERT
                cur.execute("""
                    INSERT INTO districts (name, type, boundary, meta)
                    VALUES (%s, %s, ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326), %s)
                    ON CONFLICT (name) DO UPDATE
                    SET boundary = EXCLUDED.boundary, meta = EXCLUDED.meta
                    RETURNING id;
                """, (
                    district_name,
                    source["type"],
                    geom,
                    json.dumps(props)
                ))
            
            conn.commit()
            print(f"Committed {source['name']}.")
            
        except Exception as e:
            print(f"Error processing {source['name']}: {e}")
            conn.rollback()
    
    cur.close()
    conn.close()
    print("Seeding Complete.")

if __name__ == "__main__":
    seed_districts()
