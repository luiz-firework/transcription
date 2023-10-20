import asyncio
import threading
import transcription
import websocket

def main():
    # Run the WebSocket server in a separate thread
    websocket_thread = threading.Thread(target=asyncio.run, args=(websocket.run_websocket_server(),))
    websocket_thread.start()

    # Run the transcription component in the main thread
    transcription.main()

if __name__ == "__main__":
    main()
