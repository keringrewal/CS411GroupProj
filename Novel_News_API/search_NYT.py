from private import key_store as ks
import requests
import json

def search_NYT():
    api_key = ks.get_nyt_keys()

    url = "https://api.nytimes.com/svc/mostpopular/v2/mostviewed/U.S./1.json"

    r = requests.get(url, headers={'api-key': api_key})

    parsed_json = json.loads(r.text)

    return parsed_json