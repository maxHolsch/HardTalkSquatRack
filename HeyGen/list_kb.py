import json
import urllib.request
import urllib.error
from config import API_KEY

# Trying liveavatar.com as it seems to be the working domain for this user
LIST_KB_URL = "https://api.liveavatar.com/v1/streaming/knowledge_base/list"

def list_knowledge_bases():
    headers = {
        "X-API-KEY": API_KEY,
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    }
    
    try:
        req = urllib.request.Request(LIST_KB_URL, headers=headers)
        with urllib.request.urlopen(req) as response:
            response_body = response.read().decode('utf-8')
            result = json.loads(response_body)
            print("Knowledge Bases listed successfully!")
            print(json.dumps(result, indent=2))
            return result
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        print(e.read().decode('utf-8'))
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    list_knowledge_bases()
