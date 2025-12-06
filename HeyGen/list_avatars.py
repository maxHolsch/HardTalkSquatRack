import json
import urllib.request
import urllib.error
from config import API_KEY

# Using api.liveavatar.com to match the user's guide, hoping it has the same endpoints
LIST_URL = "https://api.liveavatar.com/v1/streaming/avatar.list"

def list_avatars():
    headers = {
        "X-API-KEY": API_KEY,
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    }
    
    try:
        req = urllib.request.Request(LIST_URL, headers=headers)
        with urllib.request.urlopen(req) as response:
            response_body = response.read().decode('utf-8')
            result = json.loads(response_body)
            print("Avatars listed successfully!")
            # Print first few to avoid spam
            if 'data' in result and 'avatars' in result['data']:
                for avatar in result['data']['avatars'][:5]:
                    print(f"ID: {avatar.get('avatar_id')}, Name: {avatar.get('avatar_name')}")
            else:
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
    list_avatars()
