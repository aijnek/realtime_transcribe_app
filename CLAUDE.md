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

Run from the `backend/` directory to ensure proper environment variable loading:

```bash
cd backend
python src/transcribe.py
```

Or as a module:

```bash
cd backend
python -m src.transcribe
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
- Google Gemini 2.0 Flash Live model for real-time transcription
- PyAudio for microphone input (16kHz, mono, 16-bit)
- Real-time streaming with automatic speech detection
- Japanese language optimized with filler word removal and natural language correction