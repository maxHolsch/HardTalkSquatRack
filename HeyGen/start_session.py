import json
import urllib.request
import urllib.error
from config import BASE_URL

def start_session(session_token):
    url = f"{BASE_URL}/v1/sessions/start"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {session_token}",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    }
    
    try:
        req = urllib.request.Request(url, headers=headers, method='POST')
        with urllib.request.urlopen(req) as response:
            response_body = response.read().decode('utf-8')
            result = json.loads(response_body)
            print("Session Started Successfully!")
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
    # This script expects a session_token to be passed or hardcoded for testing.
    # In a real flow, you'd get this from generate_token.py
    import sys
    
    if len(sys.argv) > 1:
        token = sys.argv[1]
        start_session(token)
    else:
        print("Usage: python3 start_session.py <session_token>")
