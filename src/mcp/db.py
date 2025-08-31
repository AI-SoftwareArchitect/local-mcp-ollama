# src/db.py
import aiosqlite
from typing import Any, Dict

DB_PATH = "mcp_state.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id TEXT PRIMARY KEY,
            status TEXT,
            output TEXT,
            metadata TEXT
        )""")
        await db.commit()

async def save_request(id: str, status: str, output: str, metadata: str):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("BEGIN"):
            await db.execute(
                "INSERT OR REPLACE INTO requests(id,status,output,metadata) VALUES (?,?,?,?)",
                (id, status, output, metadata)
            )
            await db.commit()
