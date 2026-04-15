# =============================================================
# agent_state.py
# Single source of truth for the shared AgentState contract.
# All agents import AgentState from here — never from each other.
# =============================================================

from typing import TypedDict, List


class AgentState(TypedDict):
    # Detection Agent populates these
    flights_scanned:      int
    disruption_events:    List[dict]
    last_scan_time:       str
    detection_status:     str

    # Assessment Agent populates these
    passenger_queue:      List[dict]
    assessment_status:    str

    # Rebooking Agent populates these
    rebooking_proposals:  List[dict]
    rebooking_status:     str

    # Notification Agent populates these
    notifications_sent:   int
    notification_status:  str

    # Supervisor routing
    current_step:         str
    error_log:            List[str]