"""Auth sem dependências externas: hash de senha (pbkdf2) e JWT (HMAC-SHA256)."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time

from radar3d.config import settings

_ITERATIONS = 100_000


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _ITERATIONS)
    return f"{salt.hex()}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, hash_hex = stored.split("$", 1)
    except ValueError:
        return False
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), _ITERATIONS)
    return hmac.compare_digest(dk.hex(), hash_hex)


def _b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def _b64d(seg: str) -> bytes:
    return base64.urlsafe_b64decode(seg + "=" * (-len(seg) % 4))


def _sign(msg: str) -> str:
    return _b64(hmac.new(settings.jwt_secret.encode(), msg.encode(), hashlib.sha256).digest())


def create_token(user_id: str) -> str:
    header = _b64(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    exp = int(time.time()) + settings.jwt_expire_hours * 3600
    body = _b64(json.dumps({"sub": user_id, "exp": exp}).encode())
    msg = f"{header}.{body}"
    return f"{msg}.{_sign(msg)}"


def decode_token(token: str) -> str | None:
    """Retorna o user_id se o token for válido e não expirado; senão None."""
    try:
        header, body, sig = token.split(".")
    except ValueError:
        return None
    if not hmac.compare_digest(sig, _sign(f"{header}.{body}")):
        return None
    try:
        payload = json.loads(_b64d(body))
    except (ValueError, json.JSONDecodeError):
        return None
    if payload.get("exp", 0) < time.time():
        return None
    return payload.get("sub")
