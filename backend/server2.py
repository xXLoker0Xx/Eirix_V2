import asyncio
import websockets
import base64
from PIL import Image
from io import BytesIO
import os
import json

# Directorio donde se guardarán las imágenes
SAVE_DIR = "received_frames"
os.makedirs(SAVE_DIR, exist_ok=True)

# Manejo de conexión WebSocket
async def handle_connection(websocket):
    print("Client connected")
    try:
        while True:
            message = await websocket.recv()
            print(f"Received message: {message}")
            try:
                data = json.loads(message)

                # Procesar imagen si existe
                if "frame" in data:
                    print("Processing frame...")
                    process_frame(data["frame"])
                else:
                    print("No 'frame' key found in the message")
            except Exception as e:
                print(f"Error processing message: {e}")
    except websockets.ConnectionClosed as e:
        print(f"Client disconnected: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Procesar la imagen base64 y guardarla
def process_frame(frame_data):
    try:
        # Decodificar base64
        image_data = base64.b64decode(frame_data)
        image = Image.open(BytesIO(image_data))

        # Guardar imagen como archivo
        frame_number = len(os.listdir(SAVE_DIR))
        filename = f"{SAVE_DIR}/frame_{frame_number}.jpg"
        image.save(filename)
        print(f"Saved frame: {filename}")
    except Exception as e:
        print(f"Error processing frame: {e}")

# Iniciar servidor WebSocket
async def main():
    print("Hola")
    server = await websockets.serve(
        handle_connection, "0.0.0.0", 8000, ping_interval=20, ping_timeout=20, max_size=5 * 1024 * 1024)
    print("WebSocket server started on ws://0.0.0.0:8000")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
