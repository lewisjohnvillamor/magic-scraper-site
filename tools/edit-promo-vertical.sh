# Cut the 9:16 version of the promo for Reels/TikTok.
#
# Same plate as the landscape cut -- raw.webm, recorded by record-promo.mjs --
# recomposed to portrait: the popup region cropped out of the 1920x1080 frame
# and set on a dark canvas, with the caption cards above it. The card sources
# are in tools/cards/; render them to PNG with shoot-cards-vertical.mjs first.
#
set -euo pipefail
S=/tmp/claude-0/-home-user/11d9748f-98a9-5e1b-bd66-b55a5ed28106/scratchpad
M="/root/.claude/uploads/11d9748f-98a9-5e1b-bd66-b55a5ed28106/89921033-Warm_Launch.mp3"
cd "$S"
dur() { ffprobe -v error -show_entries format=duration -of csv=p=0 "$1"; }

TITLE=3.2; ENDC=4.0; XF=0.5
# Same cut as the landscape version: the middle of the 22-second drill is
# dropped and the halves cross-faded, so "Drilling 12 / 54" becomes
# "Drilling 40 / 54" across half a second instead of in real time.
CUT_A=18.6; CUT_B=30.6; XM=0.5; END=42.6
BODY=30.1   # CUT_A + (END - CUT_B) - XM, and what the join below produces

# The popup sits at x 1157-1809, y 65-1014 in the 1920x1080 plate (measured,
# not guessed -- record-promo.mjs scales it to 1.42 and pins it 110px from the
# right edge). Crop a little wider so a strip of the shop still shows down the
# left edge: the point of the shot is that this is running on a real page, not
# in a mockup.
CROP="crop=740:958:1085:60"

card() {   # card <png> <seconds> <rate> <out>
  ffmpeg -y -v error -loop 1 -i "$1" -frames:v "$(python3 -c "print(int($2*30))")" \
    -vf "scale=2160:3840,zoompan=z='min(1+$3*on,1.09)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30,format=yuv420p" \
    -r 30 "$4"
}
card v_title.png $TITLE 0.00085 vseg_title.mp4
card v_end.png   $ENDC  0.00055 vseg_end.mp4

# Every caption is its own looped, timed stream: a one-frame PNG ends the
# overlay stream immediately and eof_action=pass then drops it for good.
JOIN=$(python3 -c "print(round($CUT_A-$XM,3))")
ffmpeg -y -v error -i raw.webm \
  -loop 1 -framerate 30 -t 4.0 -i v_cap1.png \
  -loop 1 -framerate 30 -t 5.8 -i v_cap2.png \
  -loop 1 -framerate 30 -t 6.0 -i v_cap3.png \
  -loop 1 -framerate 30 -t 3.4 -i v_cap4.png \
  -loop 1 -framerate 30 -t $BODY -i v_foot.png \
  -f lavfi -t $BODY -i "color=c=0x14121f:s=1080x1920:r=30" \
  -filter_complex "
    [0:v]split=2[p1][p2];
    [p1]trim=0:${CUT_A},setpts=PTS-STARTPTS,${CROP},scale=1035:1340,fps=30[va];
    [p2]trim=${CUT_B}:${END},setpts=PTS-STARTPTS,${CROP},scale=1035:1340,fps=30[vb];
    [va][vb]xfade=transition=fade:duration=${XM}:offset=${JOIN}[v];
    [6:v][v]overlay=x=22:y=500[b0];
    [b0][5:v]overlay=0:0[b1];
    [1:v]format=rgba,fade=t=in:st=0:d=0.35:alpha=1,fade=t=out:st=3.65:d=0.35:alpha=1,setpts=PTS-STARTPTS+0.4/TB[c1];
    [2:v]format=rgba,fade=t=in:st=0:d=0.35:alpha=1,fade=t=out:st=5.45:d=0.35:alpha=1,setpts=PTS-STARTPTS+5.0/TB[c2];
    [3:v]format=rgba,fade=t=in:st=0:d=0.35:alpha=1,fade=t=out:st=5.65:d=0.35:alpha=1,setpts=PTS-STARTPTS+13.2/TB[c3];
    [4:v]format=rgba,fade=t=in:st=0:d=0.35:alpha=1,fade=t=out:st=3.05:d=0.35:alpha=1,setpts=PTS-STARTPTS+26.2/TB[c4];
    [b1][c1]overlay=enable='between(t,0.4,4.4)':eof_action=pass:repeatlast=0[o1];
    [o1][c2]overlay=enable='between(t,5.0,10.8)':eof_action=pass:repeatlast=0[o2];
    [o2][c3]overlay=enable='between(t,13.2,19.2)':eof_action=pass:repeatlast=0[o3];
    [o3][c4]overlay=enable='between(t,26.2,29.6)':eof_action=pass:repeatlast=0,format=yuv420p[out]
  " -map "[out]" -r 30 vseg_body.mp4

T=$(dur vseg_title.mp4); B=$(dur vseg_body.mp4); E=$(dur vseg_end.mp4)
echo "segments: title ${T}s  body ${B}s  end ${E}s"

# Offsets from the MEASURED lengths -- zoompan does not land exactly on the
# requested duration, and using the intended numbers cut six seconds off the
# end of the landscape cut.
O1=$(python3 -c "print(round($T-$XF,3))")
O2=$(python3 -c "print(round($T+$B-2*$XF,3))")
ffmpeg -y -v error -i vseg_title.mp4 -i vseg_body.mp4 -i vseg_end.mp4 \
  -filter_complex "[0:v][1:v]xfade=transition=fade:duration=$XF:offset=$O1[a];
                   [a][2:v]xfade=transition=fade:duration=$XF:offset=$O2[v]" \
  -map "[v]" -r 30 vsilent.mp4

D=$(dur vsilent.mp4); echo "silent cut: ${D}s"

FO=$(python3 -c "print(round(float('$D')-2.4,2))")
ffmpeg -y -v error -ss 3.0 -t "$D" -i "$M" \
  -af "afade=t=in:st=0:d=0.6,afade=t=out:st=$FO:d=2.4,loudnorm=I=-16:TP=-1.5:LRA=11" \
  -vn -ar 48000 -ac 2 vbed.m4a

ffmpeg -y -v error -i vsilent.mp4 -i vbed.m4a \
  -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -movflags +faststart \
  -c:a aac -b:a 192k -shortest magic-scraper-promo-vertical.mp4
echo "=== final ==="
ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_name,width,height,r_frame_rate -of default=nw=1 magic-scraper-promo-vertical.mp4
