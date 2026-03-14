import pathlib

import requests


BASE_URL = "http://127.0.0.1:8000"
# Project root: /safe-speak
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]
AUDIO_PATH = PROJECT_ROOT / "app/test_audio_files/eleven_test.mp3"


def main() -> None:
    scenario_id = "doctor"

    # Start a new call session
    resp = requests.post(
        f"{BASE_URL}/api/call/start",
        json={"scenario_id": scenario_id},
        timeout=30,
    )
    resp.raise_for_status()
    start_data = resp.json()

    session_id = start_data["session_id"]
    print(f"Started session: {session_id}")
    print(f"Greeting: {start_data['greeting_text']}\n")

    # Loop a few turns, always sending the same sample audio
    for turn_idx in range(3):
        print(f"=== Turn {turn_idx + 1} ===")

        with AUDIO_PATH.open("rb") as f:
            files = {
                "audio": ("eleven_test.mp3", f, "audio/mpeg"),
            }
            resp = requests.post(
                f"{BASE_URL}/api/call/turn",
                params={"session_id": session_id},
                files=files,
                timeout=60,
            )
        resp.raise_for_status()
        turn = resp.json()

        print(f"Transcribed user_text: {turn['user_text']}")
        print(f"Claude ai_text:        {turn['ai_text']}")
        print(f"State: {turn['state']} | goal_achieved: {turn['goal_achieved']}")

        # For now, we just reuse eleven_test.mp3 as the "AI audio" placeholder.
        print(f"(Would play {AUDIO_PATH.name} as AI response audio)\n")

        if turn["goal_achieved"]:
            break

    # End the call and print debrief
    resp = requests.post(
        f"{BASE_URL}/api/call/end",
        json={"session_id": session_id},
        timeout=30,
    )
    resp.raise_for_status()
    end_data = resp.json()

    print("=== Debrief ===")
    print(end_data["debrief"])


if __name__ == "__main__":
    main()

