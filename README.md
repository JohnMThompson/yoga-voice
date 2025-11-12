# yoga-voice

This small project builds a complete yoga audio session from a supplied script by rendering each script segment with TTS and stitching the pieces together into a single audio file.

The project was a bit of an experiment, and while it did generate an audio file, the voice quality was low. I attempted to find new ways to encode the audio with a more realistic voice, but haven't finished it.

There are three example approaches included so you can choose the TTS backend that fits your environment:

- `make_yoga_audio.py` — offline/system TTS using `pyttsx3` and `pydub` (cross-platform; uses your OS voices).
- `make_yoga_audio_edge.py` — uses `edge_tts` (Microsoft Neural voices) to produce high-quality speech (requires internet/access to Edge TTS endpoints).
- `make_yoga_audio_piper.py` — uses the `piper` CLI for local neural TTS (requires Piper binary and voice models installed locally).

Each script renders a list of script segments (text + hold/pause duration) and concatenates them into a single `.wav` (and optionally `.mp3`) file.

## What's in this repository

- `make_yoga_audio.py` — simple offline flow using `pyttsx3` and `pydub`.
- `make_yoga_audio_edge.py` — async Edge TTS flow using `edge_tts`.
- `make_yoga_audio_piper.py` — wrapper that calls the `piper` CLI and stitches output with `pydub`.
- `test_edge_list.py` — small helper that lists voices available to `edge_tts` (useful for testing access).
- `yoga_flow_audio_full.wav` / `.mp3` — example outputs (may be present in the repo from previous runs).

## Requirements

- Python 3.8+
- pip packages: `pydub` plus one or more TTS packages depending on which script you plan to run:
  - `pyttsx3` (for `make_yoga_audio.py`)
  - `edge-tts` (package name: `edge-tts`) for `make_yoga_audio_edge.py`
  - `piper` is an external CLI, not a pip package — see the Piper project for installation and models (for `make_yoga_audio_piper.py`).
- `ffmpeg` (recommended) — `pydub` needs it for MP3 export and robust audio handling.

Install the typical Python dependencies with:

```bash
python3 -m pip install pydub pyttsx3 edge-tts
```

On Debian/Ubuntu you can install ffmpeg with:

```bash
sudo apt-get update && sudo apt-get install ffmpeg
```

If you plan to use `piper`, follow Piper's documentation to install the `piper` binary and download a voice model (the example script expects models under `~/piper-voices/`).

## Quick start

1. Pick the script you want to use (system TTS, Edge TTS, or Piper).
2. Ensure dependencies are installed and any external tools (ffmpeg, piper) are available on your PATH.
3. Run the script. Examples:

```bash
# Offline/system TTS (pyttsx3)
python3 make_yoga_audio.py

# Microsoft Edge Neural voices (async)
python3 make_yoga_audio_edge.py

# Piper (local neural TTS, requires piper CLI + model)
python3 make_yoga_audio_piper.py
```

Each script writes a WAV file (and attempts an MP3 export if `ffmpeg` is installed). Output filenames are defined at the top of each script (for example: `yoga_flow_audio_full.wav`).

## Notes and tips

- `make_yoga_audio.py` uses `pyttsx3`, which will use the OS's installed voices. Voice selection and quality depend on the platform and available voices.
- `edge_tts` provides higher-quality neural voices (and different voice names are available). Use `test_edge_list.py` or the `edge_tts.list_voices()` API to see available voices.
- `piper` runs locally and can produce very natural speech if you have a good voice model; the script expects the `piper` CLI on PATH and model files in `~/piper-voices/` (adjust `VOICE_MODEL` and `VOICE_JSON` in the script as needed).
- MP3 export requires `ffmpeg` to be present. If MP3 export fails, a WAV will still be produced.
- `pydub` uses simple in-memory concatenation — for very long sessions you may need to stream or write intermediate files to keep memory usage under control.

## Troubleshooting

- If `pyttsx3` produces no audio, ensure your system TTS engines are installed and accessible. On Linux, installing `espeak`/`espeak-ng` often helps.
- If `edge_tts` fails to contact the service, check network connectivity and try `test_edge_list.py` to enumerate voices.
- If `piper` fails, make sure the `piper` executable is in your PATH and the voice model files are correct and readable.

## Extending

You can adapt the `segments` list in any script to provide different text and hold durations. The scripts are intentionally simple so you can:

- Add background music or longer room tone overlays.
- Insert per-segment audio effects, volume adjustments, or head/room filters via `pydub`.
- Split the session into multiple files or dynamically build segments from markdown or structured input.

## License / attribution

This repository contains utility scripts for assembling TTS audio. Reuse as you like.
