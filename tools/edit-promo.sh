set -euo pipefail
S=/tmp/claude-0/-home-user/11d9748f-98a9-5e1b-bd66-b55a5ed28106/scratchpad
M="/root/.claude/uploads/11d9748f-98a9-5e1b-bd66-b55a5ed28106/89921033-Warm_Launch.mp3"
cd "$S"
dur() { ffprobe -v error -show_entries format=duration -of csv=p=0 "$1"; }

TITLE=3.2; BODY=24.0; ENDC=4.0; XF=0.5

# Still cards with a slow push-in. d=1 so the zoom follows the output frame
# index; anything else holds each input frame and the segment explodes.
card() {   # card <png> <seconds> <rate> <out>
  ffmpeg -y -v error -loop 1 -i "$1" -frames:v "$(python3 -c "print(int($2*30))")" \
    -vf "scale=3840:2160,zoompan=z='min(1+$3*on,1.09)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=30,format=yuv420p" \
    -r 30 "$4"
}
card card_title.png $TITLE 0.00085 seg_title.mp4
card card_end.png   $ENDC  0.00055 seg_end.mp4

ffmpeg -y -v error -i raw.webm -loop 1 -framerate 30 -t 4.0 -i cap1.png -loop 1 -framerate 30 -t 5.8 -i cap2.png -loop 1 -framerate 30 -t 6.0 -i cap3.png -loop 1 -framerate 30 -t 2.7 -i cap4.png \
  -filter_complex "
    [0:v]trim=0:${BODY},setpts=PTS-STARTPTS,scale=1920:1080,fps=30[v];
    [1:v]format=rgba,fade=t=in:st=0:d=0.35:alpha=1,fade=t=out:st=3.65:d=0.35:alpha=1,setpts=PTS-STARTPTS+0.4/TB[c1];
    [2:v]format=rgba,fade=t=in:st=0:d=0.35:alpha=1,fade=t=out:st=5.45:d=0.35:alpha=1,setpts=PTS-STARTPTS+5.0/TB[c2];
    [3:v]format=rgba,fade=t=in:st=0:d=0.35:alpha=1,fade=t=out:st=5.65:d=0.35:alpha=1,setpts=PTS-STARTPTS+12.6/TB[c3];
    [4:v]format=rgba,fade=t=in:st=0:d=0.35:alpha=1,fade=t=out:st=2.35:d=0.35:alpha=1,setpts=PTS-STARTPTS+21.2/TB[c4];
    [v][c1]overlay=enable='between(t,0.4,4.4)':eof_action=pass:repeatlast=0[o1];
    [o1][c2]overlay=enable='between(t,5.0,10.8)':eof_action=pass:repeatlast=0[o2];
    [o2][c3]overlay=enable='between(t,12.6,18.6)':eof_action=pass:repeatlast=0[o3];
    [o3][c4]overlay=enable='between(t,21.2,23.9)':eof_action=pass:repeatlast=0,format=yuv420p[out]
  " -map "[out]" -r 30 seg_body.mp4

T=$(dur seg_title.mp4); B=$(dur seg_body.mp4); E=$(dur seg_end.mp4)
echo "segments: title ${T}s  body ${B}s  end ${E}s"

# Offsets from the MEASURED lengths. Using the intended ones cut six seconds
# off the end last time, because zoompan does not land exactly on request.
O1=$(python3 -c "print(round($T-$XF,3))")
O2=$(python3 -c "print(round($T+$B-2*$XF,3))")
ffmpeg -y -v error -i seg_title.mp4 -i seg_body.mp4 -i seg_end.mp4 \
  -filter_complex "[0:v][1:v]xfade=transition=fade:duration=$XF:offset=$O1[a];
                   [a][2:v]xfade=transition=fade:duration=$XF:offset=$O2[v]" \
  -map "[v]" -r 30 silent.mp4

D=$(dur silent.mp4); echo "silent cut: ${D}s"

# The bed is quiet until 0:06 and lands on the beat there; starting at 3.0
# puts that landing on the cut out of the title card.
FO=$(python3 -c "print(round(float('$D')-2.4,2))")
ffmpeg -y -v error -ss 3.0 -t "$D" -i "$M" \
  -af "afade=t=in:st=0:d=0.6,afade=t=out:st=$FO:d=2.4,loudnorm=I=-16:TP=-1.5:LRA=11" \
  -vn -ar 48000 -ac 2 bed.m4a

ffmpeg -y -v error -i silent.mp4 -i bed.m4a \
  -c:v libx264 -preset slow -crf 19 -pix_fmt yuv420p -movflags +faststart \
  -c:a aac -b:a 192k -shortest magic-scraper-promo.mp4
echo "=== final ==="
ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_name,width,height,r_frame_rate -of default=nw=1 magic-scraper-promo.mp4
