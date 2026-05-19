# Voice (STT/TTS)

Star Lord ships **open‑source voice adapters** with optional dependencies. You can choose the engine you prefer.

## Speech‑to‑Text (STT)
### Vosk (offline)
- Adapter: `VoskSpeechRecognizer`
- Supports file transcription and microphone input (if `sounddevice` is installed).

Minimal install:
```bash
pip install vosk
```
Optional mic input:
```bash
pip install sounddevice
```

### Whisper (offline, heavier)
- Adapter: `WhisperSpeechRecognizer`
- Supports file transcription.

Minimal install:
```bash
pip install openai-whisper
```

## Text‑to‑Speech (TTS)
### Piper (offline, CLI)
- Adapter: `PiperSpeechSynthesizer`
- Requires `piper` on PATH and a model file.

Usage:
1) Download a Piper model (e.g., `.onnx` + `.json`)
2) Set `tts_model_path` in `Settings`

## Configuration
Update settings in `src/starlord/config/settings.py` or create your own settings object:
- `stt_engine`: `vosk` | `whisper`
- `stt_model_path`: path to STT model
- `tts_engine`: `piper`
- `tts_model_path`: path to TTS model
- `tts_output_path`: output WAV path

## Notes
- Adapters are **optional** and keep the core lightweight.
- For now, the CLI only uses **TTS** output when `--voice` is enabled.
