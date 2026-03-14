import pathlib
import sys

import requests


BASE_URL = "http://127.0.0.1:8000"
PROJECT_ROOT = pathlib.Path(__file__).parent


def transcribe_file(path: pathlib.Path) -> str:
    with path.open("rb") as f:
        files = {"audio": (path.name, f, "audio/mpeg")}
        resp = requests.post(f"{BASE_URL}/api/stt/transcribe", files=files, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data.get("text", "").strip()


def main() -> None:
    if len(sys.argv) > 1:
        audio_path = pathlib.Path(sys.argv[1])
    else:
        audio_path = PROJECT_ROOT / "eleven_test.mp3"

    if not audio_path.exists():
        print(f"Audio file not found: {audio_path}")
        sys.exit(1)

    print(f"Using audio file: {audio_path}")
    print("Press Enter to run a turn, or type 'q' to quit.")

    while True:
        cmd = input("> ").strip().lower()
        if cmd in {"q", "quit", "exit"}:
            break

        try:
            user_text = transcribe_file(audio_path)
        except Exception as e:  # noqa: BLE001
            print(f"Error calling STT API: {e}")
            continue

        print(f"\nYou said: {user_text}")
        sample_reply = "Thanks for sharing that. This is a placeholder reply while we wire in the full AI."
        print(f"Sample reply: {sample_reply}\n")


if __name__ == "__main__":
    main()

