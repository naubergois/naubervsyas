#!/usr/bin/env python3
"""I2V Wan 2.2 via fal.ai — fallback quando a CivitAI está sem Buzz."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import httpx

sys.path.insert(0, "/Users/naubergois/qclawmonitor/src")

from gois.content.photo_to_video_fal_create import create_fal_i2v_task
from gois.content.photo_to_video_fal_poll import poll_fal_task
from gois.env_keys_mongo import apply_env_keys_cache_to_environ

ROOT = Path(__file__).resolve().parent
ASSETS = Path("/Users/naubergois/.cursor/projects/Users-naubergois-canalnauber/assets")
STILLS = ROOT / "stills"
OUT = ROOT / "preview" / "i2v"
JOBS = ROOT / "preview" / "fal-jobs.json"

# Só os takes que carregam a história (Buzz/FAL tem custo).
TAKES = [
    (
        "00",
        STILLS / "amanha-clean.png",
        "Young woman in a mustard-yellow jacket. The cream page lifts a finger-width, ease-out. Hair and jacket hem arrive late. Paper cat tail last. City lights flicker one by one. Camera locked, tiny push-in.",
    ),
    (
        "01",
        ASSETS / "caderno-de-farol-mare.png",
        "Night tide of printed papers rolls in, heavy then ease-out. Wind lifts sheets after the wave. The crouched figure in yellow stamps once, shoulder recoils first. Camera tracks late.",
    ),
    (
        "02",
        ASSETS / "caderno-de-farol-selo.png",
        "Brass stamp lifts a centimeter then slams. Yellow ink spreads ease-out. Rain keeps falling out of sync. Paper cat blinks last. Camera locked.",
    ),
    (
        "06",
        ASSETS / "cdf-cidade.png",
        "Coastal night city. Streetlights die left to right in a wave, not together. Windows wink out after the lamps. Camera locked.",
    ),
    (
        "07",
        STILLS / "amanha-clean.png",
        "The lamp behind her dies, flicker then dark. The page in her hands keeps glowing. Hair lifts as if air left the room. Paper cat pages ruffle last. Camera lags.",
    ),
    (
        "09",
        ASSETS / "cdf-vidro.png",
        "Dawn spray hits the glass. The wet page on the outside peels a corner then sticks. Wind after the spray. Camera locked.",
    ),
]


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with httpx.Client(timeout=120.0, follow_redirects=True) as client:
        r = client.get(url)
        r.raise_for_status()
        dest.write_bytes(r.content)


def main() -> int:
    apply_env_keys_cache_to_environ()
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = []
    for cid, still, prompt in TAKES:
        dest = OUT / f"{cid}.mp4"
        if dest.is_file() and dest.stat().st_size > 8000:
            print(f"skip {cid}")
            jobs.append({"id": cid, "ok": True, "status": "exists"})
            continue
        print(f"submit fal {cid}", flush=True)
        created = create_fal_i2v_task(
            prompt=prompt,
            image_path=str(still),
            model="wan",
            duration_seconds=5,
            aspect_ratio="16:9",
        )
        if not created.get("ok"):
            print(f"  ERRO {cid}: {created.get('error')}")
            jobs.append({"id": cid, "ok": False, "error": created.get("error")})
            continue
        if created.get("video_url"):
            download(created["video_url"], dest)
            print(f"  saved {dest}")
            jobs.append({"id": cid, "ok": True, "status": "ready"})
            continue
        rid = created.get("request_id")
        print(f"  request {rid}")
        jobs.append(
            {
                "id": cid,
                "ok": True,
                "request_id": rid,
                "status_url": created.get("status_url"),
                "response_url": created.get("response_url"),
            }
        )

    pending = [j for j in jobs if j.get("ok") and j.get("request_id") and not (OUT / f"{j['id']}.mp4").is_file()]
    deadline = time.time() + 720
    while pending and time.time() < deadline:
        still = []
        for job in pending:
            polled = poll_fal_task(
                api_key="",
                request_id=job.get("request_id") or "",
                status_url=job.get("status_url") or "",
                response_url=job.get("response_url") or "",
                model="wan",
            )
            status = str(polled.get("status") or polled.get("state") or "").lower()
            print(f"poll {job['id']} {status} {polled.get('error') or ''}", flush=True)
            url = polled.get("video_url") or ""
            if url:
                dest = OUT / f"{job['id']}.mp4"
                download(url, dest)
                job["status"] = "ready"
                print(f"  saved {dest}")
            elif status in {"failed", "error"} or polled.get("ok") is False:
                job["ok"] = False
                job["error"] = polled.get("error") or status
            else:
                still.append(job)
        pending = still
        JOBS.write_text(json.dumps(jobs, indent=2), encoding="utf-8")
        if pending:
            time.sleep(8)
    print(json.dumps(jobs, indent=2, ensure_ascii=False))
    return 0 if all(j.get("ok") for j in jobs) else 2


if __name__ == "__main__":
    raise SystemExit(main())
