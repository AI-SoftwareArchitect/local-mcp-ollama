# src/server.py
import uvicorn
from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
import asyncio, json
from src.mcp.mcp_protocol import parse_mcp_request, MCPResponse, to_json_resp
from src.mcp.utils import verify_signature
from src.mcp.worker import tool_to_cmd, run_shell_cmd
from src.mcp.db import init_db, save_request

app = FastAPI()
EVENT_QUEUE = asyncio.Queue()

@app.on_event("startup")
async def startup():
    await init_db()

@app.post("/mcp/call")
async def mcp_call(request: Request, x_signature: str = Header(None)):
    body = await request.body()
    if x_signature is None or not verify_signature(body, x_signature):
        raise HTTPException(status_code=401, detail="invalid signature")
    payload = await request.json()
    req = parse_mcp_request(payload)
    # idempotency check + persist request as 'pending'
    await save_request(req.id, "pending", "", json.dumps(req.metadata or {}))
    # enqueue for worker
    await EVENT_QUEUE.put(req)
    return JSONResponse({"id": req.id, "status": "accepted"})

async def event_generator():
    # SSE generator that yields MCPResponse as events
    while True:
        req = await EVENT_QUEUE.get()
        # synchronous-ish dispatch to worker but not block SSE streaming
        # run in background
        asyncio.create_task(process_request_async(req))
        # notify clients: simple notification (could be per-client filtering)
        yield f"data: {json.dumps({'id': req.id, 'status': 'processing'})}\n\n"

async def process_request_async(req):
    try:
        if req.tool == "shell":
            cmd = tool_to_cmd(req.tool, req.input)
            res = await run_shell_cmd(cmd, timeout=10)
            output = res
        else:
            output = {"error": "unsupported tool"}
        await save_request(req.id, "done", json.dumps(output), json.dumps(req.metadata or {}))
        # broadcast result (in real impl: push to per-client SSE groups)
        # For simplicity we use a global queue
    except Exception as e:
        await save_request(req.id, "error", str(e), json.dumps(req.metadata or {}))

@app.get("/mcp/events")
async def sse_events():
    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    # uvicorn used to serve; uv is package manager, uvicorn is ASGI server
    uvicorn.run("src.server:app", host="0.0.0.0", port=9000, loop="asyncio", ws="none")
