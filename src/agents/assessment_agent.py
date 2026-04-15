 # =============================================================
# assessment_agent.py
# Delta Airlines — Intelligent Disruption Management System
# Agent 2: Assessment Agent
# Responsibility: Score and prioritize affected passengers
# =============================================================

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List

# Import shared state from single source of truth
from src.state.agent_state import AgentState


# -------------------------------------------------------------
# DATABASE CONNECTION
# Same pattern as Detection Agent — consistent across all agents
# -------------------------------------------------------------

def get_db_connection() -> sqlite3.Connection:
    """Returns a connection to the Delta disruption database."""
    base_dir = Path(__file__).resolve().parent.parent.parent
    db_path  = str(base_dir / "database" / "delta_disruption.db")
    db_path  = db_path.replace("\\", "/")
    return sqlite3.connect(db_path)


# -------------------------------------------------------------
# PRIORITY SCORING FORMULA
# Identical to the SQL formula in Notebook 3 Cell 3
# -------------------------------------------------------------

SPECIAL_NEED_SCORES = {
    "MEDICAL":     30,
    "WHEELCHAIR":  20,
    "INFANT":      15,
    "NONE":         0,
}

LOYALTY_SCORES = {
    "DIAMOND":  25,
    "PLATINUM": 20,
    "GOLD":     15,
    "SILVER":   10,
    "GENERAL":   0,
}


def compute_priority_score(passenger: dict) -> int:
    """
    Computes a numeric priority score for a passenger.
    Higher score = higher rebooking priority.

    Formula:
        (severity × 10)
        + special_need_score
        + loyalty_score
        + connection_score
    """
    severity       = passenger.get("severity", 0) or 0
    special_need   = passenger.get("special_need", "NONE")
    loyalty_tier   = passenger.get("loyalty_tier", "GENERAL")
    has_connection = passenger.get("has_connection", 0)

    score = (severity * 10)
    score += SPECIAL_NEED_SCORES.get(special_need, 0)
    score += LOYALTY_SCORES.get(loyalty_tier, 0)
    score += 20 if has_connection else 0

    return score
# -------------------------------------------------------------
# PASSENGER DATA RETRIEVAL
# Fetches all passengers from the database and scores them
# -------------------------------------------------------------

def fetch_and_score_passengers() -> List[dict]:
    """
    Fetches all passengers from the database,
    computes their priority score, and returns
    a ranked list sorted by score descending.
    """
    conn = get_db_connection()
    try:
        cursor = conn.execute("""
            SELECT
                passenger_id,
                flight_id,
                origin,
                destination,
                disruption_type,
                severity,
                loyalty_tier,
                special_need,
                has_connection
            FROM passengers
            WHERE disruption_type IN (
                'CANCELLATION',
                'DELAY_CRITICAL',
                'DELAY_MAJOR'
            )
            ORDER BY severity DESC
        """)
        columns    = [desc[0] for desc in cursor.description]
        passengers = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # Compute priority score for each passenger
        for passenger in passengers:
            passenger["priority_score"] = compute_priority_score(passenger)

        # Sort by priority score descending
        passengers.sort(key=lambda p: p["priority_score"], reverse=True)

        return passengers

    except Exception as e:
        print(f"Assessment Agent DB error: {e}")
        return []
    finally:
        conn.close()


# -------------------------------------------------------------
# LANGGRAPH NODE — THE ASSESSMENT AGENT
# -------------------------------------------------------------

def assessment_agent(state: AgentState) -> dict:
    """
    LangGraph node: Assessment Agent.
    Scores and ranks all affected passengers.
    Updates shared state with prioritized queue.
    """
    print("Assessment Agent: Scoring passengers...")

    error_log = list(state.get("error_log", []))

    try:
        # Check Detection Agent ran successfully
        if state.get("detection_status") != "disruptions_found":
            print("Assessment Agent: No disruptions detected. Skipping.")
            return {
                "passenger_queue":   [],
                "assessment_status": "skipped",
                "current_step":      "complete",
            }

        # Fetch and score passengers
        passenger_queue = fetch_and_score_passengers()

        print(f"Assessment Agent: Scored {len(passenger_queue)} passengers.")
        print(f"Assessment Agent: Highest priority score: "
              f"{passenger_queue[0]['priority_score'] if passenger_queue else 0}")

    except Exception as e:
        error_msg = f"Assessment Agent error: {str(e)}"
        error_log.append(error_msg)
        print(error_msg)
        passenger_queue = []

    return {
        "passenger_queue":   passenger_queue,
        "assessment_status": "scored" if passenger_queue else "error",
        "current_step":      "rebooking",
        "error_log":         error_log,
    }


# -------------------------------------------------------------
# STANDALONE TEST
# -------------------------------------------------------------

if __name__ == "__main__":
    from src.agents.detection_agent import (
        detection_agent,
        create_initial_state
    )

    print("=" * 50)
    print("Testing Assessment Agent standalone")
    print("=" * 50)

    # Step 1 — Run Detection Agent first
    state  = create_initial_state()
    state  = {**state, **detection_agent(state)}
    print(f"Detection complete: {state['flights_scanned']:,} flights scanned")

    # Step 2 — Run Assessment Agent
    result = assessment_agent(state)

    # Step 3 — Display results
    print(f"\nResults:")
    print(f"  Passengers scored  : {len(result['passenger_queue']):,}")
    print(f"  Assessment status  : {result['assessment_status']}")
    print(f"  Next step          : {result['current_step']}")
    print(f"  Errors             : {len(result['error_log'])}")

    if result["passenger_queue"]:
        print(f"\nTop 5 Priority Passengers:")
        for i, p in enumerate(result["passenger_queue"][:5], 1):
            print(f"  {i}. {p['passenger_id']:12} | "
                  f"score={p['priority_score']:3} | "
                  f"{p['disruption_type']:15} | "
                  f"{p['loyalty_tier']:8} | "
                  f"need={p['special_need']}")

    print("\nAssessment Agent test complete.")
    
