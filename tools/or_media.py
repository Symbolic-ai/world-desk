#!/usr/bin/env python3
"""Generate music, voice and images through OpenRouter.

Usage:
  or_media.py audio MODEL OUT PROMPT [--voice NAME] [--format mp3|wav|pcm16]
  or_media.py image MODEL OUT PROMPT [--aspect 16:9]
Reads OPENROUTER_API_KEY from the environment.
"""
import base64, json, os, sys, urllib.request

API = "https://openrouter.ai/api/v1/chat/completions"


def post(body, stream):
    req = urllib.request.Request(API, data=json.dumps(body).encode(), headers={
        "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://www.symbolic.ai",
        "X-Title": "Symbolic World Desk assets",
    })
    return urllib.request.urlopen(req, timeout=600)


def audio(model, out, prompt, voice=None, fmt=None):
    body = {"model": model, "stream": True, "modalities": ["text", "audio"],
            "messages": [{"role": "user", "content": prompt}]}
    if voice or fmt:
        body["audio"] = {k: v for k, v in (("voice", voice), ("format", fmt)) if v}
    chunks, text, meta = [], [], {}
    with post(body, True) as r:
        for raw in r:
            line = raw.decode().strip()
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if data == "[DONE]":
                break
            ev = json.loads(data)
            if "error" in ev:
                raise SystemExit(f"error: {ev['error']}")
            for ch in ev.get("choices", []):
                d = ch.get("delta", {})
                a = d.get("audio") or {}
                if a.get("data"):
                    chunks.append(a["data"])
                for k in ("format", "mime_type", "id"):
                    if a.get(k):
                        meta[k] = a[k]
                if d.get("content"):
                    text.append(d["content"])
                if a.get("transcript"):
                    text.append(a["transcript"])
            if ev.get("usage"):
                meta["usage"] = ev["usage"]
    raw = b"".join(base64.b64decode(c) for c in chunks)
    if not raw:
        raise SystemExit(f"no audio returned; text={''.join(text)[:300]!r} meta={meta}")
    open(out, "wb").write(raw)
    print(json.dumps({"out": out, "bytes": len(raw), "meta": meta, "text": "".join(text)[:200]}))


def image(model, out, prompt, aspect=None):
    body = {"model": model, "modalities": ["image", "text"],
            "messages": [{"role": "user", "content": prompt}]}
    if aspect:
        body["image_config"] = {"aspect_ratio": aspect}
    with post(body, False) as r:
        resp = json.load(r)
    msg = resp["choices"][0]["message"]
    imgs = msg.get("images") or []
    if not imgs:
        raise SystemExit(f"no image returned: {str(msg)[:300]}")
    url = imgs[0]["image_url"]["url"]
    b64 = url.split(",", 1)[1]
    open(out, "wb").write(base64.b64decode(b64))
    print(json.dumps({"out": out, "usage": resp.get("usage", {})}))


if __name__ == "__main__":
    kind, model, out, prompt = sys.argv[1:5]
    opts = dict(zip(sys.argv[5::2], sys.argv[6::2]))
    if kind == "audio":
        audio(model, out, prompt, opts.get("--voice"), opts.get("--format"))
    else:
        image(model, out, prompt, opts.get("--aspect"))
