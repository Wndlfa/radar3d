"""Faixas de licença e classificação — o diferencial do Radar3D.

Ver docs/regras-de-negocio.md §5. A faixa NUNCA é definitiva: sempre acompanha
`license_checked_at` e a recomendação de conferir na origem.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class LicenseTier(str, Enum):
    """Uma faixa por modelo (exceto a flag de IP, que coexiste)."""

    VENDA_PERMITIDA = "VENDA_PERMITIDA"  # 🟢
    EXIGE_LICENCA = "EXIGE_LICENCA"  # 🟡
    SOMENTE_PESSOAL = "SOMENTE_PESSOAL"  # 🔴
    NAO_IDENTIFICADA = "NAO_IDENTIFICADA"  # ⚪


SEAL = {
    LicenseTier.VENDA_PERMITIDA: "🟢",
    LicenseTier.EXIGE_LICENCA: "🟡",
    LicenseTier.SOMENTE_PESSOAL: "🔴",
    LicenseTier.NAO_IDENTIFICADA: "⚪",
}


@dataclass(frozen=True)
class LicenseVerdict:
    tier: LicenseTier
    possible_protected_ip: bool  # flag ⚠️ (coexiste com qualquer faixa)
    raw: str  # texto original da licença, para a UI
    reason: str  # por que caiu nessa faixa (auditoria)


# Regras determinísticas por plataforma. Começamos auditáveis (sem ML).
# Chaves em minúsculas; casamos por substring no texto de licença bruto.
_PLATFORM_RULES: dict[str, list[tuple[str, LicenseTier]]] = {
    # Nomes reais observados na API: "CULTS CU - Commercial Use",
    # "CULTS PU - Private Use", "CULTS PC - Personal use", etc.
    "cults3d": [
        ("commercial use", LicenseTier.VENDA_PERMITIDA),
        ("cults cu", LicenseTier.VENDA_PERMITIDA),
        ("private use", LicenseTier.SOMENTE_PESSOAL),
        ("personal use", LicenseTier.SOMENTE_PESSOAL),
        ("cults pu", LicenseTier.SOMENTE_PESSOAL),
    ],
    # Thingiverse usa Creative Commons + GPL/BSD. NC proíbe venda; ordem
    # importa (NC é checado antes de "attribution"). Nomes reais tipo
    # "Creative Commons - Attribution - Non-Commercial".
    "thingiverse": [
        ("non-commercial", LicenseTier.SOMENTE_PESSOAL),
        ("noncommercial", LicenseTier.SOMENTE_PESSOAL),
        ("-nc", LicenseTier.SOMENTE_PESSOAL),
        ("all rights reserved", LicenseTier.SOMENTE_PESSOAL),
        ("none", LicenseTier.SOMENTE_PESSOAL),
        ("public domain", LicenseTier.VENDA_PERMITIDA),
        ("cc0", LicenseTier.VENDA_PERMITIDA),
        ("cc-0", LicenseTier.VENDA_PERMITIDA),
        ("attribution", LicenseTier.VENDA_PERMITIDA),
        ("cc-by", LicenseTier.VENDA_PERMITIDA),
        ("gpl", LicenseTier.VENDA_PERMITIDA),
        ("bsd", LicenseTier.VENDA_PERMITIDA),
    ],
    "myminifactory": [
        ("non-commercial", LicenseTier.SOMENTE_PESSOAL),
        ("noncommercial", LicenseTier.SOMENTE_PESSOAL),
        ("commercial use", LicenseTier.VENDA_PERMITIDA),
        ("commercial", LicenseTier.VENDA_PERMITIDA),
        ("attribution", LicenseTier.VENDA_PERMITIDA),
        ("personal", LicenseTier.SOMENTE_PESSOAL),
        ("private", LicenseTier.SOMENTE_PESSOAL),
    ],
}

# Heurística de IP protegido (flag ⚠️). Verifica TÍTULO + descrição + licença
# (personagens/marcas aparecem no nome do modelo, não na licença). É só um
# alerta para revisão — nunca bloqueia. Falso-positivo é aceitável; a lista
# cresce com os dados. Curada para termos distintivos (evita palavras genéricas).
_IP_TERMS = (
    # Pokémon
    "pokemon", "pokémon", "pikachu", "charizard", "lugia", "eevee", "bulbasaur",
    "squirtle", "charmander", "mewtwo", "snorlax", "gengar", "pokeball", "pokébola",
    # Nintendo / Mario / Zelda
    "mario", "luigi", "bowser", "yoshi", "peach", "zelda", "ganon", "kirby",
    "donkey kong", "samus", "metroid", "splatoon", "amiibo",
    # Star Wars
    "star wars", "baby yoda", "grogu", "mandalorian", "darth vader", "yoda",
    "stormtrooper", "lightsaber", "sabre de luz", "r2d2", "bb8", "the child",
    # Marvel / DC
    "marvel", "spider-man", "spiderman", "homem-aranha", "iron man", "homem de ferro",
    "hulk", "thor", "captain america", "venom", "groot", "deadpool", "wolverine",
    "batman", "superman", "coringa", "joker", "harley quinn", "mulher-maravilha",
    # Disney / Pixar
    "disney", "pixar", "mickey", "minnie", "stitch", "elsa", "frozen", "moana",
    "buzz lightyear", "toy story", "simba", "rei leão", "lion king", "baby groot",
    # Anime
    "naruto", "sasuke", "kurama", "goku", "vegeta", "dragon ball", "piccolo",
    "one piece", "luffy", "demon slayer", "tanjiro", "sailor moon", "gundam",
    "totoro", "ghibli", "saint seiya", "cavaleiros do zodíaco",
    # Games
    "sonic", "minecraft", "creeper", "among us", "fortnite", "master chief",
    "halo", "spartan", "kratos", "god of war", "pac-man", "crash bandicoot",
    "lara croft", "overwatch", "league of legends", "valorant", "fnaf",
    # Filmes/TV/brinquedos
    "harry potter", "hogwarts", "hedwig", "star trek", "transformers",
    "optimus prime", "rick and morty", "simpsons", "spongebob", "bob esponja",
    "hello kitty", "sanrio", "baby shark", "peppa pig", "sonic",
    # Marcas
    "nike", "adidas", "ferrari", "lamborghini", "porsche", "lego", "funko",
)

_IP_RE = re.compile(
    r"\b(" + "|".join(re.escape(t) for t in _IP_TERMS) + r")\b", re.IGNORECASE
)


def detect_protected_ip(*texts: str) -> bool:
    """True se algum texto (título/descrição/licença) citar IP possivelmente protegido."""
    blob = " ".join(t for t in texts if t)
    return bool(_IP_RE.search(blob))


def classify_license(
    platform: str, raw_license: str, title: str = "", description: str = ""
) -> LicenseVerdict:
    """Mapeia o texto de licença bruto para uma faixa.

    Regra R6 (fallback conservador): na ausência de match claro => NAO_IDENTIFICADA,
    nunca a faixa mais permissiva. A flag ⚠️ de IP olha título + descrição +
    licença (personagens aparecem no nome, não na licença).
    """
    text = (raw_license or "").strip().lower()
    plat = (platform or "").strip().lower()
    ip_flag = detect_protected_ip(title, description, raw_license)

    if not text:
        return LicenseVerdict(
            tier=LicenseTier.NAO_IDENTIFICADA,
            possible_protected_ip=ip_flag,
            raw=raw_license or "",
            reason="Licença ausente na fonte.",
        )

    # Item pago cuja licença se compra na loja (ex.: MMF Digital File Store
    # License) => exige licença, não "não identificada".
    if "store license" in text or "digital file store" in text:
        return LicenseVerdict(
            tier=LicenseTier.EXIGE_LICENCA,
            possible_protected_ip=ip_flag,
            raw=raw_license,
            reason="Licença de loja: comercialização exige compra/licença.",
        )

    if "subscription" in text or "assinatura" in text or "membership" in text:
        return LicenseVerdict(
            tier=LicenseTier.EXIGE_LICENCA,
            possible_protected_ip=ip_flag,
            raw=raw_license,
            reason="Licença condicionada a assinatura/plano do criador.",
        )

    for needle, tier in _PLATFORM_RULES.get(plat, []):
        if needle in text:
            return LicenseVerdict(
                tier=tier,
                possible_protected_ip=ip_flag,
                raw=raw_license,
                reason=f"Regra '{needle}' da plataforma {plat}.",
            )

    return LicenseVerdict(
        tier=LicenseTier.NAO_IDENTIFICADA,
        possible_protected_ip=ip_flag,
        raw=raw_license,
        reason="Sem regra correspondente — enviar para revisão manual (R6).",
    )
