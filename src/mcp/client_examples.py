# src/client_examples.py
import httpx, json, uuid
from src.mcp.utils import make_signature

MCP_SERVER = "http://127.0.0.1:9000/mcp/call"

def call_mcp(tool: str, input_obj: dict):
    id = str(uuid.uuid4())
    payload = {"id": id, "tool": tool, "input": input_obj}
    b = json.dumps(payload).encode()
    sig = make_signature(b)
    r = httpx.post(MCP_SERVER, content=b, headers={"x-signature": sig, "content-type":"application/json"})
    return r.json()

if __name__ == "__main__":
    print(call_mcp("shell", {"cmd":"echo hello && uname -a"}))
