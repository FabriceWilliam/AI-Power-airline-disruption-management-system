# =============================================================
# streamlit_app.py — Cloud-ready version
# Delta Airlines — AI Disruption Management Dashboard
# Uses embedded sample data — no database required
# =============================================================

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Delta Airlines — Disruption Dashboard",
    page_icon="✈",
    layout="wide"
)

# -------------------------------------------------------------
# HEADER
# -------------------------------------------------------------
st.title("✈ Delta Airlines — AI Disruption Management")
st.caption("Multi-Agent System | Real-time Disruption Response")
st.divider()

# -------------------------------------------------------------
# KEY METRICS
# -------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Disruptions",   "75,287", "+8.6% of flights")
col2.metric("Passengers Affected", "1,974",  "Simulated dataset")
col3.metric("Cancellations",       "3,824",  "Severity 5")
col4.metric("Critical Events",     "17,981", "Severity ≥ 3")

st.divider()

# -------------------------------------------------------------
# DISRUPTION BREAKDOWN
# -------------------------------------------------------------
st.subheader("Disruption Breakdown")

df_breakdown = pd.DataFrame({
    "disruption_type": ["DELAY_MINOR", "DELAY_MAJOR", "DELAY_CRITICAL", "CANCELLATION"],
    "count":           [35651, 21655, 14157, 3824],
    "avg_delay":       [41.6, 83.3, 218.5, 112.3]
})

col_left, col_right = st.columns(2)
with col_left:
    st.bar_chart(df_breakdown.set_index("disruption_type")["count"])
with col_right:
    st.dataframe(df_breakdown, use_container_width=True)

st.divider()

# -------------------------------------------------------------
# PRIORITY PASSENGER QUEUE
# -------------------------------------------------------------
st.subheader("Top Priority Passengers")

df_passengers = pd.DataFrame([
    {"passenger_id": "PAX-0263-0", "flight_id": "DL435",  "loyalty_tier": "GOLD",     "special_need": "MEDICAL",     "disruption_type": "CANCELLATION",   "severity": 5, "connection": "Yes", "priority_score": 115},
    {"passenger_id": "PAX-0420-0", "flight_id": "DL1779", "loyalty_tier": "GOLD",     "special_need": "MEDICAL",     "disruption_type": "CANCELLATION",   "severity": 5, "connection": "Yes", "priority_score": 115},
    {"passenger_id": "PAX-0026-0", "flight_id": "DL2599", "loyalty_tier": "SILVER",   "special_need": "MEDICAL",     "disruption_type": "CANCELLATION",   "severity": 5, "connection": "Yes", "priority_score": 110},
    {"passenger_id": "PAX-0084-2", "flight_id": "DL2678", "loyalty_tier": "PLATINUM", "special_need": "WHEELCHAIR",  "disruption_type": "CANCELLATION",   "severity": 5, "connection": "Yes", "priority_score": 110},
    {"passenger_id": "PAX-0261-0", "flight_id": "DL1131", "loyalty_tier": "PLATINUM", "special_need": "WHEELCHAIR",  "disruption_type": "CANCELLATION",   "severity": 5, "connection": "Yes", "priority_score": 110},
    {"passenger_id": "PAX-0335-1", "flight_id": "DL1780", "loyalty_tier": "GOLD",     "special_need": "WHEELCHAIR",  "disruption_type": "CANCELLATION",   "severity": 5, "connection": "Yes", "priority_score": 105},
    {"passenger_id": "PAX-0034-1", "flight_id": "DL2489", "loyalty_tier": "SILVER",   "special_need": "WHEELCHAIR",  "disruption_type": "CANCELLATION",   "severity": 5, "connection": "Yes", "priority_score": 100},
    {"passenger_id": "PAX-0701-0", "flight_id": "DL2042", "loyalty_tier": "PLATINUM", "special_need": "MEDICAL",     "disruption_type": "DELAY_CRITICAL", "severity": 3, "connection": "Yes", "priority_score": 100},
    {"passenger_id": "PAX-0791-1", "flight_id": "DL2075", "loyalty_tier": "PLATINUM", "special_need": "MEDICAL",     "disruption_type": "CANCELLATION",   "severity": 5, "connection": "No",  "priority_score": 100},
    {"passenger_id": "PAX-0792-0", "flight_id": "DL835",  "loyalty_tier": "GOLD",     "special_need": "INFANT",      "disruption_type": "CANCELLATION",   "severity": 5, "connection": "Yes", "priority_score": 100},
])

st.dataframe(df_passengers, use_container_width=True)

st.divider()

# -------------------------------------------------------------
# KPI SUMMARY
# -------------------------------------------------------------
st.subheader("KPI Achievement")

kpi_data = pd.DataFrame([
    {"KPI": "Rebooking Time",        "Baseline": "20–40 min", "Target": "< 5 min",  "Result": "✅ Near-instant"},
    {"KPI": "Resolution Rate",       "Baseline": "30–50%",    "Target": "70–85%",   "Result": "✅ 100%"},
    {"KPI": "Missed Connections",    "Baseline": "15–25%",    "Target": "5–10%",    "Result": "✅ Priority routing"},
    {"KPI": "Notification Time",     "Baseline": "15–30 min", "Target": "< 1 min",  "Result": "✅ Real-time AI"},
    {"KPI": "Call Center Load",      "Baseline": "200–400%",  "Target": "–30–50%",  "Result": "✅ Fully automated"},
])

st.dataframe(kpi_data, use_container_width=True, hide_index=True)

st.divider()

# -------------------------------------------------------------
# PIPELINE RESULTS
# -------------------------------------------------------------
st.subheader("Pipeline Execution Results")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Flights Scanned",    "75,287")
col2.metric("Passengers Scored",  "1,008")
col3.metric("Proposals Made",     "1,008")
col4.metric("Notifications Sent", "5")
col5.metric("Pipeline Errors",    "0")

st.divider()

# -------------------------------------------------------------
# FOOTER
# -------------------------------------------------------------
st.caption("Built by Fabrice William Fomhom · Python · LangGraph · Claude API · Streamlit · SQLite")
st.caption("GitHub: https://github.com/FabriceWilliam/AI-Power-airline-disruption-management-system")