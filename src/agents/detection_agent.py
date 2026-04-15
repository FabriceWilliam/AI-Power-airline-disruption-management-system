# =============================================================
# detection_agent.py
# Delta Airlines — Intelligent Disruption Management System
# Agent 1: Detection Agent
# =============================================================

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List

# Import shared state from single source of truth
from src.state.agent_state import AgentState

# -------------------------------------------------------------
# DATABASE CONNECTION
# Reusable helper — every agent uses this same pattern
# -------------------------------------------------------------

def get_db_connection() -> sqlite3.Connection:
    """
    Returns a connection to the Delta disruption database.
    Always call conn.close() after use to free resources.
    """
    base_dir = Path(__file__).resolve().parent.parent.parent
    db_path  = str(base_dir / "database" / "delta_disruption.db")
    db_path  = db_path.replace("\\", "/")
    return sqlite3.connect(db_path)


def fetch_active_flights() -> List[dict]:
    """
    Fetches all disrupted flights from the database.
    Returns a list of dictionaries — one per flight.
    """
    conn = get_db_connection()
    try:
        cursor = conn.execute("""
            SELECT
                FLIGHT_NUMBER,
                ORIGIN_AIRPORT,
                DESTINATION_AIRPORT,
                DEPARTURE_DELAY,
                CANCELLED,
                disruption_type,
                severity
            FROM disrupted_flights
            ORDER BY severity DESC, DEPARTURE_DELAY DESC
        """)
        columns = [desc[0] for desc in cursor.description]
        flights  = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return flights
    except Exception as e:
        print(f"Database error: {e}")
        return []
    finally:
        conn.close()

# -------------------------------------------------------------
# DISRUPTION CLASSIFICATION
# Core business logic — maps raw delay data to disruption types
# -------------------------------------------------------------

def classify_disruption(flight: dict) -> tuple:
    """
    Classifies a flight into a disruption type and severity.
    Returns: (disruption_type: str, severity: int)
    """
    if flight.get("CANCELLED") == 1:
        return "CANCELLATION", 5
    delay = flight.get("DEPARTURE_DELAY", 0) or 0
    if delay >= 120:
        return "DELAY_CRITICAL", 3
    elif delay >= 60:
        return "DELAY_MAJOR", 2
    elif delay >= 15:
        return "DELAY_MINOR", 1
    return "ON_TIME", 0


# -------------------------------------------------------------
# LANGGRAPH NODE — THE DETECTION AGENT
# This function IS the agent. LangGraph calls it automatically.
# Input:  current AgentState
# Output: dict of updated state keys
# -------------------------------------------------------------

def detection_agent(state: AgentState) -> dict:
    """
    LangGraph node: Detection Agent.
    Scans the flight database for disruptions.
    Updates shared state with findings.
    """
    print("Detection Agent: Starting flight scan...")

    disruption_events = []
    error_log         = list(state.get("error_log", []))

    try:
        flights = fetch_active_flights()

        for flight in flights:
            disruption_type, severity = classify_disruption(flight)

            if severity > 0:
                event = {
                    "flight_id":        str(flight.get("FLIGHT_NUMBER", "UNKNOWN")),
                    "origin":           flight.get("ORIGIN_AIRPORT", ""),
                    "destination":      flight.get("DESTINATION_AIRPORT", ""),
                    "disruption_type":  disruption_type,
                    "severity":         severity,
                    "delay_minutes":    flight.get("DEPARTURE_DELAY", 0) or 0,
                    "detected_at":      datetime.now().isoformat(),
                }
                disruption_events.append(event)

        print(f"Detection Agent: Found {len(disruption_events)} disruptions.")

    except Exception as e:
        error_msg = f"Detection Agent error: {str(e)}"
        error_log.append(error_msg)
        print(error_msg)

    # Return ONLY the keys this agent updates
    return {
        "flights_scanned":    len(disruption_events),
        "disruption_events":  disruption_events,
        "last_scan_time":     datetime.now().isoformat(),
        "detection_status":   "disruptions_found" if disruption_events else "idle",
        "current_step":       "assessment",
        "error_log":          error_log,
    }

    # -------------------------------------------------------------
# INITIAL STATE FACTORY
# Creates a clean starting state for every new workflow run.
# Called by main.py before invoking the LangGraph graph.
# -------------------------------------------------------------

def create_initial_state() -> AgentState:
    """
    Returns a fresh AgentState with all fields initialized.
    Always start from a clean state — never reuse old state.
    """
    return {
        "flights_scanned":     0,
        "disruption_events":   [],
        "last_scan_time":      "",
        "detection_status":    "idle",
        "passenger_queue":     [],
        "assessment_status":   "pending",
        "rebooking_proposals": [],
        "rebooking_status":    "pending",
        "notifications_sent":  0,
        "notification_status": "pending",
        "current_step":        "detection",
        "error_log":           [],
    }


# -------------------------------------------------------------
# STANDALONE TEST — runs when you execute this file directly
# python src/agents/detection_agent.py
# -------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 50)
    print("Testing Detection Agent standalone")
    print("=" * 50)

    # Create fresh state
    state = create_initial_state()
    print(f"Initial state created. Current step: {state['current_step']}")

    # Run the agent
    result = detection_agent(state)

    # Display results
    print(f"\nResults:")
    print(f"  Flights scanned    : {result['flights_scanned']:,}")
    print(f"  Detection status   : {result['detection_status']}")
    print(f"  Current step       : {result['current_step']}")
    print(f"  Errors             : {len(result['error_log'])}")

    if result["disruption_events"]:
        print(f"\nSample disruption (first event):")
        first = result["disruption_events"][0]
        for key, value in first.items():
            print(f"  {key:20} : {value}")

    print("\nDetection Agent test complete.")
    
