import asyncio
import websockets
import base64
import os

async def send_image(websocket, path):
    while True:
        image_path = input("Enter path to image: ")

        if not os.path.exists(image_path):
            print(f"File not found: {image_path}")
            continue

        try:
            with open(image_path, "rb") as image_file:
                file_extension = os.path.splitext(image_path)[1][1:].lower()
                encoded_image = f"data:image/{file_extension};base64,{base64.b64encode(image_file.read()).decode()}"
                await websocket.send(encoded_image)
                print(f"Image sent: {image_path}")
        except Exception as e:
            print(f"Error sending image: {e}")

async def main():
    server = await websockets.serve(send_image, "localhost", 8080)
    print("Server started")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
