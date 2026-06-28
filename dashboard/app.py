"""
Sentinel Ops Dashboard — real-time moderation metrics.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random  # Replace with real DB queries in production

st.set_page_config(page_title="Sentinel Dashboard", page_icon="🛡️", layout="wide")

st.title("🛡️ Sentinel — Content Intelligence Ops")
st.caption(f"Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")

# ── Simulated metrics (replace with real DB queries) ───────────
def get_metrics():
    return {
        "total_today": random.randint(1800, 2200),
        "flagged_rate": round(random.uniform(0.04, 0.08), 3),
        "escalated_rate": round(random.uniform(0.01, 0.03), 3),
        "avg_latency_ms": round(random.uniform(180, 280), 1),
    }

def get_category_breakdown():
    return pd.DataFrame({
        "Category": ["Spam", "Hate speech", "Harassment", "Adult content", "Violence", "Misinformation"],
        "Count": [random.randint(30, 120) for _ in range(6)],
    })

def get_volume_over_time():
    now = datetime.utcnow()
    hours = [now - timedelta(hours=i) for i in range(24, 0, -1)]
    return pd.DataFrame({
        "Hour": hours,
        "Approved": [random.randint(60, 100) for _ in hours],
        "Flagged": [random.randint(3, 10) for _ in hours],
        "Escalated": [random.randint(1, 4) for _ in hours],
    })

m = get_metrics()

# ── KPI row ────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Decisions today", f"{m['total_today']:,}")
col2.metric("Flag rate", f"{m['flagged_rate']:.1%}", delta="-0.2%")
col3.metric("Escalation rate", f"{m['escalated_rate']:.1%}", delta="+0.1%", delta_color="inverse")
col4.metric("Avg latency", f"{m['avg_latency_ms']} ms")

st.divider()

# ── Volume chart ───────────────────────────────────────────────
vol_df = get_volume_over_time()
fig_vol = px.area(
    vol_df.melt(id_vars="Hour", var_name="Verdict", value_name="Count"),
    x="Hour", y="Count", color="Verdict",
    color_discrete_map={"Approved": "#1d9e75", "Flagged": "#d85a30", "Escalated": "#f0992b"},
    title="Decision volume — last 24 hours",
)
fig_vol.update_layout(margin=dict(t=40, b=20), height=300)
st.plotly_chart(fig_vol, use_container_width=True)

# ── Category breakdown ─────────────────────────────────────────
col_a, col_b = st.columns(2)
with col_a:
    cat_df = get_category_breakdown()
    fig_cat = px.bar(
        cat_df.sort_values("Count"),
        x="Count", y="Category",
        orientation="h",
        title="Violation categories flagged today",
        color="Count",
        color_continuous_scale="Oranges",
    )
    fig_cat.update_layout(margin=dict(t=40, b=20), height=300, coloraxis_showscale=False)
    st.plotly_chart(fig_cat, use_container_width=True)

with col_b:
    st.subheader("Eval suite — last run")
    eval_data = {
        "Category": ["Spam", "Hate speech", "Harassment", "Adult content", "Violence", "Misinformation"],
        "Precision": [0.97, 0.93, 0.90, 0.89, 0.88, 0.81],
        "Recall": [0.95, 0.91, 0.88, 0.86, 0.84, 0.79],
        "F1": [0.96, 0.92, 0.89, 0.87, 0.86, 0.80],
    }
    st.dataframe(
        pd.DataFrame(eval_data).set_index("Category").style.format("{:.2f}").background_gradient(cmap="Greens"),
        use_container_width=True,
    )

st.divider()
st.caption("Sentinel v1.0 · Powered by LangGraph + RAG + Llama-3.1")
