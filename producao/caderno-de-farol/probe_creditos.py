#!/usr/bin/env python3
"""Sonda saldo de provedores I2V. Nunca imprime chave."""
from __future__ import annotations

import json
import sys
import time

import httpx

sys.path.insert(0, "/Users/naubergois/qclawmonitor/src")

from gois.env_keys_mongo import apply_env_keys_cache_to_environ, get_cached_env_keys
from gois.integrations.api_credits import resolve_env_key
from gois.content.local_image_keys import usable_secret

VIDEO_KEYS = [
    "CIVITAI_API_TOKEN",
    "CIVITAI_API_KEY",
    "FAL_KEY",
    "FAL_API_KEY",
    "REPLICATE_API_TOKEN",
    "REPLICATE_API_KEY",
    "RUNWAYML_API_SECRET",
    "RUNWAY_API_KEY",
    "KLING_ACCESS_KEY",
    "KLING_SECRET_KEY",
    "KLING_API_KEY",
    "KLINGAI_API_KEY",
    "ACEDATACLOUD_API_TOKEN",
    "WAVESPEED_API_KEY",
    "LUMA_API_KEY",
    "LUMAAI_API_KEY",
    "HEYGEN_API_KEY",
    "COMFY_API_KEY",
    "COMFYUI_API_KEY",
    "RUNCOMFY_API_KEY",
    "MINIMAX_API_KEY",
    "PIKA_API_KEY",
]


def has(name: str) -> bool:
    return bool(usable_secret(resolve_env_key(name)))


def get(name: str) -> str:
    return usable_secret(resolve_env_key(name))


def probe_civitai() -> dict:
    tok = get("CIVITAI_API_TOKEN") or get("CIVITAI_API_KEY")
    if not tok:
        return {"ok": False, "reason": "sem chave"}
    out = {"ok": True, "user": None, "buzz": None}
    with httpx.Client(timeout=25.0) as c:
        me = c.get("https://civitai.com/api/v1/me", headers={"Authorization": f"Bearer {tok}"})
        if me.status_code == 200:
            d = me.json()
            out["user"] = d.get("username")
            out["buzzLimit"] = d.get("buzzLimit")
        else:
            out["me_status"] = me.status_code
        for url in (
            "https://civitai.com/api/v1/user/buzz",
            "https://orchestration.civitai.com/v2/consumer/account",
        ):
            r = c.get(url, headers={"Authorization": f"Bearer {tok}"})
            if r.status_code == 200:
                try:
                    out["buzz"] = r.json()
                except Exception:
                    out["buzz_raw"] = r.text[:200]
                break
            out.setdefault("buzz_tries", []).append(r.status_code)
    return out


def probe_fal() -> dict:
    key = get("FAL_KEY") or get("FAL_API_KEY")
    if not key:
        return {"ok": False, "reason": "sem chave"}
    with httpx.Client(timeout=20.0) as c:
        r = c.post(
            "https://queue.fal.run/fal-ai/ltx-video/image-to-video",
            headers={"Authorization": f"Key {key}", "Content-Type": "application/json"},
            json={"prompt": "probe"},
        )
        # 403 exhausted / 422 missing image still proves auth+billing
        return {"ok": r.status_code not in {401, 403}, "http": r.status_code, "body": r.text[:180]}


def probe_replicate() -> dict:
    tok = get("REPLICATE_API_TOKEN") or get("REPLICATE_API_KEY")
    if not tok:
        return {"ok": False, "reason": "sem chave"}
    with httpx.Client(timeout=20.0) as c:
        r = c.get(
            "https://api.replicate.com/v1/account",
            headers={"Authorization": f"Bearer {tok}"},
        )
        if r.status_code != 200:
            return {"ok": False, "http": r.status_code, "body": r.text[:180]}
        d = r.json()
        return {
            "ok": True,
            "username": d.get("username") or (d.get("github") or {}).get("login"),
            "type": d.get("type"),
            "keys": list(d.keys())[:12],
        }


def probe_runway() -> dict:
    tok = get("RUNWAYML_API_SECRET") or get("RUNWAY_API_KEY")
    if not tok:
        return {"ok": False, "reason": "sem chave"}
    headers = {
        "Authorization": f"Bearer {tok}",
        "X-Runway-Version": "2024-11-06",
    }
    with httpx.Client(timeout=20.0) as c:
        results = {}
        for url in (
            "https://api.dev.runwayml.com/v1/organization",
            "https://api.runwayml.com/v1/organization",
        ):
            r = c.get(url, headers=headers)
            results[url.split("/")[2] + url.rsplit("/", 1)[-1]] = {
                "http": r.status_code,
                "body": r.text[:220],
            }
        return {"ok": any(v["http"] == 200 for v in results.values()), "tries": results}


