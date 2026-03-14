from dataclasses import dataclass


@dataclass
class Scenario:
    id: str
    title: str
    persona_name: str
    role: str
    organization: str
    call_goal: str
    greeting: str
    voice_id: str  # ElevenLabs voice ID
    hint_phrases: list[str]
    debrief_success: str
    debrief_partial: str


SCENARIOS: dict[str, Scenario] = {
    "doctor": Scenario(
        id="doctor",
        title="Doctor's Office",
        persona_name="Sarah",
        role="receptionist",
        organization="Riverside Family Clinic",
        call_goal="Help the caller book a checkup appointment for next week",
        greeting="Good morning, Riverside Family Clinic, this is Sarah speaking. How can I help you?",
        voice_id="EXAVITQu4vr4xnSDxMaL",  # Sarah - friendly female
        hint_phrases=[
            "You could say: I'd like to book an appointment please.",
            "Try saying: Do you have anything available next week?",
            "You could say: Yes, that time works for me.",
        ],
        debrief_success="Great call! You successfully booked your appointment. You handled the date and time negotiation really well.",
        debrief_partial="Good effort! You started the conversation well. Next time, try to confirm the date and time before hanging up.",
    ),
    "transit": Scenario(
        id="transit",
        title="Transit Info Line",
        persona_name="Michael",
        role="transit information agent",
        organization="City Transit Authority",
        call_goal="Help the caller find a bus route from their home to a specific address",
        greeting="Thank you for calling City Transit Authority. My name is Michael. How can I assist you today?",
        voice_id="TX3LPaxmHKxFdv7VOQHJ",  # Michael - professional male
        hint_phrases=[
            "You could say: I need to find a bus route to get somewhere.",
            "Try saying: I'm at the corner of Main Street. How do I get to the library?",
            "You could say: What time does the next bus come?",
        ],
        debrief_success="Great call! You got the route information you needed. You asked clear questions about the bus schedule.",
        debrief_partial="Good try! Next time, make sure to ask about transfer points and the fare.",
    ),
    "landlord": Scenario(
        id="landlord",
        title="Landlord Call",
        persona_name="Robert",
        role="landlord",
        organization="Pine Street Apartments",
        call_goal="Help the caller report a broken heater and find out when it will be fixed",
        greeting="Hello, this is Robert from Pine Street Apartments. What can I do for you?",
        voice_id="N2lVS1w4EtoT3dr4eOWO",  # Robert - neutral male
        hint_phrases=[
            "You could say: Hi, I'm calling about a problem in my apartment.",
            "Try saying: My heater is broken and it's very cold.",
            "You could say: When can someone come to fix it?",
        ],
        debrief_success="Great call! You reported the issue clearly and got a repair timeline. Well done!",
        debrief_partial="Good start! Next time, try to get a specific date for when the repair will happen.",
    ),
    "school": Scenario(
        id="school",
        title="School Absence",
        persona_name="Mrs. Johnson",
        role="school secretary",
        organization="Maple Leaf Elementary School",
        call_goal="Help the caller report their child absent due to illness",
        greeting="Good morning, Maple Leaf Elementary School, Mrs. Johnson speaking. How can I help you?",
        voice_id="EXAVITQu4vr4xnSDxMaL",  # Friendly female
        hint_phrases=[
            "You could say: I'm calling to report my child absent today.",
            "Try saying: My child's name is... and they are in grade...",
            "You could say: They are sick and should be back by Monday.",
        ],
        debrief_success="Great call! You reported the absence with all the details the school needed.",
        debrief_partial="Good effort! Remember to mention your child's name, grade, and when they'll return.",
    ),
    "pharmacy": Scenario(
        id="pharmacy",
        title="Pharmacy Refill",
        persona_name="Lisa",
        role="pharmacy technician",
        organization="HealthFirst Pharmacy",
        call_goal="Help the caller refill a prescription by phone",
        greeting="HealthFirst Pharmacy, this is Lisa. How can I help you?",
        voice_id="EXAVITQu4vr4xnSDxMaL",  # Fast-paced female
        hint_phrases=[
            "You could say: I'd like to refill my prescription please.",
            "Try saying: My prescription number is on the bottle label.",
            "You could say: I can pick it up this afternoon.",
        ],
        debrief_success="Great call! You refilled your prescription and confirmed the pickup time.",
        debrief_partial="Good try! Next time, have your prescription number ready before calling.",
    ),
    "utility": Scenario(
        id="utility",
        title="Utility Company",
        persona_name="David",
        role="customer service representative",
        organization="PowerGrid Energy Services",
        call_goal="Help the caller report a power outage at their home",
        greeting="Thank you for calling PowerGrid Energy Services. My name is David. How may I help you?",
        voice_id="TX3LPaxmHKxFdv7VOQHJ",  # Professional male
        hint_phrases=[
            "You could say: I'm calling to report a power outage.",
            "Try saying: The power went out about an hour ago at my address.",
            "You could say: Do you know when the power will come back?",
        ],
        debrief_success="Great call! You reported the outage and got an estimated time for power restoration.",
        debrief_partial="Good effort! Remember to confirm your address and ask for an estimated repair time.",
    ),
}


def get_scenario(scenario_id: str) -> Scenario | None:
    return SCENARIOS.get(scenario_id)


def list_scenarios() -> list[dict]:
    return [
        {"id": s.id, "title": s.title, "role": s.role, "organization": s.organization}
        for s in SCENARIOS.values()
    ]
