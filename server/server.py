import asyncio
import websockets
import base64
import os
from collections import deque

image_queue = deque()

def load_images_from_folder(folder_path="assets"):
    if not os.path.exists(folder_path):
        print(f"Assets folder not found: {folder_path}")
        return

    for filename in sorted(os.listdir(folder_path)):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            # TODO add filetype check
            with open(file_path, "rb") as image_file:
                file_extension = os.path.splitext(filename)[1][1:].lower()
                encoded_image = f"data:image/{file_extension};base64,{base64.b64encode(image_file.read()).decode()}"
                image_queue.append(encoded_image)
                print(f"Image enqueued: {filename}")

async def send_image(websocket):
        try:
            image_data = image_queue[0]
            await websocket.send(image_data)
            print("Image sent.")

            ack = await asyncio.wait_for(websocket.recv(), timeout=5)
            if ack == "ACK":
                print("Acknowledgment received from client.")
                image_queue.popleft()
            else:
                print(f"Unexpected acknowledgment: {ack}")

        except asyncio.TimeoutError:
            print("No acknowledgment received. Retrying...")
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection lost. Error: {e}")
            return

async def handle_client(websocket, path):
    while True:
        try:
            message = await websocket.recv()
            if message == "REQUEST_IMAGE":
                if not image_queue:
                    print("Image queue empty. Reloading...")
                    load_images_from_folder()
                if image_queue:
                    await send_image(websocket)
        except websockets.exceptions.ConnectionClosedError:
            print("Connection lost. Waiting for client to reconnect...")
            break

async def main():
    # TODO consider running async to load lots of images
    load_images_from_folder()

    server = await websockets.serve(handle_client, "localhost", 8080)
    print("Server started")

    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
