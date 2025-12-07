import asyncio
from livekit import api

# Your LiveKit Cloud credentials
LIVEKIT_URL = "wss://sadrobot-wlnlb0pv.livekit.cloud"
LIVEKIT_API_KEY = "APIgqwQm9DTGxip"
LIVEKIT_API_SECRET = "8b1YjFS8G6nB2fVQ5hmekxsVJhOyMMDRCRn0JyhrGqfB"

ROOM_NAME = "parker-test-room"
AGENT_NAME = "Parker"

async def main():
    # Create the LiveKit API client
    lk_api = api.LiveKitAPI(
        url=LIVEKIT_URL,
        api_key=LIVEKIT_API_KEY,
        api_secret=LIVEKIT_API_SECRET,
    )
    
    try:
        # Step 1: Create the room
        print(f"Creating room: {ROOM_NAME}")
        room = await lk_api.room.create_room(
            api.CreateRoomRequest(name=ROOM_NAME)
        )
        print(f"✓ Room created: {room.name} (sid: {room.sid})")
        
        # Step 2: Dispatch Parker to the room
        print(f"\nDispatching agent '{AGENT_NAME}' to room...")
        dispatch = await lk_api.agent_dispatch.create_dispatch(
            api.CreateAgentDispatchRequest(
                room=ROOM_NAME,
                agent_name=AGENT_NAME,
            )
        )
        print(f"✓ Agent dispatched: {dispatch}")
        
        # Step 3: Generate a token for you to join
        print("\nGenerating join token for you...")
        token = (
            api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
            .with_identity("test-user")
            .with_name("Test User")
            .with_grants(api.VideoGrants(
                room_join=True,
                room=ROOM_NAME,
                can_publish=True,
                can_subscribe=True,
                can_publish_data=True,
            ))
            .to_jwt()
        )
        
        print(f"✓ Token generated")
        
        # Print the join URL
        print("\n" + "="*60)
        print("SUCCESS! Join the room using this URL:")
        print("="*60)
        print(f"\nhttps://meet.livekit.io/custom?liveKitUrl={LIVEKIT_URL}&token={token}")
        print("\n" + "="*60)
        
        # Also print individual components for HeyGen integration later
        print("\nFor HeyGen Custom Mode integration, you'll need:")
        print(f"  livekit_url: {LIVEKIT_URL}")
        print(f"  livekit_room: {ROOM_NAME}")
        print(f"  livekit_client_token: {token}")
        
    finally:
        await lk_api.aclose()

if __name__ == "__main__":
    asyncio.run(main())