# Nadir Ali — premium IBKR Fiverr video, version 2

Revised specifically for Nadir Ali’s Fiverr profile. No Team NAK branding is present in the video, cover, narration or captions. The original production is preserved in the sibling `ibkr_fiverr` folder.

## Deliverables

- `output/nadir_ali_ibkr_fiverr_v2.mp4`: 30 seconds, 1920×1080, 60 fps, H.264 video and AAC stereo audio.
- `output/nadir_ali_ibkr_preview.mp4`: 720p30 lightweight preview.
- `output/thumbnail.png`: matching personal-brand cover.
- `output/storyboard.jpg`: six-scene contact sheet.
- `output/nadir_ali_ibkr.srt`: synchronized subtitles.
- `output/narration.wav`: isolated neural voiceover.
- `assets/mascot.png` and `assets/mascot_presenter.png`: transparent custom mascot artwork.

The mascot has two poses, hovering and tilt motion, grounding shadows and role-specific placement. Depth cards, moving signal packets, orbital accents, a subtle camera push and transition sounds support the story. Captions use word timing from the speech engine.

Voice: en-US-AndrewNeural. The personal script starts “I’m Nadir Ali. I build custom bots for Interactive Brokers” and ends “Message Nadir Ali on Fiverr.” Music and sound effects are synthesized for this video. Interfaces are illustrative rather than footage of a live account or client system.

## Rebuild

```sh
../.venv/bin/python build.py
```

Dependencies are pinned in `requirements.txt`; FFmpeg must be installed. Fonts and platform assets are saved locally. `render.py` is the runnable renderer; `scenes.py` retains the composition definitions for reference. Change scenes directly in `render.py` for subsequent edits. Narration lives in `voice.py`; delete the matching cached `voice_<n>.mp3` and `voice_<n>_words.jsonl` when changing text.

## Platform artwork sources

- Interactive Brokers: https://www.interactivebrokers.com/images/web/logos/ib-logo-text-white.png — official white wordmark, preserved on a dark plaque.
- TradingView: https://www.tradingview.com/media-kit/ — official media kit, white full wordmark.
- Python: https://www.python.org/community/logos/ — official generic SVG, rendered on a white plaque.

The platform marks indicate the technologies used, not sponsorship. They are separate from Nadir Ali’s identity and have not been generated or redesigned.

## Mascot generation

Generated using the built-in ImageGen tool; the saved transparent artwork retains its alpha channel. The initial brief and pose edit are saved in `assets/mascot-prompts.md`.
