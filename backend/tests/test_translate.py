"""Testes do tradutor por glossário PT->EN (busca + match textual)."""

from radar3d.translate import looks_portuguese
from radar3d.translate.glossary import GlossaryTranslator

t = GlossaryTranslator()


def test_domain_terms():
    out = t.to_english("suporte de controle cabeça de dragão para videogame")
    assert "controller stand" in out
    assert "dragon head" in out
    assert "de" not in out.split()  # preposições descartadas


def test_english_passthrough():
    s = "dragon head controller stand"
    assert t.to_english(s) == s  # já em inglês, não mexe


def test_looks_portuguese():
    assert looks_portuguese("organizador de controles")
    assert not looks_portuguese("controller stand")