def probe_kling() -> dict:
    access = get("KLING_ACCESS_KEY")
    secret = get("KLING_SECRET_KEY")
    bearer = get("KLING_API_KEY") or get("KLINGAI_API_KEY")
    if not ((access and secret) or bearer):
        return {"ok": False, "reason": "sem chave"}
    headers = {"Content-Type": "application/json"}
    if access and secret:
        import jwt

        token = jwt.encode(
            {
                "iss": access,
                "exp": int(time.time()) + 1800,
                "nbf": int(time.time()) - 5,
            },
            secret,
            algorithm="HS256",
        )
        headers["Authorization"] = f"Bearer {token}"
    else:
        headers["Authorization"] = f"Bearer {bearer}"
    with httpx.Client(timeout=20.0) as c:
        tries = {}
        for url in (
            "https://api.klingai.com/v1/account",
            "https://api.kling.ai/v1/account",
            "https://api.klingai.com/v1/videos/image2video",
        ):
            # GET no endpoint de create: só testa auth, não cria job.
            r = c.get(url, headers=headers)
            tries[url.rsplit("/", 2)[-1]] = {"http": r.status_code, "body": r.text[:200]}
        ok = any(v["http"] not in {401, 403} for v in tries.values())
        return {"ok": ok, "tries": tries}


def probe_acedata() -> dict:
    tok = get("ACEDATACLOUD_API_TOKEN")
    if not tok:
        return {"ok": False, "reason": "sem chave"}
    headers = {"Authorization": f"Bearer {tok}", "Accept": "application/json"}
    with httpx.Client(timeout=15.0) as c:
        tries = {}
        for url in (
            "https://api.acedatacloud.com/api/v1/user/info",
            "https://platform.acedatacloud.com/api/v1/user/info",
            "https://api.acedata.cloud/api/v1/users/me",
        ):
            try:
                r = c.get(url, headers=headers)
                tries[url] = {"http": r.status_code, "body": r.text[:200]}
            except Exception as exc:
                tries[url] = {"error": f"{type(exc).__name__}"}
        return {"ok": any(v.get("http") == 200 for v in tries.values()), "tries": tries}


def probe_wavespeed() -> dict:
    tok = get("WAVESPEED_API_KEY")
    if not tok:
        return {"ok": False, "reason": "sem chave"}
    with httpx.Client(timeout=20.0) as c:
        r = c.get(
            "https://api.wavespeed.ai/api/v3/balance",
            headers={"Authorization": f"Bearer {tok}"},
        )
        return {"ok": r.status_code == 200, "http": r.status_code, "body": r.text[:220]}


def probe_luma() -> dict:
    tok = get("LUMA_API_KEY") or get("LUMAAI_API_KEY")
    if not tok:
        return {"ok": False, "reason": "sem chave"}
    with httpx.Client(timeout=20.0) as c:
        r = c.get(
            "https://api.lumalabs.ai/dream-machine/v1/credits",
            headers={"Authorization": f"Bearer {tok}"},
        )
        return {"ok": r.status_code == 200, "http": r.status_code, "body": r.text[:220]}


def probe_heygen() -> dict:
    tok = get("HEYGEN_API_KEY")
    if not tok:
        return {"ok": False, "reason": "sem chave"}
    with httpx.Client(timeout=20.0) as c:
        r = c.get(
            "https://api.heygen.com/v2/user/remaining_quota",
            headers={"X-Api-Key": tok, "Accept": "application/json"},
        )
        return {"ok": r.status_code == 200, "http": r.status_code, "body": r.text[:220]}


def main() -> int:
    apply_env_keys_cache_to_environ()
    cached = get_cached_env_keys() or {}
    present = [k for k in VIDEO_KEYS if usable_secret(cached.get(k) or resolve_env_key(k))]
    print("chaves de vídeo no Mongo:", present)
    report = {}
    for name, fn in (
        ("civitai", probe_civitai),
        ("fal", probe_fal),
        ("replicate", probe_replicate),
        ("runway", probe_runway),
        ("kling", probe_kling),
        ("acedata", probe_acedata),
        ("wavespeed", probe_wavespeed),
        ("luma", probe_luma),
        ("heygen", probe_heygen),
    ):
        try:
            report[name] = fn()
        except Exception as exc:
            report[name] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        print(f"-- {name} --", flush=True)
        print(json.dumps(report[name], indent=2, ensure_ascii=False)[:1500], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
