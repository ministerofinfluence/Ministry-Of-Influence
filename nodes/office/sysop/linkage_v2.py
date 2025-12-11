
import os
import time
import requests
import psycopg2
from psycopg2.extras import RealDictCursor

# --- Configuration ---
DB_HOST = "10.0.0.100"
DB_USER = "supabase_admin"
DB_PASS = "postgres"
DB_NAME = "postgres"

# Provided by User for api.data.gov / Census
API_KEY = "CNqd5lAxwU7czXb5Kl0nkLlX8QbhJQ8kXeQqWORU"

# Census Geocoder Endpoint (Public)
# Using the key might help if routed through a gateway, but main fix is throttling.
GEOCODER_URL = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        dbname=DB_NAME
    )

def geocode_address(address):
    """
    Geocodes an address using the Census Bureau API.
    Returns (lon, lat) or None.
    """
    params = {
        "address": address,
        "benchmark": "Public_AR_Current",
        "format": "json",
        "key": API_KEY # Attempting to force key usage
    }
    
    try:
        response = requests.get(GEOCODER_URL, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            matches = data.get("result", {}).get("addressMatches", [])
            if matches:
                # Take the first match
                coords = matches[0].get("coordinates", {})
                return coords.get("x"), coords.get("y")
        else:
            print(f"Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"Exception during geocoding: {e}")
    
    return None

def find_district_for_point(conn, lon, lat):
    """
    Finds the district ID containing the point.
    """
    sql = """
        SELECT id FROM districts 
        WHERE ST_Contains(boundary, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
        LIMIT 1;
    """
    with conn.cursor() as cur:
        cur.execute(sql, (lon, lat))
        row = cur.fetchone()
        return row[0] if row else None

def main():
    print("Starting Linkage Protocol V2...")
    conn = get_db_connection()
    
    # 1. Get Unlinked Candidates with Addresses
    fetch_sql = """
        SELECT id, full_name, campaign_headquarters_address 
        FROM candidates 
        WHERE district_id IS NULL 
          AND campaign_headquarters_address IS NOT NULL;
    """
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(fetch_sql)
        candidates = cur.fetchall()
        
    print(f"Found {len(candidates)} candidates to process.")
    
    updates = 0
    errors = 0
    
    for cand in candidates:
        cand_id = cand['id']
        name = cand['full_name']
        addr = cand['campaign_headquarters_address']
        
        print(f"Processing: {name}...")
        
        # Geocode
        coords = geocode_address(addr)
        
        if coords:
            lon, lat = coords
            print(f"  -> Coords: {lon}, {lat}")
            
            # Spatial Join
            district_id = find_district_for_point(conn, lon, lat)
            
            if district_id:
                print(f"  -> Matched District: {district_id}")
                
                # Update DB
                update_sql = "UPDATE candidates SET district_id = %s WHERE id = %s"
                with conn.cursor() as cur:
                    cur.execute(update_sql, (district_id, cand_id))
                    conn.commit()
                updates += 1
            else:
                print("  -> No District Found (Outside bounds?)")
                errors += 1
        else:
            print("  -> Geocoding Failed.")
            errors += 1
            
        # THROTTLE: 2 seconds per request to be safe
        time.sleep(2)
        
    print("---")
    print(f"Linkage Complete. Updates: {updates}, Failures: {errors}")
    conn.close()

if __name__ == "__main__":
    main()
