#!/bin/bash
# Encodes raw generated media into web-sized assets, then packs them into assets.js.
set -e
cd "$(dirname "$0")/.."
F="ffmpeg -v error -y"
$F -i raw/music_shift.mp3 -t 176 -af "loudnorm=I=-18:TP=-1.5,afade=t=out:st=172:d=4" -b:a 128k assets/music_shift.mp3
$F -i raw/music_title.mp3 -af "loudnorm=I=-17:TP=-1.5" -b:a 128k assets/music_title.mp3
$F -i raw/music_dawn.mp3 -af "loudnorm=I=-16:TP=-1.5" -b:a 128k assets/music_dawn.mp3
for s in publish:2.6 upgrade:3.2 rival:2.4 breaking:2.4; do
  n=${s%%:*}; d=${s##*:}; fo=$(python3 -c "print($d-0.7)")
  $F -i raw/sting_$n.mp3 -t $d -af "loudnorm=I=-15:TP=-1.5,afade=t=in:d=0.01,afade=t=out:st=$fo:d=0.7" -b:a 128k assets/sting_$n.mp3
done
for f in raw/v_*.pcm; do
  n=$(basename "$f" .pcm)
  $F -f s16le -ar 24000 -ac 1 -i "$f" -af "loudnorm=I=-15:TP=-1.5" -ar 24000 -b:a 64k assets/$n.mp3
done
for f in raw/cap_*.png; do cwebp -quiet -q 80 -resize 520 520 "$f" -o assets/$(basename "$f" .png).webp; done
cwebp -quiet -q 82 -resize 1280 0 raw/frontpage.png -o assets/frontpage.webp
cwebp -quiet -q 78 -resize 1920 0 raw/title_art.png -o assets/title_art.webp
cp logo.png assets/logo.png
python3 - <<'PY'
import base64, json, os
mime = {'.mp3': 'audio/mpeg', '.webp': 'image/webp', '.png': 'image/png'}
out = {}
for f in sorted(os.listdir('assets')):
    name, ext = os.path.splitext(f)
    if ext in mime:
        out[name] = f"data:{mime[ext]};base64," + base64.b64encode(open(f'assets/{f}', 'rb').read()).decode()
for f in sorted(os.listdir('models')):
    name, ext = os.path.splitext(f)
    if ext == '.glb':
        out['model_' + name] = "data:model/gltf-binary;base64," + base64.b64encode(open(f'models/{f}', 'rb').read()).decode()
with open('assets.js', 'w') as fh:
    fh.write('/* Generated with OpenRouter (Lyria 3, gpt-audio, Gemini 3 Pro Image) and Blender. Packed by tools/process.sh. */\n')
    fh.write('window.WD_ASSETS = ' + json.dumps(out) + ';\n')
print(len(out), 'assets,', os.path.getsize('assets.js') // 1024, 'KB')
PY
