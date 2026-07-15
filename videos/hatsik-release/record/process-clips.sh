#!/usr/bin/env bash
# Speed-process the raw recordings (clips/) into the beat media used by index.html (beats/).
# Trims and speed factors match STORYBOARD.md; event timestamps in the composition
# assume exactly these values.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p beats

enc="-an -c:v libx264 -crf 18 -pix_fmt yuv420p"

ffmpeg -v error -y -ss 1.2 -to 20.5 -i clips/clip-01-crear-evento.mp4 \
    -vf "setpts=(PTS-STARTPTS)/1.8,fps=30" $enc beats/b1-crear.mp4

ffmpeg -v error -y -ss 2.2 -to 13.5 -i clips/clip-02-anadir-items.mp4 \
    -vf "setpts=(PTS-STARTPTS)/2.0,fps=30" $enc beats/_b2a.mp4
ffmpeg -v error -y -ss 13.5 -to 33.9 -i clips/clip-02-anadir-items.mp4 \
    -vf "setpts=(PTS-STARTPTS)/3.5,fps=30" $enc beats/_b2b.mp4
printf "file '_b2a.mp4'\nfile '_b2b.mp4'\n" > beats/_b2.txt
ffmpeg -v error -y -f concat -safe 0 -i beats/_b2.txt -c copy beats/b2-items.mp4
rm beats/_b2a.mp4 beats/_b2b.mp4 beats/_b2.txt

ffmpeg -v error -y -ss 2.5 -to 12.6 -i clips/clip-03-compartir.mp4 \
    -vf "setpts=(PTS-STARTPTS)/1.5,fps=30" $enc beats/b3-compartir.mp4

ffmpeg -v error -y -ss 2.5 -to 17.4 -i clips/clip-04-tomar.mp4 \
    -vf "setpts=(PTS-STARTPTS)/1.8,fps=30" $enc beats/b4-tomar.mp4

ffmpeg -v error -y -ss 2.5 -to 13.9 -i clips/clip-05-comprado.mp4 \
    -vf "setpts=(PTS-STARTPTS)/1.5,fps=30" $enc beats/b5-comprado.mp4

echo "beats/ ready:"
ls -lh beats/*.mp4
