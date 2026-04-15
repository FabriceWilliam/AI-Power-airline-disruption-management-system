# =============================================================
# rebooking_agent.py
# Delta Airlines — Intelligent Disruption Management System
# Agent 3: Rebooking Agent
# =============================================================

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List

from src.state.agent_state import AgentState


def get_db_connection() -> sqlite3.Connection:
    base_dir = Path(__file__).resolve().parent.parent.parent
    db_path  = str(base_dir / "database" / "delta_disruption.db")
    db_path  = db_path.replace("\\", "/")
    return sqlite3.connect(db_path)


AVAILABLE_FLIGHTS = [
    {"flight": "DL401",  "dep": "14:30", "arr": "17:45", "seats": 12},
    {"flight": "DL567",  "dep": "16:00", "arr": "19:20", "seats": 4},
    {"flight": "DL723",  "dep": "17:45", "arr": "21:00", "seats": 8},
    {"flight": "DL891",  "dep": "19:30", "arr": "22:45", "seats": 2},
    {"flight": "DL1043", "dep": "21:00", "arr": "00:15", "seats": 15},
]


def find_best_alternative(passenger: dict) -> dict:
    available = [f for f in AVAILABLE_FLIGHTS if f["seats"] > 0]

    if not available:
        return None

    special_need   = passenger.get("special_need", "NONE")
    has_connection = passenger.get("has_connection", 0)
    loyalty_tier   = passenger.get("loyalty_tier", "GENERAL")

    if special_need in ("MEDICAL", "WHEELCHAIR"):
        chosen = available[0]
        reason = f"Priority boarding: {special_need} requirement. Earliest available seat secured."
    elif has_connection:
        chosen = available[0]
        reason = "Earliest available flight selected to minimize connection risk."
    elif loyalty_tier in ("DIAMOND", "PLATINUM"):
        chosen = max(available, key=lambda f: f["seats"])
        reason = f"Premium member {loyalty_tier}: flight with best seat availability selected."
    else:
        chosen = available[0]
        reason = "Earliest available alternative flight assigned."

    return {
        "passenger_id":     passenger["passenger_id"],
        "original_flight":  passenger["flight_id"],
        "origin":           passenger.get("origin", ""),
        "destination":      passenger.get("destination", ""),
        "disruption_type":  passenger.get("disruption_type", ""),
        "severity":         passenger.get("severity", 0),
        "priority_score":   passenger.get("priority_score", 0),
        "new_flight":       chosen["flight"],
        "new_departure":    chosen["dep"],
        "new_arrival":      chosen["arr"],
        "selection_reason": reason,
        "proposed_at":      datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status":           "PROPOSED",
    }


def rebooking_agent(state: AgentState) -> dict:
    print("Rebooking Agent: Generating proposals...")

    error_log           = list(state.get("error_log", []))
    rebooking_proposals = []

    try:
        if state.get("assessment_status") != "scored":
            print("Rebooking Agent: No scored passengers. Skipping.")
            return {
                "rebooking_proposals": [],
                "rebooking_status":    "skipped",
                "current_step":        "notification",
            }

        passenger_queue = state.get("passenger_queue", [])

        if not passenger_queue:
            print("Rebooking Agent: Passenger queue is empty.")
            return {
                "rebooking_proposals": [],
                "rebooking_status":    "skipped",
                "current_step":        "notification",
            }

        processed = 0
        skipped   = 0

        for passenger in passenger_queue:
            proposal = find_best_alternative(passenger)
            if proposal:
                rebooking_proposals.append(proposal)
                processed += 1
            else:
                error_log.append(
                    f"No available flight for {passenger['passenger_id']}"
                )
                skipped += 1

        print(f"Rebooking Agent: {processed} proposals generated.")
        print(f"Rebooking Agent: {skipped} passengers could not be rebooked.")

    except Exception as e:
        error_msg = f"Rebooking Agent error: {str(e)}"
        error_log.append(error_msg)
        print(error_msg)

    return {
        "rebooking_proposals": rebooking_proposals,
        "rebooking_status":    "proposed" if rebooking_proposals else "error",
        "current_step":        "notification",
        "error_log":           error_log,
    }


if __name__ == "__main__":
    from src.agents.detection_agent  import detection_agent, create_initial_state
    from src.agents.assessment_agent import assessment_agent

    print("=" * 50)
    print("Testing Rebooking Agent standalone")
    print("=" * 50)

    state  = create_initial_state()
    state  = {**state, **detection_agent(state)}
    state  = {**state, **assessment_agent(state)}
    result = rebooking_agent(state)

    print(f"\nResults:")
    print(f"  Proposals generated : {len(result['rebooking_proposals']):,}")
    print(f"  Rebooking status    : {result['rebooking_status']}")
    print(f"  Next step           : {result['current_step']}")
    print(f"  Errors              : {len(result['error_log'])}")

    if result["rebooking_proposals"]:
        print(f"\nTop 5 Rebooking Proposals:")
        for i, p in enumerate(result["rebooking_proposals"][:5], 1):
            print(f"  {i}. {p['passenger_id']:12} | "
                  f"score={p['priority_score']:3} | "
                  f"{p['original_flight']:8} → {p['new_flight']:8} | "
                  f"dep={p['new_departure']} | "
                  f"{p['status']}")

    print("\nRebooking Agent test complete.")

