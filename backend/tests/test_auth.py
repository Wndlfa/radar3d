"""Testes de segurança (hash de senha e token JWT stdlib) e planos."""

from radar3d.auth.plans import can
from radar3d.auth.security import (
    create_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_hash_roundtrip():
    h = hash_password("senha123")
    assert verify_password("senha123", h)
    assert not verify_password("errada", h)


def test_token_roundtrip():
    tok = create_token("user-abc")
    assert decode_token(tok) == "user-abc"


def test_tampered_token_rejected():
    tok = create_token("user-abc")
    assert decode_token(tok + "x") is None
    assert decode_token("nao.e.jwt") is None


def test_plan_entitlements():
    assert not can("free", "commercial_filter")
    assert can("pro", "commercial_filter")
    assert can("business", "api")
    assert not can("pro", "api")
