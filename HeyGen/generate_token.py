import json
import urllib.request
import urllib.error
from config import API_KEY, BASE_URL

def generate_session_token(avatar_id, voice_id):
    url = f"{BASE_URL}/v1/sessions/token"
    headers = {
        "X-API-KEY": API_KEY,
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    }
    
    # Payload as per the user's curl example
    # Payload as per the user's curl example
    data = {
        "mode": "FULL",
        "avatar_id": avatar_id,
        "avatar_persona": {
            "voice_id": voice_id,
            "context_id": "3b101576-8373-4664-ad8a-5cab6522c26b",
            "language": "en"
        }
    }
    
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req) as response:
            response_body = response.read().decode('utf-8')
            result = json.loads(response_body)
            print("Session Token Generated Successfully!")
            print(json.dumps(result, indent=2))
            return result
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        error_body = e.read().decode('utf-8')
        print(error_body)
        if e.code == 422:
            print("\n[!] Validation Error: You need to provide a valid 'avatar_id', 'voice_id', and 'context_id'.")
            print("    Please check the IDs in this script.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    # Valid IDs obtained from user and API
    TEST_AVATAR_ID = "0930fd59-c8ad-434d-ad53-b391a1768720" 
    TEST_VOICE_ID = "9c0d4577-2863-4d96-b476-05dcd28878da"
    
    print(f"Attempting to generate token for Avatar: {TEST_AVATAR_ID}, Voice: {TEST_VOICE_ID}")
    generate_session_token(TEST_AVATAR_ID, TEST_VOICE_ID)
