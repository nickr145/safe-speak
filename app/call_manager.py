"""Call state machine managing the lifecycle of a simulated phone call."""

import uuid
from enum import Enum
from dataclasses import dataclass, field

from app.scenarios import Scenario, get_scenario


class CallState(str, Enum):
    IDLE = "IDLE"
    RINGING = "RINGING"
    GREETING = "GREETING"
    EXCHANGE = "EXCHANGE"
    HINT_CHECK = "HINT_CHECK"
    RESOLUTION = "RESOLUTION"
    DEBRIEF = "DEBRIEF"
    RETRY = "RETRY"


@dataclass
class CallSession:
    session_id: str
    scenario: Scenario
    state: CallState = CallState.IDLE
    conversation_history: list[dict] = field(default_factory=list)
    turn_count: int = 0
    goal_achieved: bool = False
    max_turns: int = 8


# In-memory session store
_sessions: dict[str, CallSession] = {}


def create_session(scenario_id: str) -> CallSession:
    """Create a new call session for a given scenario."""
    scenario = get_scenario(scenario_id)
    if scenario is None:
        raise ValueError(f"Unknown scenario: {scenario_id}")

    session_id = str(uuid.uuid4())
    session = CallSession(session_id=session_id, scenario=scenario)
    _sessions[session_id] = session
    return session


def get_session(session_id: str) -> CallSession | None:
    return _sessions.get(session_id)


def start_call(session: CallSession) -> str:
    """Transition from IDLE -> RINGING -> GREETING and return the greeting text."""
    session.state = CallState.RINGING
    # Immediately transition to GREETING (ringing delay handled by frontend)
    session.state = CallState.GREETING

    greeting = session.scenario.greeting
    session.conversation_history.append(
        {"role": "assistant", "content": greeting}
    )
    session.state = CallState.EXCHANGE
    return greeting


def process_user_turn(session: CallSession, user_text: str) -> dict:
    """Process a user's spoken turn and get the AI response.

    Returns dict with: ai_text, state, goal_achieved, hint
    """
    from app.llm import get_ai_response, check_goal_achieved

    session.conversation_history.append({"role": "user", "content": user_text})
    session.turn_count += 1

    # Get AI response
    ai_text = get_ai_response(session.scenario, session.conversation_history)
    session.conversation_history.append({"role": "assistant", "content": ai_text})

    # Check if goal is achieved
    goal_achieved = check_goal_achieved(session.scenario, session.conversation_history)
    session.goal_achieved = goal_achieved

    if goal_achieved:
        session.state = CallState.RESOLUTION

    if session.turn_count >= session.max_turns and not goal_achieved:
        session.state = CallState.RESOLUTION

    return {
        "ai_text": ai_text,
        "state": session.state.value,
        "goal_achieved": goal_achieved,
        "hint": None,
    }


def get_hint(session: CallSession) -> str:
    """Get a hint for the current conversation state."""
    from app.llm import generate_hint

    session.state = CallState.HINT_CHECK
    hint = generate_hint(session.scenario, session.conversation_history)
    session.state = CallState.EXCHANGE
    return hint


def end_call(session: CallSession) -> dict:
    """End the call and return debrief info."""
    session.state = CallState.DEBRIEF

    debrief = (
        session.scenario.debrief_success
        if session.goal_achieved
        else session.scenario.debrief_partial
    )

    transcript = [
        {"role": m["role"], "content": m["content"]}
        for m in session.conversation_history
    ]

    return {
        "state": session.state.value,
        "debrief": debrief,
        "transcript": transcript,
    }


def delete_session(session_id: str) -> None:
    _sessions.pop(session_id, None)
