#!/bin/bash
# Generates every raw asset through OpenRouter. Safe to re-run: skips files that exist.
cd "$(dirname "$0")/.." || exit 1
. ~/.config/shell/secrets.env
G="python3 tools/or_media.py"
job() { local out="$1"; shift; [ -s "$out" ] && { echo "skip $out"; return; }; "$@" && echo "done $out" || echo "FAIL $out"; }

NO="No vocals."
job raw/music_shift.mp3 $G audio google/lyria-3-pro-preview raw/music_shift.mp3 "Instrumental score for a night shift in a retrofuturist newsroom mission control, watching a glowing globe while news breaks around the world. Warm analog synthesizers in the style of a Juno-106 and a Prophet-5, a pulsing arpeggiated sequence, deep sub bass, a soft brushed drum machine, a subtle teletype rhythm, tape saturation. 92 BPM, D minor. Calm and focused, slowly building tension, never aggressive, steady energy that loops well. Evokes 1970s space program documentaries with modern cinematic production. $NO" &
job raw/music_title.mp3 $G audio google/lyria-3-clip-preview raw/music_title.mp3 "Instrumental opening title theme, retrofuturist and cutting edge: shimmering analog synth pads, a confident rising melodic motif on a bright polysynth, a deep bass pulse, cinematic wonder, 1960s space-age optimism with modern production. D minor opening that lifts to F major. $NO" &
job raw/music_dawn.mp3 $G audio google/lyria-3-clip-preview raw/music_dawn.mp3 "Instrumental sunrise finale: triumphant and warm analog synth brass with soft strings, a bright resolution in F major, a gentle drum machine, the feeling of a night's work done well at dawn, 1970s space program optimism. $NO" &
job raw/sting_publish.mp3 $G audio google/lyria-3-clip-preview raw/sting_publish.mp3 "Instrumental. Starts immediately with a short bright triumphant synth fanfare stinger of about two seconds: a rising major chord on an analog polysynth with a sparkle. Then silence for the rest of the clip. $NO" &
job raw/sting_upgrade.mp3 $G audio google/lyria-3-clip-preview raw/sting_upgrade.mp3 "Instrumental. Starts immediately with a short futuristic power-up jingle of about three seconds: a fast ascending analog synth arpeggio that resolves on a shimmering major chord. Then silence for the rest of the clip. $NO" &
job raw/sting_rival.mp3 $G audio google/lyria-3-clip-preview raw/sting_rival.mp3 "Instrumental. Starts immediately with a short ominous two-second synth sting: a descending minor brass stab on an analog synth with a low boom. Then silence for the rest of the clip. $NO" &
job raw/sting_breaking.mp3 $G audio google/lyria-3-clip-preview raw/sting_breaking.mp3 "Instrumental. Starts immediately with a short urgent news bulletin stinger of about two seconds: rapid teletype-like synth pulses and a bold brass chord, like a classic TV breaking-news alert. Then silence for the rest of the clip. $NO" &
wait

VOICE="You are the calm, precise voice of a 1960s mission control announcer who works in a newsroom. Speak with a warm, low, confident tone. Say exactly the following line and nothing else:"
while IFS='|' read -r name line; do
  [ -z "$name" ] && continue
  job "raw/$name.pcm" $G audio openai/gpt-audio "raw/$name.pcm" "$VOICE $line" --voice cedar --format pcm16 &
done <<'LINES'
v_start|Night shift is live. Twenty hundred hours. Stories are breaking around the world.
v_breaking|Breaking news.
v_call|Editor, your call.
v_published|Published.
v_scoop|Scoop. We ran it first.
v_rival|The Daily Rumor ran it first.
v_capability|New capability online.
v_correction|Correction issued.
v_dawn|Oh six hundred. The morning edition is going to press. Good work, editor.
v_trust|We lost the readers' trust. The shift is over.
LINES
wait

STYLE="Retrofuturist 1960s space-age technical illustration in the style of vintage NASA and IBM posters. Screen-print texture, flat limited palette: signal red #F42C2B, electric blue #0160F1, sodium orange #FF6D1B, deep ink navy #0B1640 linework, on a warm cream paper #FDFCF5 background. Clean geometric shapes, subtle halftone dot shading, generous empty margin, one centered subject. Absolutely no text, no letters, no numbers, no logos."
while IFS='|' read -r name subj; do
  [ -z "$name" ] && continue
  job "raw/$name.png" $G image google/gemini-3-pro-image "raw/$name.png" "$STYLE Subject: $subj" --aspect 1:1 &
done <<'IMGS'
cap_transcribe|a reel-to-reel tape recorder whose tape unspools into flowing lines of printed type
cap_documents|a tall stack of paper documents with a glowing scanning lens hovering over the top page
cap_style|a fountain pen nib drawing one perfect ribbon of type beside a closed style guide book
cap_factcheck|a magnifying glass over a document, with one large check mark and one cross mark
cap_routing|a railway switch junction where glowing signal lines branch toward three different machines
cap_memory|a tall archive cabinet of drawers with one drawer open and light pouring out of it
cap_packages|a pneumatic tube capsule opening to release a folded newspaper, a photograph and small cards
cap_seats|two friendly retro robot desk agents with antennas working at a curved console
IMGS
job raw/frontpage.png $G image google/gemini-3-pro-image raw/frontpage.png "Retrofuturist 1960s newsroom mission control at dawn, wide shot: curved rows of consoles with glowing screens, a few editors at work, a giant glowing holographic globe floating in the center of the room, tall windows showing a sunrise over a city skyline. Cinematic lighting, strong contrast, photographic illustration. No text, no letters, no logos." --aspect 16:9 &
job raw/title_art.png $G image google/gemini-3-pro-image raw/title_art.png "Retrofuturist space-age newsroom seen from above: a vast dark circular mission control room under a geodesic dome at night, a huge glowing globe of halftone dots floats in the center with light arcs travelling between cities, rings of cream consoles, warm sodium orange and electric blue light. Cinematic, cutting edge, 1960s World's Fair optimism. No text, no letters, no logos." --aspect 16:9 &
wait
echo ALL_DONE
