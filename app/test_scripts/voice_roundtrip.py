import pathlib
import time
from typing import Optional

import requests
import sounddevice as sd
import soundfile as sf


BASE_URL = "http://127.0.0.1:8000"
# Project root: /safe-speak
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]


def record_to_wav(path: pathlib.Path, duration: float = 5.0, sample_rate: int = 16000) -> None:
    """Record a short clip from the default microphone and save as WAV."""
    print(f"\nRecording for {duration} seconds...")
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="float32",
    )
    sd.wait()
    sf.write(path, audio, sample_rate)
    print(f"Saved recording to {path}")


def start_session(scenario_id: str = "doctor") -> dict:
    resp = requests.post(
        f"{BASE_URL}/api/call/start",
        json={"scenario_id": scenario_id},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def stt_transcribe(path: pathlib.Path) -> str:
    with path.open("rb") as f:
        files = {"audio": (path.name, f, "audio/wav")}
        resp = requests.post(f"{BASE_URL}/api/stt/transcribe", files=files, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data.get("text", "").strip()


def call_claude(session_id: str, user_text: str) -> dict:
    params = {"session_id": session_id, "text": user_text}
    resp = requests.post(f"{BASE_URL}/api/call/turn/text", params=params, timeout=60)
    resp.raise_for_status()
    return resp.json()


def tts_synthesize(text: str, out_path: pathlib.Path, voice_id: Optional[str] = None) -> None:
    payload = {"text": text}
    if voice_id is not None:
        payload["voice_id"] = voice_id

    resp = requests.post(f"{BASE_URL}/api/tts/synthesize", json=payload, timeout=60)
    resp.raise_for_status()

    out_path.write_bytes(resp.content)
    print(f"Saved AI reply audio to {out_path}")


def main() -> None:
    print("Starting voice roundtrip demo (ElevenLabs STT + Claude + ElevenLabs TTS)")
    session = start_session("doctor")
    session_id = session["session_id"]
    greeting = session["greeting_text"]
    scenario_title = session["scenario_title"]

    print(f"\nScenario: {scenario_title}")
    print(f"Session: {session_id}")
    print(f"Greeting: {greeting}\n")

    tmp_audio = PROJECT_ROOT / "tmp_user.wav"

    turn_idx = 0
    try:
        while True:
            cmd = input("Press Enter to record, or type 'q' to quit: ").strip().lower()
            if cmd in {"q", "quit", "exit"}:
                break

            turn_idx += 1

            record_to_wav(tmp_audio, duration=5.0)

            # STT
            user_text = stt_transcribe(tmp_audio)
            print(f"\nYou said: {user_text}")
            if not user_text:
                print("Nothing transcribed; try again.")
                continue

            # Claude via backend call manager
            turn = call_claude(session_id, user_text)
            ai_text = turn["ai_text"]
            print(f"Claude reply: {ai_text}")

            # TTS
            reply_path = PROJECT_ROOT / f"reply_{int(time.time())}.mp3"
            tts_synthesize(ai_text, reply_path)
            print()

    finally:
        # Optionally end the call for a debrief
        try:
            resp = requests.post(
                f"{BASE_URL}/api/call/end",
                json={"session_id": session_id},
                timeout=30,
            )
            if resp.ok:
                end = resp.json()
                print("\n=== Debrief ===")
                print(end["debrief"])
        except Exception:
            pass


if __name__ == "__main__":
    main()

