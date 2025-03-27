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

active_websockets = []

@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/start")
async def start_requests(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_requests)
    return {"message": "Process started"}

async def run_requests():
    total_requests = 10
    for i in range(1, total_requests + 1):
        async with httpx.AsyncClient() as client:
            response = await client.get("https://catfact.ninja/fact")
            json_obj = json.loads(response.text)
            response_text = json_obj["fact"]
        
        progress_percentage = int((i / total_requests) * 100)
        for websocket in active_websockets:
            await websocket.send_json({"progress": progress_percentage, "response": response_text})
        await asyncio.sleep(0.1)
        
    for websocket in active_websockets:
        await websocket.close()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_websockets.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        pass
    finally:
        if websocket in active_websockets:
            active_websockets.remove(websocket)

