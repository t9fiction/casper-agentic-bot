import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from .agent import run_agent

app = FastAPI(title="Casper Agentic Bot")

NETWORK = os.getenv("CASPER_NETWORK", "testnet")


class ChatRequest(BaseModel):
    message: str


@app.get("/")
async def index():
    return FileResponse(Path(__file__).parent / "public" / "index.html")


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
