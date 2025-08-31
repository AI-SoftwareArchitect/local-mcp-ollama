# src/utils.py
import hmac, hashlib, os
from typing import Tuple

SECRET = os.getenv("MCP_SHARED_SECRET", "change-me")

def make_signature(message: bytes) -> str:
    return hmac.new(SECRET.encode(), message, hashlib.sha256).hexdigest()

def verify_signature(message: bytes, signature: str) -> bool:
    expected = make_signature(message)
    return hmac.compare_digest(expected, signature)
