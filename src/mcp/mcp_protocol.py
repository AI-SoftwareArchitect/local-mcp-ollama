# src/mcp_protocol.py
from dataclasses import dataclass
from typing import Any, Dict, Optional
import json

@dataclass(frozen=True)
class MCPRequest:
    id: str
    tool: str
    input: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

@dataclass(frozen=True)
class MCPResponse:
    id: str
    status: str
    output: Any
    metadata: Optional[Dict[str, Any]] = None

def parse_mcp_request(payload: Dict[str, Any]) -> MCPRequest:
    # pure transformation + validation
    if 'id' not in payload or 'tool' not in payload:
        raise ValueError("invalid mcp request")
    return MCPRequest(
        id=str(payload['id']),
        tool=str(payload['tool']),
        input=payload.get('input', {}),
        metadata=payload.get('metadata')
    )

def to_json_resp(resp: MCPResponse) -> Dict[str, Any]:
    return {
        "id": resp.id,
        "status": resp.status,
        "output": resp.output,
        "metadata": resp.metadata
    }
