import cloudscraper
from flask import Flask
from waitress import serve
import os
import sys

def check_single_instance():
    if os.path.exists(lock_file):
        # Try to remove it. If we can't, another instance is using it.
        try:
            os.remove(lock_file)
        except OSError:
            print("Script is already running! Exiting...")
            sys.exit(0)
    # Create the lock file (first execution)
    global f
    f=open(lock_file, 'w')# Windows won't let another script delete a file that is 'open'

##### RUN ONLY ONCE #####
lock_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scrapMatchData.lock")
check_single_instance()


app = Flask(__name__)
scraper = cloudscraper.create_scraper()
last_match_id = ""

@app.route('/get-stats')
def get_stats():
    global last_match_id
    # The exact URL you were trying to reach
    url = "https://api.tracker.gg/api/v2/valorant/standard/matches/riot/nawakman%2329232?platform=pc&season=4c4b8cff-43eb-13d3-8f14-96b783c90cd2&type=competitive"
  
    response = scraper.get(url)

    ##### RESPONSE #####
    if response.status_code != 200:
        print(f"BLOCKED! Status: {response.status_code}", flush=True)
        print(f"server Response: {response.text[:500]}", flush=True)#log blocking page
        return "server error: connection blockedrt"
    
    ##### JSON #####
    try:   
        data = response.json() # Convert the response to a Python Dictionary
        current_match = data['data']['matches'][0]
        current_id = current_match['attributes']['id']
        result = current_match['metadata']['result'] # e.g., "victory"

        if current_id != last_match_id:
            last_match_id = current_id
            print(f"new match detected",flush=True)
            print(f"sending to ESP32: {result}",flush=True)
            return str(result)
        else:
            return "none" 
    except Exception as e:
        print(e,flush=True)#flush to instantly print the log 
        return "server error: JSON parsing error"
    return "server error: no successful attempts"



if __name__ == '__main__':
    print("launching waitress on http://localhost:5000")
    serve(app, host='0.0.0.0', port=5000)