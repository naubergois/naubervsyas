#!/usr/bin/env python3
"""Locução ElevenLabs (pt-BR) para o piloto Caderno de Farol."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, "/Users/naubergois/qclawmonitor/src")

from gois.content.elevenlabs_tts_api import list_voices, resolve_elevenlabs_api_key, synthesize_speech
from gois.env_keys_mongo import apply_env_keys_cache_to_environ

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "audio" / "eleven"

CHUNKS = [
    ("00", "A letra era dela. A data era amanhã."),
    (
        "01",
        "Cora trabalha no farol de Mucuripe. De noite o mar não traz peixe. Traz folha. Gráfico molhado. Pergunta que alguém largou no meio.",
    ),
    ("02", "O regulamento cabe numa linha. Carimba. Guarda. Não lê."),
    (
        "03",
        "Ela carimba até a mão doer. Rascunho, um gato feito das páginas que ela recusou, acompanha o selo.",
    ),
    (
        "04",
        "Uma noite a lâmpada do farol já vinha fraca. Chega uma folha ainda quente. Sem data velha. A letra é a dela. No canto, o carimbo: amanhã.",
    ),
    ("05", "Cora lê um verbete só."),
    ("06", "A cidade apaga em onda. Iracema. O porto. A faixa de prédio."),
    (
        "07",
        "A lâmpada morre. No escuro a página ainda brilha. A última linha não é pergunta. É ordem. Não carimba essa.",
    ),
    (
        "08",
        "De manhã Seu Lino abre a porta do farol. A lâmpada fria. O caderno aberto. Cora sem sombra no chão de aço.",
    ),
    ("09", "Uma folha nova encosta no vidro. Por fora."),
]


def pick_voice() -> tuple[str, str]:
    listed = list_voices()
    if not listed.get("ok"):
        raise SystemExit(listed.get("error") or "falha ao listar vozes")
    voices = listed.get("voices") or []
    scored: list[tuple[int, dict]] = []
    for v in voices:
        blob = " ".join(
            [
                str(v.get("name") or ""),
                str(v.get("accent") or ""),
                str(v.get("description") or ""),
                str(v.get("label") or ""),
            ]
        ).lower()
        score = 0
        if "brazil" in blob or "brasil" in blob or "portuguese" in blob or "portugu" in blob:
            score += 5
        if str(v.get("gender") or "").lower() in {"female", "feminino", "woman"}:
            score += 2
        if "narrat" in blob or "story" in blob or "calm" in blob:
            score += 1
        if score:
            scored.append((score, v))
    scored.sort(key=lambda x: x[0], reverse=True)
    if scored:
        v = scored[0][1]
        return str(v["voice_id"]), str(v.get("label") or v.get("name"))
    # Rachel só se não houver voz pt
    return "21m00Tcm4TlvDq8ikWAM", "Rachel (fallback)"


def main() -> int:
    apply_env_keys_cache_to_environ()
    key = resolve_elevenlabs_api_key()
    if not key:
        print("sem ELEVENLABS_API_KEY no Mongo /chaves")
        return 1
    OUT.mkdir(parents=True, exist_ok=True)
    voice_id, label = pick_voice()
    print(f"voz {label}")
    (OUT / "VOICE.txt").write_text(f"{label}\n{voice_id}\n", encoding="utf-8")
    for cid, text in CHUNKS:
        dest = OUT / f"{cid}.mp3"
        side = dest.with_suffix(".txt")
        if dest.is_file() and side.is_file() and side.read_text(encoding="utf-8") == text:
            print(f"cache {cid}")
            continue
        print(f"tts {cid}")
        res = synthesize_speech(
            text,
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            stability=0.42,
            similarity_boost=0.80,
        )
        if not res.get("ok"):
            print("ERRO", cid, res.get("error"))
            return 2
        audio = res.get("audio_bytes")
        if not isinstance(audio, (bytes, bytearray)):
            print("ERRO sem bytes", cid, list(res.keys()))
            return 2
        dest.write_bytes(audio)
        side.write_text(text, encoding="utf-8")
        print(f"  {dest.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
