# =============================================================
# notification_agent.py
# Delta Airlines — Intelligent Disruption Management System
# Agent 4: Notification Agent
# Responsibility: Generate personalized messages for passengers
# =============================================================

import os
from pathlib import Path
from datetime import datetime
from typing import List
from dotenv import load_dotenv
import anthropic

from src.state.agent_state import AgentState

# Load API key from .env
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")


# -------------------------------------------------------------
# MESSAGE GENERATOR
# Uses Claude API to write empathetic, personalized messages
# -------------------------------------------------------------

def generate_passenger_message(proposal: dict) -> str:
    """
    Calls Claude API to generate a personalized disruption message.
    Falls back to a template message if API call fails.
    """
    client = anthropic.Anthropic(
        api_key=os.getenv("jwMX5t9E_rd_E258ycmCAgJY9A_zhb6n50O5gHrKGE8eJJiuV3RLHQiQou7xbKO8z5NjqzzHjKX1XpTjjq4IGQ-ACEzDAAA")
    )

    # Build context for Claude
    prompt = f"""You are a Delta Airlines customer service AI.
Write a short, empathetic, professional message to a passenger affected by a flight disruption.

Passenger details:
- Passenger ID: {proposal['passenger_id']}
- Original flight: {proposal['original_flight']}
- Route: {proposal['origin']} → {proposal['destination']}
- Disruption type: {proposal['disruption_type']}
- New flight: {proposal['new_flight']}
- New departure: {proposal['new_departure']}
- New arrival: {proposal['new_arrival']}
- Rebooking reason: {proposal['selection_reason']}

Requirements:
- Maximum 3 sentences
- Empathetic but professional tone
- Include the new flight details clearly
- End with an offer to help further
- Do NOT use the passenger ID in the message
"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text.strip()

    except Exception as e:
        # Fallback template if API fails
        return (
            f"Dear Passenger, we sincerely apologize for the disruption "
            f"to your flight {proposal['original_flight']}. "
            f"We have rebooked you on flight {proposal['new_flight']} "
            f"departing at {proposal['new_departure']}. "
            f"Please contact us if you need further assistance."
        )


# -------------------------------------------------------------
# LANGGRAPH NODE — THE NOTIFICATION AGENT
# -------------------------------------------------------------

def notification_agent(state: AgentState) -> dict:
    """
    LangGraph node: Notification Agent.
    Generates personalized messages for each rebooked passenger.
    Updates shared state with notification results.
    """
    print("Notification Agent: Generating messages...")

    error_log          = list(state.get("error_log", []))
    notifications_sent = 0
    sample_messages    = []

    try:
        # Guard clause
        if state.get("rebooking_status") != "proposed":
            print("Notification Agent: No proposals to notify. Skipping.")
            return {
                "notifications_sent":  0,
                "notification_status": "skipped",
                "current_step":        "complete",
            }

        proposals = state.get("rebooking_proposals", [])

        if not proposals:
            return {
                "notifications_sent":  0,
                "notification_status": "skipped",
                "current_step":        "complete",
            }

        # Generate messages for top 5 passengers only
        # In production: send to all 1,008
        # In prototype: limit API calls to save cost
        for proposal in proposals[:5]:
            try:
                message = generate_passenger_message(proposal)
                notifications_sent += 1

                sample_messages.append({
                    "passenger_id": proposal["passenger_id"],
                    "flight":       proposal["new_flight"],
                    "message":      message,
                    "sent_at":      datetime.now().isoformat(),
                })

                print(f"  Notified: {proposal['passenger_id']} "
                      f"(score={proposal['priority_score']})")

            except Exception as e:
                error_log.append(
                    f"Notification failed for "
                    f"{proposal['passenger_id']}: {str(e)}"
                )

        print(f"Notification Agent: {notifications_sent} messages sent.")

    except Exception as e:
        error_msg = f"Notification Agent error: {str(e)}"
        error_log.append(error_msg)
        print(error_msg)

    return {
        "notifications_sent":  notifications_sent,
        "notification_status": "complete" if notifications_sent > 0 else "error",
        "current_step":        "complete",
        "error_log":           error_log,
    }


# -------------------------------------------------------------
# STANDALONE TEST
# -------------------------------------------------------------

if __name__ == "__main__":
    from src.agents.detection_agent  import detection_agent, create_initial_state
    from src.agents.assessment_agent import assessment_agent
    from src.agents.rebooking_agent  import rebooking_agent

    print("=" * 50)
    print("Testing Notification Agent standalone")
    print("=" * 50)

    # Run full pipeline
    state  = create_initial_state()
    state  = {**state, **detection_agent(state)}
    state  = {**state, **assessment_agent(state)}
    state  = {**state, **rebooking_agent(state)}
    result = notification_agent(state)

    print(f"\nResults:")
    print(f"  Notifications sent   : {result['notifications_sent']}")
    print(f"  Notification status  : {result['notification_status']}")
    print(f"  Pipeline complete    : {result['current_step']}")
    print(f"  Errors               : {len(result['error_log'])}")

    print("\nNotification Agent test complete.")
    
