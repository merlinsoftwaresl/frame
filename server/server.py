import asyncio
import websockets
import base64
import os
from collections import deque

image_queue = deque()

def enqueue_image():
    while True:
        image_path = input("Enter path to image: ")
        if not os.path.exists(image_path):
            print(f"File not found: {image_path}")
            continue
        with open(image_path, "rb") as image_file:
            file_extension = os.path.splitext(image_path)[1][1:].lower()
            encoded_image = f"data:image/{file_extension};base64,{base64.b64encode(image_file.read()).decode()}"
            image_queue.append(encoded_image)
            print(f"Image enqueued: {image_path}")

async def send_images(websocket):
    while image_queue:
        try:
            image_data = image_queue[0]
            await websocket.send(image_data)
            print("Image sent.")

            ack = await asyncio.wait_for(websocket.recv(), timeout=5)
            if ack == "ACK":
                print("Acknowledgment received from client.")
                image_queue.popleft()
                break 
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
            await send_images(websocket)
        except websockets.exceptions.ConnectionClosedError:
            print("Connection lost. Waiting for client to reconnect...")
            break

async def main():
    server = await websockets.serve(handle_client, "localhost", 8080)
    print("Server started")

    enqueue_task = asyncio.create_task(asyncio.to_thread(enqueue_image))

    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
