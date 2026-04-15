# =============================================================
# supervisor.py
# Delta Airlines — Intelligent Disruption Management System
# Supervisor: LangGraph orchestrator — connects all four agents
# =============================================================

from langgraph.graph import StateGraph, END

from src.state.agent_state        import AgentState
from src.agents.detection_agent   import detection_agent, create_initial_state
from src.agents.assessment_agent  import assessment_agent
from src.agents.rebooking_agent   import rebooking_agent
from src.agents.notification_agent import notification_agent


# -------------------------------------------------------------
# ROUTING LOGIC
# The Supervisor reads current_step from state and decides
# which agent runs next — or whether to end the pipeline.
# -------------------------------------------------------------

def route_next_step(state: AgentState) -> str:
    """
    Reads current_step from state.
    Returns the name of the next node to execute.
    This is how LangGraph knows where to go after each agent.
    """
    current_step = state.get("current_step", "detection")

    # If any critical error occurred — end immediately
    error_log = state.get("error_log", [])
    if len(error_log) > 5:
        print(f"Supervisor: Too many errors ({len(error_log)}). Ending pipeline.")
        return END

    # Route based on current step
    routing_table = {
        "detection":    "assessment",
        "assessment":   "rebooking",
        "rebooking":    "notification",
        "notification": END,
        "complete":     END,
    }

    next_step = routing_table.get(current_step, END)
    print(f"Supervisor: Routing {current_step} → {next_step}")
    return next_step


# -------------------------------------------------------------
# GRAPH CONSTRUCTION
# Define nodes, edges, and compile the LangGraph workflow
# -------------------------------------------------------------

def build_graph() -> StateGraph:
    """
    Builds and compiles the LangGraph StateGraph.
    Returns a compiled graph ready to invoke.
    """
    # Initialize the graph with our shared state
    graph = StateGraph(AgentState)

    # Add all four agents as nodes
    graph.add_node("detection",    detection_agent)
    graph.add_node("assessment",   assessment_agent)
    graph.add_node("rebooking",    rebooking_agent)
    graph.add_node("notification", notification_agent)

    # Set the entry point — always start with Detection
    graph.set_entry_point("detection")

    # Add conditional edges — Supervisor decides what runs next
    graph.add_conditional_edges(
        "detection",
        route_next_step,
        {
            "assessment": "assessment",
            END:           END,
        }
    )

    graph.add_conditional_edges(
        "assessment",
        route_next_step,
        {
            "rebooking": "rebooking",
            END:          END,
        }
    )

    graph.add_conditional_edges(
        "rebooking",
        route_next_step,
        {
            "notification": "notification",
            END:             END,
        }
    )

    # Notification always ends the pipeline
    graph.add_edge("notification", END)

    # Compile and return
    return graph.compile()

# -------------------------------------------------------------
# IMPROVED ROUTING — implements your architectural fix
# Checks detection_status before routing to assessment
# -------------------------------------------------------------

def route_after_detection(state: AgentState) -> str:
    """
    Smart routing after Detection Agent.
    Only proceeds to Assessment if disruptions were actually found.
    """
    detection_status = state.get("detection_status", "idle")
    error_log        = state.get("error_log", [])

    if len(error_log) > 5:
        print("Supervisor: Too many errors. Ending pipeline.")
        return END

    if detection_status != "disruptions_found":
        print("Supervisor: No disruptions found. Pipeline complete.")
        return END

    print("Supervisor: Disruptions found. Routing to Assessment.")
    return "assessment"


# -------------------------------------------------------------
# IMPROVED GRAPH — uses smart routing after detection
# -------------------------------------------------------------

def build_smart_graph() -> StateGraph:
    """
    Builds the improved graph with smart post-detection routing.
    This is the production-ready version of build_graph().
    """
    graph = StateGraph(AgentState)

    # Register all four agents as nodes
    graph.add_node("detection",    detection_agent)
    graph.add_node("assessment",   assessment_agent)
    graph.add_node("rebooking",    rebooking_agent)
    graph.add_node("notification", notification_agent)

    # Entry point
    graph.set_entry_point("detection")

    # Smart routing after detection
    graph.add_conditional_edges(
        "detection",
        route_after_detection,
        {
            "assessment": "assessment",
            END:           END,
        }
    )

    # Fixed edges for remaining steps
    graph.add_edge("assessment",   "rebooking")
    graph.add_edge("rebooking",    "notification")
    graph.add_edge("notification", END)

    return graph.compile()


# -------------------------------------------------------------
# STANDALONE TEST — runs the full pipeline via LangGraph
# -------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 50)
    print("Delta Airlines — Multi-Agent Disruption System")
    print("=" * 50)

    # Build the compiled graph
    print("\nBuilding LangGraph workflow...")
    app = build_smart_graph()
    print("Graph compiled successfully.")

    # Create fresh initial state
    initial_state = create_initial_state()
    print(f"Initial state created. Entry point: detection\n")

    # Run the full pipeline
    print("Invoking pipeline...\n")
    final_state = app.invoke(initial_state)

    # Display final results
    print("\n" + "=" * 50)
    print("PIPELINE COMPLETE — Final State Summary")
    print("=" * 50)
    print(f"  Flights scanned      : {final_state.get('flights_scanned', 0):,}")
    print(f"  Disruptions found    : {len(final_state.get('disruption_events', [])):,}")
    print(f"  Passengers scored    : {len(final_state.get('passenger_queue', [])):,}")
    print(f"  Proposals generated  : {len(final_state.get('rebooking_proposals', [])):,}")
    print(f"  Notifications sent   : {final_state.get('notifications_sent', 0)}")
    print(f"  Pipeline status      : {final_state.get('notification_status', 'unknown')}")
    print(f"  Total errors         : {len(final_state.get('error_log', []))}")

    if final_state.get("error_log"):
        print(f"\nErrors logged:")
        for err in final_state["error_log"]:
            print(f"  - {err}")

    print("\nSystem shutdown complete.")