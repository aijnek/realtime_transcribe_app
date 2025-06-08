# CLAUDE.md

指定がない場合は日本語で回答してください．
This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Structure

This is a realtime transcription application with a backend Python service using Google's Gemini Live API for real-time audio transcription.

- `backend/`: Python backend using uv for dependency management
  - `src/transcribe.py`: Main transcription module using Google GenAI Live API
  - `pyproject.toml`: Project dependencies and configuration
  - `.env`: Environment variables (contains GOOGLE_API_KEY)
- `frontend/`: Frontend application (currently empty)

## Development Commands

### Backend Development

Start the FastAPI WebSocket server:

```bash
cd backend
uv run python -m src.main
```

Test with microphone input:

```bash
cd backend
uv run python mic_test.py
```

Install dependencies:

```bash
cd backend
uv sync
```

## Environment Configuration

- Environment variables are loaded from `backend/.env`
- Required: `GOOGLE_API_KEY` for Google GenAI Live API
- The `load_dotenv()` call in `transcribe.py` expects to be run from the `backend/` directory

## Audio Transcription Architecture

The transcription system uses:
- **FastAPI + WebSocket**: Real-time audio data streaming
- **Google Gemini 2.0 Flash Live**: AI-powered transcription
- **Frontend audio collection**: Browser-based microphone capture (planned)
- **16kHz mono 16-bit PCM**: Audio format specification
- **Japanese language optimized**: Filler word removal and natural language correction