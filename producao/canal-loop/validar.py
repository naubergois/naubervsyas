#!/usr/bin/env python3
"""Confere se o loop do canal tem os artefatos obrigatórios."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

REQUIRED = [
    "README.md",
    "brand-profile.md",
    "audience.md",
    "content-pillars.md",
    "social-strategy.md",
    "goals-and-kpis.md",
    "angulos.md",
    "social-seo.md",
    "youtube-seo.md",
    "instagram-seo.md",
    "tiktok-seo.md",
    "geo.md",
    "hashtags.md",
    "perfis.md",
    "calendario.md",
    "republicacao.md",
    "fila.md",
    "experimentos.md",
    "analytics.md",
]


def main() -> int:
    missing = [name for name in REQUIRED if not (ROOT / name).is_file()]
    empty = [
        name
        for name in REQUIRED
        if (ROOT / name).is_file() and (ROOT / name).stat().st_size < 80
    ]
    if missing:
        print("Falta:", ", ".join(missing))
    if empty:
        print("Curto demais (vazio de verdade):", ", ".join(empty))
    if missing or empty:
        return 1
    print(f"OK {len(REQUIRED)} artefatos em {ROOT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
