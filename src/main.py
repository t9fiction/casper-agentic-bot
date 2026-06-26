import os, asyncio
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from .agent import run_agent
from .monitor import monitor_service

load_dotenv()

app = FastAPI(title="Casper Agentic Bot")

NETWORK = os.getenv("CASPER_NETWORK", "testnet")


class ChatRequest(BaseModel):
    message: str


class MonitorRequest(BaseModel):
    account_hash: str
    label: str = ""
    min_amount_cspr: float = 0


@app.on_event("startup")
async def startup():
    asyncio.create_task(monitor_service.run())


@app.on_event("shutdown")
async def shutdown():
    monitor_service.stop()


@app.get("/")
async def index():
    return FileResponse(Path(__file__).parent / "public" / "index.html")


@app.get("/monitor")
async def monitor_page():
    return FileResponse(Path(__file__).parent / "public" / "monitor.html")


@app.post("/api/chat")
async def chat(req: ChatRequest):
    if not req.message.strip():
        return JSONResponse({"error": "Message is required"}, status_code=400)
    try:
        reply = await run_agent(req.message)
        return {"reply": reply}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/health")
async def health():
    return {"status": "ok", "network": NETWORK}


@app.get("/api/monitors")
async def list_monitors():
    return {"monitors": monitor_service.list_monitors()}


@app.post("/api/monitors")
async def add_monitor(req: MonitorRequest):
    key = monitor_service.add_monitor(req.account_hash, req.label, req.min_amount_cspr)
    return {"monitor_id": key, "status": "active"}


@app.delete("/api/monitors/{monitor_id}")
async def remove_monitor(monitor_id: str):
    monitor_service.remove_monitor(monitor_id)
    return {"status": "removed"}


@app.get("/api/monitors/alerts")
async def get_alerts():
    return {"alerts": monitor_service.get_alerts(clear=True)}
