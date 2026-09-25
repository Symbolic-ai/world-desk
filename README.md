# Symbolic: World Desk

A retrofuturist 3D strategy game about running a newsroom's night shift with
[Symbolic](https://www.symbolic.ai).

**Play it:** https://symbolic-ai.github.io/world-desk/

Stories break in cities around a halftone globe from 20:00 to 06:00. You send
Symbolic's AI agents to cover them. Each story moves through research, writing,
fact check and publishing. At the fact check, you read what Symbolic found and
weigh three sources that disagree and choose, before a timer runs out, the one
version of four that the latest authoritative source supports. Publish before the rival paper to
get a scoop. The hours you save unlock Symbolic capabilities: transcription,
document analysis, house style, fact check, AI routing, institutional memory,
publishing packages and more agents. At dawn, the morning edition prints your
best stories.

## Controls

- Drag to turn the globe. Click a story to select it.
- Press `Enter`, or click the story again, to assign an agent.
- Press `A` to `D` to make a fact-check call.
- Press `1` to `9` to pick a story from the list.
- Press `P` to pause and `M` to mute.

## How it is built

- One HTML file with [three.js](https://threejs.org) from a CDN. The file has no
  build step.
- The Earth uses NASA Blue Marble and Black Marble maps (public domain), with a
  ray-marched Rayleigh and Mie atmosphere, cloud shadows, and ocean sun glint.
- The hub station and the satellites are Blender models. Build them with
  `/Applications/Blender.app/Contents/MacOS/Blender -b -P tools/build_models.py`.
- The UI uses the tokens and primitives of the Symbolic app's dark theme and the
  Open Runde font (SIL OFL 1.1, see `fonts/OpenRunde-OFL.txt`).
- The land mask comes from [world-atlas](https://github.com/topojson/world-atlas)
  (Natural Earth).
- `assets.js` holds all generated media as data URIs, so the game also runs
  when you open `index.html` from disk.

The generated media comes from OpenRouter:

| Asset | Model |
| --- | --- |
| Music and stings | `google/lyria-3-pro-preview`, `google/lyria-3-clip-preview` |
| Announcer voice | `openai/gpt-audio` (voice `cedar`) |
| Capability cards, front-page photo, splash | `google/gemini-3-pro-image` |

To make the media again, set `OPENROUTER_API_KEY` and run these commands:

```sh
tools/gen_all.sh   # writes raw/ (about $2 of generation)
tools/process.sh   # encodes raw/ into assets/ and packs assets.js
```

`tools/process.sh` needs `ffmpeg` and `cwebp`.
