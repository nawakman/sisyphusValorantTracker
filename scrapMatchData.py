import cloudscraper
from flask import Flask, jsonify
from fp.fp import FreeProxy

def get_new_proxy():
    """Finds a fresh free proxy that supports HTTPS."""
    try:
        # 'https=True' is vital because Tracker.gg is an HTTPS site
        return FreeProxy(https=True, anonym=True).get()
    except Exception as e:
        print(f"Proxy retrieval failed: {e}", flush=True)
        return None

app = Flask(__name__)
scraper = cloudscraper.create_scraper()
current_proxy = get_new_proxy()#cloudflare blocks render.com
#scraper = cloudscraper.create_scraper(interpreter='js2py')
last_match_id = ""

@app.route('/get-stats')
def get_stats():
    global last_match_id
    # The exact URL you were trying to reach
    url = "https://api.tracker.gg/api/v2/valorant/standard/matches/riot/nawakman%2329232?platform=pc&season=4c4b8cff-43eb-13d3-8f14-96b783c90cd2&type=competitive"

    # Try up to 3 different proxies if we get blocked
    for attempt in range(3):
        ##### PROXY #####
        try:
            proxy_dict = {"http": current_proxy, "https": current_proxy} if current_proxy else None            
            response = scraper.get(url, proxies=proxy_dict, timeout=15)
        except Exception as e:
            print(f"Error with proxy: {e}", flush=True)
            print(f"attempt with new proxy", flush=True)
            current_proxy = get_new_proxy()
            continue

        ##### RESPONSE #####
        if response.status_code != 200:
            print(f"BLOCKED! Status: {response.status_code}", flush=True)
            print(f"server Response: {response.text[:500]}", flush=True)#log blocking page
            print(f"attempt with new proxy", flush=True)
            current_proxy = get_new_proxy()
            continue
        
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
    app.run(host='0.0.0.0', port=5000)