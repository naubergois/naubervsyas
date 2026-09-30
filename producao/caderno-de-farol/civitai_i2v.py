#!/usr/bin/env python3
"""I2V Wan 3.0 na CivitAI — takes do Caderno de Farol."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from PIL import Image

sys.path.insert(0, "/Users/naubergois/qclawmonitor/src")

from gois.content.civitai_orchestrate import get_workflow, submit_workflow
from gois.content.local_image_civitai_http import civitai_post
from gois.content.local_image_keys import resolve_civitai_token
from gois.env_keys_mongo import apply_env_keys_cache_to_environ

ROOT = Path(__file__).resolve().parent
ASSETS = Path("/Users/naubergois/.cursor/projects/Users-naubergois-canalnauber/assets")
STILLS = ROOT / "stills"
OUT = ROOT / "preview" / "i2v"
JOBS = ROOT / "preview" / "civitai-jobs.json"
NEG = (
    "constant speed, linear motion, frozen cloth, no anticipation, "
    "everything stops at once, slideshow, jitter, morphing face, "
    "photoreal face, english text, watermark, logo"
)

TAKES = [
    {
        "id": "00",
        "still": STILLS / "amanha-clean.png",
        "prompt": (
            "Young woman in a mustard-yellow jacket holds a glowing cream page. "
            "She inhales, then the page lifts a finger-width with ease-out. "
            "Hair and jacket hem arrive late. Paper cat on the rail twitches its tail last. "
            "City lights behind the glass flicker one by one, not all at once. "
            "Camera locked at chest height, tiny push-in, no orbit. Same face, same bun."
        ),
    },
    {
        "id": "01",
        "still": ASSETS / "caderno-de-farol-mare.png",
        "prompt": (
            "Night tide of printed papers rolls in, heavy then ease-out. "
            "A few sheets lift in the wind after the wave. "
            "The crouched figure in the yellow jacket stamps once — shoulder recoils first. "
            "Camera tracks late along the waterline. No new faces."
        ),
    },
    {
        "id": "02",
        "still": ASSETS / "caderno-de-farol-selo.png",
        "prompt": (
            "The brass stamp lifts a centimeter, then slams. Ease-in on the lift, "
            "ease-out as yellow ink spreads on the cream page. "
            "Raindrops keep falling out of sync. Paper cat on the right blinks last. "
            "Camera locked, one punch-in of a palm. Hands stay the same."
        ),
    },
    {
        "id": "03",
        "still": ASSETS / "caderno-de-farol-rascunho.png",
        "prompt": (
            "Paper cat made of taped journal pages. Chest expands. "
            "Origami ear flicks. Tape-ribbon tail arrives two beats late. "
            "Ink-dot eye blinks once. Camera locked. No morphing into a real cat."
        ),
    },
    {
        "id": "06",
        "still": ASSETS / "cdf-cidade.png",
        "prompt": (
            "Coastal city night from a lighthouse window. Streetlights die in a wave "
            "from left to right, not together. Windows wink out after the streetlamps. "
            "Camera locked. No new buildings, no text."
        ),
    },
    {
        "id": "07",
        "still": STILLS / "amanha-clean.png",
        "prompt": (
            "The lighthouse lamp behind her dies — flicker, then dead steel. "
            "The cream page in her hands keeps glowing. Hair lifts as if air left the room. "
            "Paper cat's pages ruffle last. Camera lags half a beat. Same woman, same jacket."
        ),
    },
    {
        "id": "08",
        "still": ASSETS / "cdf-sombra.png",
        "prompt": (
            "Morning steel room. Dust drifts in the shaft of light. "
            "The paper cat's shadow on the crate shifts a little. "
            "The woman in the yellow jacket does not cast a shadow. "
            "Old man in the doorway stays still. Camera locked."
        ),
    },
    {
        "id": "09",
        "still": ASSETS / "cdf-vidro.png",
        "prompt": (
            "Dawn spray hits the lighthouse glass. The wet page on the outside "
            "peels a corner, then sticks again. Wind after the spray. "
            "Camera locked close. No new text."
        ),
    },
]


def to_png(src: Path, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(src).convert("RGB")
    im.save(dest, "PNG")
    return dest


def upload_png(path: Path, token: str) -> str:
    import requests

    url = "https://orchestration.civitai.com/v2/consumer/blobs"
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "caderno-de-farol-i2v/1.0",
        "Content-Type": "image/png",
    }
    r = requests.post(url, headers=headers, data=path.read_bytes(), timeout=60)
    if r.status_code not in {200, 201}:
        raise RuntimeError(f"upload {path.name} HTTP {r.status_code}: {r.text[:300]}")
    payload = r.json() if r.content else {}
    for key in ("url", "availableUrl"):
        if payload.get(key):
            return str(payload[key])
    blob = payload.get("blob") or payload.get("data") or {}
    if isinstance(blob, dict) and (blob.get("url") or blob.get("availableUrl")):
        return str(blob.get("url") or blob.get("availableUrl"))
    if payload.get("id"):
        return f"https://orchestration.civitai.com/v2/consumer/blobs/{payload['id']}"
    raise RuntimeError(f"upload sem URL: {str(payload)[:240]}")


def submit_take(take: dict, image_url: str, token: str) -> dict:
    step = {
        "engine": "wan",
        "version": "v3.0",
        "operation": "image-to-video",
        "startImage": image_url,
        "prompt": take["prompt"],
        "resolution": "720p",
        "duration": 5,
        "enablePromptExpansion": False,
        "negativePrompt": NEG,
    }
    body = {
        "steps": [{"$type": "videoGen", "input": step}],
        "tags": ["caderno-de-farol", take["id"]],
        "metadata": {"source": "caderno-de-farol", "beat": take["id"]},
        "allowMatureContent": False,
        "currencies": ["green", "blue", "yellow"],
    }
    return submit_workflow(body, token=token, wait=0, whatif=False)


def main() -> int:
    apply_env_keys_cache_to_environ()
    token = resolve_civitai_token()
    if not token:
        print("sem CIVITAI_API_TOKEN")
        return 1
    OUT.mkdir(parents=True, exist_ok=True)
    print("civitai token ok, user naubergois")

    jobs = []
    if JOBS.is_file():
        try:
            jobs = json.loads(JOBS.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            jobs = []
    by_id = {j.get("id"): j for j in jobs if isinstance(j, dict)}

    for take in TAKES:
        dest = OUT / f"{take['id']}.mp4"
        if dest.is_file() and dest.stat().st_size > 8000:
            print(f"skip {take['id']} (mp4)")
            by_id[take["id"]] = {"id": take["id"], "ok": True, "status": "exists", "video": str(dest)}
            continue
        prev = by_id.get(take["id"]) or {}
        if prev.get("workflow_id") and prev.get("ok") and prev.get("status") not in {"failed", "canceled"}:
            print(f"resume {take['id']} {prev['workflow_id']}")
            continue
        png = STILLS / f"i2v-{take['id']}.png"
        print(f"upload {take['id']}")
        to_png(take["still"], png)
        url = upload_png(png, token)
        print(f"submit {take['id']}")
        res = submit_take(take, url, token)
        if not res.get("ok"):
            print(f"  ERRO {take['id']}: {res.get('error')}")
            by_id[take["id"]] = {"id": take["id"], "ok": False, "error": res.get("error")}
            continue
        wf = res.get("workflow") or {}
        wid = str(res.get("workflow_id") or wf.get("id") or "")
        print(f"  wf {wid} {res.get('status') or wf.get('status')}")
        by_id[take["id"]] = {"id": take["id"], "ok": True, "workflow_id": wid, "status": res.get("status")}

    jobs = list(by_id.values())
    JOBS.write_text(json.dumps(jobs, indent=2), encoding="utf-8")

    pending = [j for j in jobs if j.get("ok") and j.get("workflow_id") and not (OUT / f"{j['id']}.mp4").is_file()]
    deadline = time.time() + 900
    while pending and time.time() < deadline:
        still = []
        for job in pending:
            got = get_workflow(job["workflow_id"], token=token)
            wf = got.get("workflow") or {}
            status = str(got.get("status") or wf.get("status") or "").lower()
            job["status"] = status
            print(f"poll {job['id']} {status}", flush=True)
            if status in {"succeeded", "success", "completed"}:
                from gois.content.civitai_orchestrate import _download_url, _extract_media_urls

                media = _extract_media_urls(wf)
                vids = [m for m in media if m.get("kind") in {"video", "blob"} and m.get("url")]
                if vids:
                    dest = OUT / f"{job['id']}.mp4"
                    saved = _download_url(vids[0]["url"], dest, token=token)
                    job["video"] = str(saved or dest)
                    print(f"  saved {job['video']}")
            elif status in {"failed", "canceled", "cancelled"}:
                job["ok"] = False
                job["error"] = got.get("error") or status
            else:
                still.append(job)
        pending = still
        JOBS.write_text(json.dumps(jobs, indent=2), encoding="utf-8")
        if pending:
            time.sleep(12)
    print(json.dumps(jobs, indent=2, ensure_ascii=False))
    return 0 if all(j.get("ok") for j in jobs) else 2


if __name__ == "__main__":
    raise SystemExit(main())
