# Team NAK — IBKR Fiverr explainer

An independent 30-second motion-design production. The existing broad Team NAK video is preserved.

- 1920 × 1080, 30 fps, H.264 / AAC stereo, exactly 30 seconds.
- Neural voice: en-US-AndrewNeural, modestly lowered pitch, natural delivery.
- Original synthesized electronic music and transition sounds, ducked beneath the voice.
- Six distinct compositions, animated charts, a broker-engine orbit, workflow, risk interface and green CTA.
- Captions aligned to speech word timestamps; accompanying SRT.
- No external contact details, seller badges, ratings or performance claims.
- Screens are illustrative, not client screenshots or a recording of a live brokerage account.

## Files

`output/teamnak_ibkr_fiverr_30s.mp4` is the finished upload file.
`output/teamnak_ibkr_preview_720p.mp4` is a lighter preview.
`output/thumbnail.png` is a matching cover image.
`output/storyboard.jpg` shows the six compositions.
`output/narration.wav` is the isolated voiceover.
`output/teamnak_ibkr.srt` contains subtitles.

## Rebuild

From the parent project’s virtual environment:

```sh
../.venv/bin/python build.py
```

Dependencies: skia-python, numpy, soundfile, edge-tts, Pillow, FFmpeg.
Inter and JetBrains Mono are downloaded into `fonts/` from Google Fonts; both are SIL Open Font License fonts.
Voice generation requires network access. Subsequent builds reuse saved audio and timing files.
Edit `SCENES` and `CAPTION_CHUNKS` in `voice.py` to change narration, then remove the corresponding cached `output/voice_<n>.mp3` and metadata before rebuilding.

## Story

0–4s: The manual-trading problem.
4–9s: Custom bots for Interactive Brokers.
9–15s: Strategy / TradingView signal → custom bot → IBKR order.
15–20s: Position sizing, stop-loss logic and monitoring.
20–25s: Paper testing, source ownership, setup and support.
25–30s: Message Team NAK on Fiverr.

Service descriptions are grounded in Team NAK’s local IBKR service page and execution-engine README. Current references checked during production:

- https://help.fiverr.com/hc/en-us/articles/360010451657-Adding-and-managing-your-Gig-video
- https://www.interactivebrokers.com/docs
