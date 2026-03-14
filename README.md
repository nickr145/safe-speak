# Safe Speak

AI-powered phone call practice for newcomers. Practice realistic phone conversations (doctor, landlord, pharmacy, etc.) with voice input, Claude for dialogue, and optional bilingual replies (English + another language) with ElevenLabs TTS.

## Features

- **Voice in, voice out**: Record your turn → ElevenLabs STT → Claude reply → ElevenLabs TTS (MP3).
- **Call scenarios**: Doctor's office, transit info, landlord, school absence, pharmacy, utility company.
- **Bilingual mode**: Optional `target_language` (e.g. `"French"`, `"Spanish"`) returns both English and translated replies.
- **REST API**: Start a session, send audio or text turns, get hints, end call with debrief.

## Requirements

- Python 3.10+
- API keys: **Anthropic** (Claude), **ElevenLabs** (STT + TTS; enable Speech-to-Text in your ElevenLabs account)

## Setup

1. **Clone and enter the project**

   ```bash
   cd safe-speak
   ```

2. **Create a virtual environment and install dependencies**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment**

   Copy `.env.example` to `.env` in the project root and set your keys:

   ```bash
   cp .env.example .env
   ```

   Edit `.env`:

   ```
   ANTHROPIC_API_KEY=your_anthropic_key
   ELEVENLABS_API_KEY=your_elevenlabs_key
   ```

   Optional: set `CORS_ORIGINS` as a JSON array of allowed origins (defaults include common localhost ports).

4. **Run the API**

   ```bash
   uvicorn app.main:app --reload
   ```

   API base URL: `http://127.0.0.1:8000`  
   Docs: `http://127.0.0.1:8000/docs`

## API overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/scenarios` | List available call scenarios |
| POST | `/api/call/start` | Start a call (JSON: `scenario_id`, optional `target_language`) |
| POST | `/api/call/start/simple?scenario_id=...&target_language=...` | Start call via query params (no JSON body) |
| POST | `/api/call/turn?session_id=...` | Send audio (multipart form field `audio`) → get `user_text`, `ai_text`, `ai_text_translated` |
| POST | `/api/call/turn/text?session_id=...&text=...` | Send text turn instead of audio |
| POST | `/api/call/hint` | Get a hint (JSON: `session_id`) |
| POST | `/api/call/end` | End call and get debrief (JSON: `session_id`) |
| POST | `/api/stt/transcribe` | Standalone STT (multipart form field `audio`) |
| POST | `/api/tts/synthesize` | Standalone TTS (JSON: `text`, optional `voice_id`) → returns MP3 |
| GET | `/api/health` | Health check |

### Example: voice turn

```bash
# Start (with optional French translation)
curl -X POST "http://127.0.0.1:8000/api/call/start" \
  -H "Content-Type: application/json" \
  -d '{"scenario_id": "doctor", "target_language": "French"}'

# Send audio (use the session_id from above)
curl -X POST "http://127.0.0.1:8000/api/call/turn?session_id=YOUR_SESSION_ID" \
  -F "audio=@recording.webm;type=audio/webm"
```

Response includes `user_text` (transcribed), `ai_text` (English), and `ai_text_translated` (e.g. French) when `target_language` was set.

## Test scripts

Scripts live under `app/test_scripts/`. Run from the **project root** with the API already running.

- **`demo_loop.py`** – Starts a session and sends a fixed MP3 (`eleven_test.mp3`) for a few turns, then prints debrief. Good for sanity-checking the pipeline.
- **`voice_roundtrip.py`** – Full loop: record from mic (5s) → STT → Claude (bilingual French) → TTS → save English and French MP3s. Requires `sounddevice` and `soundfile` (install if needed: `pip install sounddevice soundfile`).
- **`test.html`** – Simple browser UI: start session, record in browser, send to `/api/call/turn`, show transcript and AI reply. Serve over HTTP (e.g. `python3 -m http.server 8001`) and open `http://127.0.0.1:8001/app/test_scripts/test.html` (or wherever you placed it) so CORS and mic work.

Example:

```bash
# Terminal 1
uvicorn app.main:app --reload

# Terminal 2 (from project root)
python3 app/test_scripts/voice_roundtrip.py
```

## Project structure

```
safe-speak/
├── app/
│   ├── main.py          # FastAPI app, routes, CORS
│   ├── config.py        # Settings (env, CORS origins)
│   ├── schemas.py       # Pydantic request/response models
│   ├── call_manager.py  # Call session state, process_user_turn
│   ├── llm.py           # Claude system prompt, get_ai_response, goal check
│   ├── scenarios.py     # Scenario definitions (doctor, landlord, etc.)
│   ├── stt.py           # ElevenLabs Scribe v2 (speech-to-text)
│   ├── tts.py           # ElevenLabs text-to-speech
│   └── test_scripts/    # demo_loop, voice_roundtrip, test.html
├── .env.example
├── requirements.txt
└── README.md
```

## Empty transcript / 400 handling

If the user sends silence or unintelligible audio, STT may return an empty string. The API no longer returns 400 in that case: it logs a warning, substitutes `"I didn't catch that."` as the user turn, and continues so Claude can ask the user to repeat or clarify.

## License

See repository license file.
