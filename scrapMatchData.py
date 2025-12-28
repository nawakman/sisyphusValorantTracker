import cloudscraper
from flask import Flask, jsonify

app = Flask(__name__)
scraper = cloudscraper.create_scraper() # This mimics a real browser perfectly

last_match_id = ""

@app.route('/get-stats')
def get_stats():
    global last_match_id
    # The exact URL you were trying to reach
    url = "https://api.tracker.gg/api/v2/valorant/standard/matches/riot/nawakman%2329232?platform=pc&season=4c4b8cff-43eb-13d3-8f14-96b783c90cd2&type=competitive"
    
    try:
        response = scraper.get(url)

        if response.status_code != 200:
            print(f"BLOCKED! Status: {response.status_code}", flush=True)
            # This prints the first 200 characters of the block page to your logs
            print(f"Server Response: {response.text[:200]}", flush=True)
            return "server error: connection blocked"

        data = response.json() # Convert the response to a Python Dictionary
        
        # Extract data
        current_match = data['data']['matches'][0]
        current_id = current_match['attributes']['id']
        result = current_match['metadata']['result'] # e.g., "victory"

        if current_id != last_match_id:
            last_match_id = current_id
            print(f"new Match Detected",flush=True)
            print(f"sending to ESP32: {result}",flush=True)
            return str(result)
        else:
            return "none" 
    except Exception as e:
        print(e,flush=True)#flush to instantly print the log 
        return "server error: JSON parsing error"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)