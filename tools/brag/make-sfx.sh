#!/usr/bin/env bash
# Synthesise the brag cuts' sound effects.
#
# Made rather than sourced, for two reasons. Licensing: every bundled SFX pack
# we looked at either stated no terms or shipped one pre-rendered track welded
# to another block's timing. And fit: these are cut to our own beat grid --
# 120.19 BPM, a beat every 0.50s -- so a tick is shorter than the gap it sits
# in and nothing smears into the next line.
#
# Deterministic: same inputs, same bytes. Re-run freely.
set -euo pipefail
OUT="${1:-$(dirname "$0")/../../brag-output/sfx}"
mkdir -p "$OUT"
FF="ffmpeg -hide_banner -v error -y"

# tick -- one soft wooden click under each kinetic line. Two short sines an
# octave apart with a near-instant decay; at 55ms it reads as punctuation
# rather than a note.
$FF -f lavfi -i "sine=frequency=1800:duration=0.055" \
    -f lavfi -i "sine=frequency=900:duration=0.055" \
    -filter_complex "[0:a]volume=0.5[a];[1:a]volume=0.32[b];[a][b]amix=inputs=2:normalize=0,\
afade=t=out:st=0.004:d=0.05:curve=exp,highpass=f=320,volume=0.9" \
    -ar 48000 -ac 2 "$OUT/tick.wav"

# thud -- the turn on "Stop." A low sine drop with a noise transient on the
# front so it has an edge rather than just weight.
$FF -f lavfi -i "sine=frequency=150:duration=0.42" \
    -f lavfi -i "anoisesrc=d=0.06:c=brown:a=0.5" \
    -filter_complex "[0:a]volume=1.0,afade=t=out:st=0.02:d=0.4:curve=exp[a];\
[1:a]lowpass=f=1400,afade=t=out:st=0:d=0.06:curve=exp,volume=0.55[b];\
[a][b]amix=inputs=2:normalize=0,volume=1.1" \
    -ar 48000 -ac 2 "$OUT/thud.wav"

# riser -- 0.9s into the product reveal. Filtered noise opening up, so it
# builds without the cliche of a pitch-swept siren.
$FF -f lavfi -i "anoisesrc=d=0.9:c=pink:a=0.6" \
    -af "highpass=f=200,lowpass=f=1000:poles=1,\
volume='0.05+0.95*pow(t/0.9,2.2)':eval=frame,afade=t=out:st=0.84:d=0.06,volume=0.5" \
    -ar 48000 -ac 2 "$OUT/riser.wav"

# land -- the product arriving. Soft low body plus a short bright tail, the
# sound of something being set down rather than dropped.
$FF -f lavfi -i "sine=frequency=210:duration=0.5" \
    -f lavfi -i "sine=frequency=1260:duration=0.34" \
    -filter_complex "[0:a]afade=t=out:st=0.03:d=0.46:curve=exp,volume=0.85[a];\
[1:a]afade=t=out:st=0.01:d=0.32:curve=exp,volume=0.2[b];\
[a][b]amix=inputs=2:normalize=0" \
    -ar 48000 -ac 2 "$OUT/land.wav"

# tap -- a touch point on the UI. Deliberately drier and higher than the tick
# so a tap never reads as another line of type.
$FF -f lavfi -i "sine=frequency=2600:duration=0.035" \
    -f lavfi -i "anoisesrc=d=0.03:c=white:a=0.35" \
    -filter_complex "[0:a]volume=0.42,afade=t=out:st=0.002:d=0.032:curve=exp[a];\
[1:a]highpass=f=2000,afade=t=out:st=0:d=0.03:curve=exp,volume=0.3[b];\
[a][b]amix=inputs=2:normalize=0" \
    -ar 48000 -ac 2 "$OUT/tap.wav"

# chime -- the wordmark. A major third, quiet, the only pitched cue in the cut.
$FF -f lavfi -i "sine=frequency=880:duration=1.1" \
    -f lavfi -i "sine=frequency=1108:duration=1.1" \
    -filter_complex "[0:a]volume=0.3[a];[1:a]volume=0.22,adelay=70|70[b];\
[a][b]amix=inputs=2:normalize=0,afade=t=out:st=0.12:d=0.95:curve=exp,volume=0.8" \
    -ar 48000 -ac 2 "$OUT/chime.wav"

for f in "$OUT"/*.wav; do
  printf '%-10s %ss\n' "$(basename "$f")" "$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")"
done
