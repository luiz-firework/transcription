import asyncio
from websockets.server import serve
import json

async def handle_client(websocket):
    async for message in websocket:
        try:
            data = json.loads(message)
            topic = data.get("topic")
            event = data.get("event")
            payload = data.get("payload")

            if topic and event and payload:
                if event == "phx_join":
                    # Handle the "phx_join" event
                    domain_assistant_id = payload.get("domain_assistant_id")
                    locale = payload.get("locale")

                    # Your custom handling logic for the "phx_join" event
                    print(f"Received 'phx_join' event:")
                    print(f"Topic: {topic}")
                    print(f"Domain Assistant ID: {domain_assistant_id}")
                    print(f"Locale: {locale}")
                    
                    # Respond to the client if needed
                    response = {
                        "status": "ok"
                    }
                    await websocket.send(json.dumps(response))
                else:
                    # Handle other events as needed
                    pass
            else:
                # Handle invalid or incomplete messages
                pass
        except json.JSONDecodeError:
            # Handle invalid JSON
            pass

async def main():
    async with serve(handle_client, "localhost", 8765):
        await asyncio.Future()  # run forever

asyncio.run(main())
