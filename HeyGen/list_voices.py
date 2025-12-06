import json
import urllib.request
import urllib.error
from config import API_KEY

# Trying v1 voices on liveavatar.com
LIST_VOICES_URL = "https://api.liveavatar.com/v1/voices"

def list_voices():
    headers = {
        "X-API-KEY": API_KEY,
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    }
    
    try:
        req = urllib.request.Request(LIST_VOICES_URL, headers=headers)
        with urllib.request.urlopen(req) as response:
            response_body = response.read().decode('utf-8')
            result = json.loads(response_body)
            print("Voices listed successfully!")
            
            # Print first few voices to pick one
            if 'data' in result and 'voices' in result['data']:
                voices = result['data']['voices']
                print(f"Found {len(voices)} voices. Showing first 5:")
                for voice in voices[:5]:
                    print(f"ID: {voice.get('voice_id')}, Name: {voice.get('name')}, Language: {voice.get('language')}")
                
                # Return the first one for automatic usage
                if voices:
                    return voices[0].get('voice_id')
            else:
                print(json.dumps(result, indent=2))
            return None
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        print(e.read().decode('utf-8'))
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    list_voices()
