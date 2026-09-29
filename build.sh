#!/usr/bin/env bash
# Team NAK explainer video engine: voice -> audio mix -> frames -> MP4
set -e
cd "$(dirname "$0")"
# 1) one-time downloads (voice model + heading font)
[ -f kokoro-v1.0.onnx ] || curl -L -o kokoro-v1.0.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
[ -f voices-v1.0.bin ]  || curl -L -o voices-v1.0.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
mkdir -p fonts/higgsfield fonts/dejavu
[ -f fonts/higgsfield/Montserrat-ExtraBold.ttf ] || curl -L -o fonts/higgsfield/Montserrat-ExtraBold.ttf https://raw.githubusercontent.com/JulietaUla/Montserrat/master/fonts/ttf/Montserrat-ExtraBold.ttf
[ -f fonts/higgsfield/Inter-Bold.ttf ] || (curl -L -o /tmp/inter.zip https://github.com/rsms/inter/releases/download/v4.0/Inter-4.0.zip && unzip -j -o /tmp/inter.zip extras/ttf/Inter-Bold.ttf -d fonts/higgsfield)
# DejaVu fonts: copy from your system (Linux: /usr/share/fonts/truetype/dejavu) into fonts/dejavu
export FD="$(pwd)/fonts/"
# 2) voice (skip if you replaced v0.wav..v8.wav with your own recordings)
[ -f v8.wav ] || python3 tts.py
# 3) music, sound effects, ducking, lip-sync data
python3 mix.py
# 4) render frames in parallel segments
N=${N:-4}; rm -f seg*.mp4 list.txt
for ((w=0; w<N; w++)); do python3 render.py enc $w $N & echo "file 'seg$w.mp4'" >> list.txt; done; wait
MUX="-map 0:v -map 1:a -c:v copy -af loudnorm=I=-16:TP=-1.5 -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart"
ffmpeg -y -loglevel error -f concat -safe 0 -i list.txt -i mix.wav $MUX teamnak-explainer-website.mp4
# 5) Fiverr-safe version (no URL): re-render only the last segment
CTA=fiverr python3 render.py enc $((N-1)) $N
ffmpeg -y -loglevel error -f concat -safe 0 -i list.txt -i mix.wav $MUX teamnak-explainer-fiverr.mp4
echo "Done: teamnak-explainer-website.mp4, teamnak-explainer-fiverr.mp4"
