from fastapi import FastAPI, WebSocket, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import httpx
import asyncio
import json

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

active_websockets = {}

@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/start")
async def start_requests(client_id: str):
    print(f"Received start request for client_id: {client_id}")
    return {"message": f"Will start process for client_id: {client_id} when WebSocket is ready"}

async def run_requests(client_id: str):
    total_requests = 10
    websocket = active_websockets.get(client_id)
    if not websocket:
        print(f"WebSocket still not found for client_id: {client_id} - Task will exit.")
        return

    print(f"Starting requests for client_id: {client_id}")
    for i in range(1, total_requests + 1):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get("https://catfact.ninja/fact")
                response.raise_for_status()
                json_obj = response.json()
                response_text = json_obj["fact"]
                print(f"[{client_id}] Request {i}: Received fact - {response_text}")  # Added print
            except httpx.RequestError as e:
                response_text = f"Error fetching fact: {e}"
                print(f"[{client_id}] Request {i}: Error fetching fact - {e}")  # Added print
            except json.JSONDecodeError:
                response_text = "Error decoding JSON response"
                print(f"[{client_id}] Request {i}: Error decoding JSON")  # Added print

        progress_percentage = int((i / total_requests) * 100)
        data_to_send = {"progress": progress_percentage, "response": response_text}
        try:
            await websocket.send_json(data_to_send)
            print(f"[{client_id}] Sent to WebSocket: {data_to_send}")  # Added print
        except Exception as e:
            print(f"[{client_id}] Error sending data to WebSocket: {e}")
            break

        await asyncio.sleep(0.1)

    if client_id in active_websockets:
        try:
            await active_websockets[client_id].close()
            del active_websockets[client_id]
            print(f"WebSocket closed and removed for client_id: {client_id}")
        except Exception as e:
            print(f"Error closing WebSocket for client_id {client_id}: {e}")

    if client_id in active_websockets:
        try:
            await active_websockets[client_id].close()
            del active_websockets[client_id]
            print(f"WebSocket closed and removed for client_id: {client_id}")
        except Exception as e:
            print(f"Error closing WebSocket for client_id {client_id}: {e}")

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    active_websockets[client_id] = websocket
    print(f"WebSocket connected with client_id: {client_id}")
    print(f"Active WebSockets: {active_websockets}")

    asyncio.create_task(run_requests(client_id=client_id))
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received data from client {client_id}: {data}")
    except Exception as e:
        print(f"WebSocket disconnected for client_id {client_id}: {e}")
    finally:
        if client_id in active_websockets:
            del active_websockets[client_id]
            print(f"Removed WebSocket for client_id: {client_id}")