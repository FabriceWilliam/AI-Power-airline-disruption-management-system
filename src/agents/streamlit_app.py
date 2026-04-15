# =============================================================
# streamlit_app.py
# Delta Airlines — Disruption Management Dashboard
# =============================================================

import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path

# -------------------------------------------------------------
# PAGE CONFIG — must be first Streamlit command
# -------------------------------------------------------------
st.set_page_config(
    page_title = "Delta Airlines — Disruption Dashboard",
    page_icon  = "✈",
    layout     = "wide"
)

# -------------------------------------------------------------
# DATABASE CONNECTION
# -------------------------------------------------------------
def get_conn():
    db_path = Path(__file__).resolve().parent / "database" / "delta_disruption.db"
    return sqlite3.connect(str(db_path).replace("\\", "/"))

# -------------------------------------------------------------
# HEADER
# -------------------------------------------------------------
st.title("✈ Delta Airlines — AI Disruption Management")
st.caption("Multi-Agent System | Real-time Disruption Response")
st.divider()

# -------------------------------------------------------------
# KEY METRICS ROW
# -------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

conn = get_conn()

total_disruptions = pd.read_sql(
    "SELECT COUNT(*) as n FROM disrupted_flights", conn
).iloc[0]["n"]

total_passengers = pd.read_sql(
    "SELECT COUNT(*) as n FROM passengers", conn
).iloc[0]["n"]

cancellations = pd.read_sql(
    "SELECT COUNT(*) as n FROM disrupted_flights WHERE disruption_type='CANCELLATION'", conn
).iloc[0]["n"]

critical = pd.read_sql(
    "SELECT COUNT(*) as n FROM disrupted_flights WHERE severity >= 3", conn
).iloc[0]["n"]

conn.close()

col1.metric("Total Disruptions",  f"{total_disruptions:,}")
col2.metric("Passengers Affected", f"{total_passengers:,}")
col3.metric("Cancellations",       f"{int(cancellations):,}")
col4.metric("Critical Events",     f"{int(critical):,}")

st.divider()

# -------------------------------------------------------------
# DISRUPTION BREAKDOWN
# -------------------------------------------------------------
st.subheader("Disruption Breakdown")

conn = get_conn()
df_breakdown = pd.read_sql("""
    SELECT disruption_type, COUNT(*) as count, AVG(DEPARTURE_DELAY) as avg_delay
    FROM disrupted_flights
    GROUP BY disruption_type
    ORDER BY count DESC
""", conn)
conn.close()

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

conn = get_conn()
df_passengers = pd.read_sql("""
    SELECT
        passenger_id,
        flight_id,
        loyalty_tier,
        special_need,
        disruption_type,
        severity,
        CASE has_connection WHEN 1 THEN 'Yes' ELSE 'No' END as connection,
        (severity * 10)
        + CASE special_need
            WHEN 'MEDICAL'    THEN 30
            WHEN 'WHEELCHAIR' THEN 20
            WHEN 'INFANT'     THEN 15
            ELSE 0 END
        + CASE loyalty_tier
            WHEN 'DIAMOND'  THEN 25
            WHEN 'PLATINUM' THEN 20
            WHEN 'GOLD'     THEN 15
            WHEN 'SILVER'   THEN 10
            ELSE 0 END
        + CASE has_connection WHEN 1 THEN 20 ELSE 0 END
        AS priority_score
    FROM passengers
    WHERE disruption_type IN ('CANCELLATION','DELAY_CRITICAL','DELAY_MAJOR')
    ORDER BY priority_score DESC
    LIMIT 20
""", conn)
conn.close()

st.dataframe(df_passengers, use_container_width=True)