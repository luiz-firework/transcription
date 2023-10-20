import asyncio
import websockets
from websockets.server import serve
import json

CONNECTIONS = set()

async def on_ws_message(websocket):
    CONNECTIONS.add(websocket)

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
                        "status": "connected"
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

def broadcast_transcription(message, is_final):
    payload = {
        "message": message,
        "is_final": is_final
    }
    websockets.broadcast(CONNECTIONS, json.dumps(payload))

async def run_websocket_server():
    server = await serve(on_ws_message, "localhost", 8765)
    await server.wait_closed()

async def main():
    server = await serve(on_ws_message, "localhost", 8765)
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
