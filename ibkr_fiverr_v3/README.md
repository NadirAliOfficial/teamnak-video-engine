# IBKR Fiverr explainer — lip sync revision

30-second anonymous service explainer with platform logos, neural narration and a speech-driven robot mascot. No personal or company name appears in the rendered video, narration, captions or cover.

## Deliverables

- `output/ibkr_fiverr_lipsync_v3.mp4`: final 1920×1080, 60 fps, H.264 / AAC stereo.
- `output/ibkr_fiverr_preview.mp4`: smaller 720p30 preview.
- `output/thumbnail.png`: matching anonymous cover.
- `output/ibkr_fiverr.srt`: subtitles.
- `output/lip_sync_check.jpg`: visual check of closed, A, E, O, U and F/V mouth shapes.
- `assets/mascot.png`, `assets/mascot_presenter.png`: edited transparent faceplate assets.

## Lip sync implementation

The original static smiles were removed from both poses using the built-in ImageGen tool. The renderer draws an emissive mouth on each robot’s glass faceplate, within the same local transforms as its head and body.

`lip_sync.py` uses the speech engine’s word timestamps, CMUdict pronunciations and the actual narration waveform to generate a 60 fps viseme track. Vowels, rounded vowels, lip closures, F/V and tongue shapes have different mouth geometry. Bilabial closures stay crisp. The audio envelope controls openness, and silent frames remain closed. Within-word phoneme timing is a weighted estimate; it is not forced phoneme alignment.

The build verifies that the track contains 1800 finite frames, substantial speech articulation and no mouth opening during silent audio. `output/lip_sync.json` preserves the timing events for inspection.

## Script changes

Introduction: “I build custom trading bots for Interactive Brokers.”

Final invitation: “Ready to automate? Send your strategy on Fiverr.”

## Rebuild

```sh
../.venv/bin/python build.py
```

Dependencies are pinned in `requirements.txt`, including CMUdict; FFmpeg must be installed. Change text in `voice.py` and remove the associated cached speech audio and word metadata before rebuilding. Edit visual compositions and mouth geometry in `render.py`.

Official logos are retained from the previous cut: Interactive Brokers’ white wordmark, TradingView’s media kit and Python’s community logo. Only their displayed size changes; proportions are preserved.

Python uses the official transparent two-snakes PNG directly, without a white box or background: https://s3.dualstack.us-east-2.amazonaws.com/pythondotorg-assets/media/community/logos/python-logo-only.png

## Mascot edits

Both assets were edited with the built-in ImageGen tool. The exact edit prompts are recorded in [mascot-edit-prompts.md](assets/mascot-edit-prompts.md). The original video versions are preserved in their existing folders.
