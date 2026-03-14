"""Conversation AI module using Anthropic Claude API."""

import anthropic

from app.config import settings
from app.scenarios import Scenario

_client: anthropic.Anthropic | None = None

MODEL = "claude-sonnet-4-20250514"


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    return _client


def _build_system_prompt(scenario: Scenario, target_language: str | None = None) -> str:
    """Build the system prompt for Claude, optionally requesting bilingual replies."""
    lang_rule = ""
    if target_language:
        lang_rule = (
            f"- For every reply, first respond in clear English only.\n"
            f"- Then on a new line starting with 'In {target_language}: ' "
            f"give a natural translation of the same reply in {target_language}.\n"
        )

    return (
        f"You are {scenario.persona_name}, a {scenario.role} at {scenario.organization}. "
        f"You are speaking with a newcomer over the phone. "
        f"Your job is to complete this interaction: {scenario.call_goal}. "
        f"Rules:\n"
        f"{lang_rule}"
        f"- Speak as a real {scenario.role} would — professional, clear, slightly slow pacing.\n"
        f"- Keep each response under 30 words.\n"
        f"- If the user says something unclear, ask ONE clarifying question.\n"
        f'- If the user is silent or confused, offer a helpful prompt: \"Are you looking for...\".\n'
        f"- When the goal is achieved, confirm it and say goodbye warmly.\n"
        f"- If the user makes a language error, respond naturally — do not correct grammar."
    )


def get_ai_response(
    scenario: Scenario,
    conversation_history: list[dict],
    target_language: str | None = None,
) -> str:
    """Get AI persona response for the current conversation turn.

    Args:
        scenario: The active call scenario.
        conversation_history: List of {"role": "user"|"assistant", "content": str} dicts.

    Returns:
        AI persona's response text.
    """
    client = _get_client()

    response = client.messages.create(
        model=MODEL,
        max_tokens=150,
        system=_build_system_prompt(scenario, target_language=target_language),
        messages=conversation_history,
    )

    return response.content[0].text


def check_goal_achieved(scenario: Scenario, conversation_history: list[dict]) -> bool:
    """Check if the call goal has been achieved based on conversation history.

    Args:
        scenario: The active call scenario.
        conversation_history: Full conversation history.

    Returns:
        True if the goal appears to be achieved.
    """
    if len(conversation_history) < 4:
        return False

    client = _get_client()

    transcript = "\n".join(
        f"{'Caller' if m['role'] == 'user' else scenario.persona_name}: {m['content']}"
        for m in conversation_history
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=10,
        system=(
            "You evaluate phone call transcripts. "
            f"The goal of this call is: {scenario.call_goal}. "
            "Based on the transcript, has this goal been achieved? "
            "Reply with only YES or NO."
        ),
        messages=[{"role": "user", "content": transcript}],
    )

    return response.content[0].text.strip().upper().startswith("YES")


def generate_hint(scenario: Scenario, conversation_history: list[dict]) -> str:
    """Generate a contextual hint for the user based on conversation state.

    Args:
        scenario: The active call scenario.
        conversation_history: Full conversation history.

    Returns:
        A hint string the user could say next.
    """
    # Use pre-written hints based on conversation length
    turn_count = len([m for m in conversation_history if m["role"] == "user"])
    hints = scenario.hint_phrases
    idx = min(turn_count, len(hints) - 1)
    return hints[idx]
