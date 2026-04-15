# =============================================================
# main.py
# Delta Airlines — Intelligent Disruption Management System
# Entry point — run this file to start the full pipeline
# =============================================================

from src.agents.detection_agent import create_initial_state
from src.agents.supervisor      import build_smart_graph


def main():
    print("=" * 55)
    print("  Delta Airlines — AI Disruption Management System")
    print("=" * 55)

    # Build the LangGraph workflow
    app           = build_smart_graph()
    initial_state = create_initial_state()

    # Run the full pipeline
    final_state = app.invoke(initial_state)

    # Summary
    print("\n" + "=" * 55)
    print("  PIPELINE SUMMARY")
    print("=" * 55)
    print(f"  Flights scanned    : {final_state.get('flights_scanned', 0):,}")
    print(f"  Passengers scored  : {len(final_state.get('passenger_queue', [])):,}")
    print(f"  Proposals made     : {len(final_state.get('rebooking_proposals', [])):,}")
    print(f"  Notifications sent : {final_state.get('notifications_sent', 0)}")
    print(f"  Status             : {final_state.get('notification_status', 'unknown')}")
    print(f"  Errors             : {len(final_state.get('error_log', []))}")
    print("=" * 55)


if __name__ == "__main__":
    main()
