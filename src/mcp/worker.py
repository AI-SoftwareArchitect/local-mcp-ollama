# src/worker.py
import asyncio
from asyncio.subprocess import create_subprocess_exec, PIPE
from typing import Dict, Any
import json
import shlex
import os

# Pure function to transform tool call into command (decoupled)
def tool_to_cmd(tool: str, input: Dict[str, Any]) -> str:
    # örnek: "shell" tool -> run input["cmd"]
    if tool == "shell":
        cmd = input.get("cmd", "")
        # sanitize / whitelist logic here in caller
        return cmd
    raise NotImplementedError("tool not supported")

async def run_shell_cmd(cmd: str, timeout: int = 10) -> Dict[str, Any]:
    # sandbox: run in subprocess with resource limits if needed (platform dependent)
    proc = await create_subprocess_exec(*shlex.split(cmd), stdout=PIPE, stderr=PIPE)
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return {"rc": proc.returncode, "stdout": stdout.decode()[:20000], "stderr": stderr.decode()[:20000]}
    except asyncio.TimeoutError:
        proc.kill()
        return {"rc": -1, "stdout": "", "stderr": "timed out"}
