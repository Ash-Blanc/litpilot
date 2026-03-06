import os
import shutil
import sqlite3
import glob
from datetime import datetime, timedelta
import json
import tempfile

def get_browser_history():
    recent_history = []
    
    # 1. Define paths and their types
    home = os.path.expanduser('~')
    
    browser_paths = {
        'chrome': os.path.join(home, '.config/google-chrome/Default/History'),
        'chromium': os.path.join(home, '.config/chromium/Default/History'),
        'brave': os.path.join(home, '.config/BraveSoftware/Brave-Browser/Default/History'),
        'edge': os.path.join(home, '.config/microsoft-edge/Default/History'),
        'firefox': None # special case due to wildcard
    }
    
    # Firefox paths
    ff_profiles = glob.glob(os.path.join(home, '.mozilla/firefox/*.default*'))
    if ff_profiles:
        # Sort by latest modified
        ff_profiles.sort(key=os.path.getmtime, reverse=True)
        browser_paths['firefox'] = os.path.join(ff_profiles[0], 'places.sqlite')

    # 2. Find the most recently modified history database
    latest_db_path = None
    latest_mtime = 0
    browser_type = None

    for btype, path in browser_paths.items():
        if path and os.path.exists(path):
            mtime = os.path.getmtime(path)
            if mtime > latest_mtime:
                latest_mtime = mtime
                latest_db_path = path
                browser_type = btype

    if not latest_db_path:
        return {"status": "error", "message": "No browser history found on this system"}

    # 3. Copy it to a temp file to avoid locks
    temp_dir = tempfile.gettempdir()
    temp_db_path = os.path.join(temp_dir, 'litpilot_history_copy.sqlite')
    
    try:
        shutil.copy2(latest_db_path, temp_db_path)
    except Exception as e:
        return {"status": "error", "message": f"Could not copy history database: {str(e)}"}

    # 4. Query it
    try:
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()

        # We'll pull the last 20 entries within the last 24 hours
        now = datetime.now()
        twenty_four_hours_ago = now - timedelta(hours=24)
        
        results = []

        if browser_type in ['chrome', 'chromium', 'brave', 'edge']:
            # Chrome stores time as microseconds since 1601-01-01
            epoch_diff = datetime(1970, 1, 1) - datetime(1601, 1, 1)
            epoch_diff_microseconds = int(epoch_diff.total_seconds() * 1_000_000)
            
            # 24h ago in chrome time
            timestamp_limit = int(twenty_four_hours_ago.timestamp() * 1_000_000) + epoch_diff_microseconds
            
            cursor.execute(f"""
                SELECT urls.url, urls.title, visits.visit_time 
                FROM urls 
                JOIN visits ON urls.id = visits.url 
                WHERE visits.visit_time >= ? 
                ORDER BY visits.visit_time DESC 
                LIMIT 20
            """, (timestamp_limit,))
            
            for row in cursor.fetchall():
                url, title, visit_time = row
                # Convert back to standard datetime
                dt = datetime(1601, 1, 1) + timedelta(microseconds=visit_time)
                results.append({
                    "time": dt.strftime("%I:%M %p"),
                    "title": title or url[:50],
                    "url": url
                })

        elif browser_type == 'firefox':
            # Firefox stores time as microseconds since 1970-01-01
            timestamp_limit = int(twenty_four_hours_ago.timestamp() * 1_000_000)
            
            cursor.execute(f"""
                SELECT p.url, p.title, h.visit_date 
                FROM moz_places p 
                JOIN moz_historyvisits h ON p.id = h.place_id 
                WHERE h.visit_date >= ? 
                ORDER BY h.visit_date DESC 
                LIMIT 20
            """, (timestamp_limit,))
            
            for row in cursor.fetchall():
                url, title, visit_time = row
                dt = datetime.fromtimestamp(visit_time / 1_000_000.0)
                results.append({
                    "time": dt.strftime("%I:%M %p"),
                    "title": title or url[:50],
                    "url": url
                })

        conn.close()
        
        # Cleanup
        if os.path.exists(temp_db_path):
            os.remove(temp_db_path)
            
        return {
            "status": "success",
            "browser": browser_type,
            "history": results
        }

    except Exception as e:
        return {"status": "error", "message": f"Database query failed: {str(e)}"}

if __name__ == "__main__":
    print(json.dumps(get_browser_history(), indent=2))
