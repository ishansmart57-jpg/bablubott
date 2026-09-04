import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="GeoSync AI",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CSS ----------------
st.markdown("""
<style>

.main {
    background-color: #f7f9fc;
}

.block-container {
    padding-top: 1.5rem;
}

.logo {
    font-size: 28px;
    font-weight: 700;
    color: #174ea6;
}

.subtitle {
    color: #64748b;
    font-size: 14px;
}

.card {
    background: white;
    padding: 22px;
    border-radius: 14px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    min-height: 120px;
}

.card-title {
    color: #64748b;
    font-size: 14px;
}

.card-number {
    font-size: 30px;
    font-weight: 700;
    color: #111827;
    margin-top: 8px;
}

.card-info {
    font-size: 13px;
    color: #2563eb;
}

.section {
    font-size: 18px;
    font-weight: 700;
    color: #1e293b;
}

.status-green {
    color: #16a34a;
    background: #dcfce7;
    padding: 5px 10px;
    border-radius: 20px;
}

.status-yellow {
    color: #ca8a04;
    background: #fef9c3;
    padding: 5px 10px;
    border-radius: 20px;
}

.status-blue {
    color: #2563eb;
    background: #dbeafe;
    padding: 5px 10px;
    border-radius: 20px;
}

</style>
""", unsafe_allow_html=True)


# ---------------- SIDEBAR ----------------
with st.sidebar:

    st.markdown("""
    <div style="font-size:28px;font-weight:700;color:#174ea6;">
    ◆ GeoSync AI
    </div>
    <div style="color:#64748b;margin-bottom:25px;">
    Urban Land Record Management
    </div>
    """, unsafe_allow_html=True)

    menu = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "🗄️ Datasets",
            "🧠 AI Feature Extraction",
            "🔗 Integration",
            "🛡️ Validation",
            "🗺️ Map Viewer",
            "🔄 Sync Status",
            "📊 Reports",
            "⚙️ Settings"
        ]
    )

    st.markdown("---")

    st.markdown("### System Status")
    st.success("● All Systems Operational")
    st.caption("Last updated: 2 min ago")


# ---------------- HEADER ----------------
col1, col2 = st.columns([8, 2])

with col1:
    st.markdown(
        '<div class="logo">GeoSync AI</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="subtitle">AI-powered geospatial data integration & synchronization</div>',
        unsafe_allow_html=True
    )

with col2:
    st.markdown("🔔   **MR**  MoRD User")


st.markdown("---")


# ---------------- TITLE ----------------
st.title("Dashboard")
st.caption(
    "Overview of multi-source geospatial data integration, validation and synchronization"
)


# ---------------- KPI CARDS ----------------
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("""
    <div class="card">
        <div class="card-title">Total Datasets</div>
        <div class="card-number">12</div>
        <div class="card-info">+2 new this week</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="card">
        <div class="card-title">Integrated</div>
        <div class="card-number">7</div>
        <div class="card-info">58% of total</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="card">
        <div class="card-title">Processing</div>
        <div class="card-number">3</div>
        <div class="card-info">In progress</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown("""
    <div class="card">
        <div class="card-title">Records Synced</div>
        <div class="card-number">1.24M</div>
        <div class="card-info">+125K this week</div>
    </div>
    """, unsafe_allow_html=True)


st.markdown("<br>", unsafe_allow_html=True)


# ---------------- MAP + ACTIVITY ----------------
map_col, activity_col = st.columns([2.1, 1])


# ---------------- MAP ----------------
with map_col:

    st.markdown(
        '<div class="section">🗺️ Dataset Overview Map</div>',
        unsafe_allow_html=True
    )

    # Fake map background
    fig = go.Figure()

    # Roads
    roads = [
        ([0, 10], [2, 8]),
        ([2, 9], [9, 1]),
        ([0, 10], [5, 5]),
        ([5, 5], [0, 10]),
        ([1, 8], [0, 10])
    ]

    for x, y in roads:
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="lines",
                line=dict(color="#d1d5db", width=2),
                hoverinfo="skip",
                showlegend=False
            )
        )

    # Drone Survey area
    fig.add_trace(go.Scatter(
        x=[1, 4, 5, 3, 1],
        y=[7, 9, 6, 3, 7],
        fill="toself",
        fillcolor="rgba(37,99,235,0.20)",
        line=dict(color="#2563eb", width=2),
        name="Drone Survey"
    ))

    # Ortho imagery
    fig.add_trace(go.Scatter(
        x=[5, 9, 8, 6, 5],
        y=[7, 8, 5, 4, 7],
        fill="toself",
        fillcolor="rgba(34,197,94,0.20)",
        line=dict(color="#22c55e", width=2),
        name="Orthorectified Imagery"
    ))

    # Ground truth
    fig.add_trace(go.Scatter(
        x=[5, 7, 8, 7, 5],
        y=[3, 4, 1, 0, 3],
        fill="toself",
        fillcolor="rgba(239,68,68,0.20)",
        line=dict(color="#ef4444", width=2),
        name="Ground Truth"
    ))

    fig.update_layout(
        height=390,
        margin=dict(l=0, r=0, t=10, b=10),
        paper_bgcolor="white",
        plot_bgcolor="#f8fafc",
        xaxis=dict(
            showgrid=True,
            gridcolor="#e5e7eb",
            showticklabels=False,
            zeroline=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#e5e7eb",
            showticklabels=False,
            zeroline=False
        ),
        legend=dict(
            bgcolor="white",
            bordercolor="#e5e7eb",
            borderwidth=1
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ---------------- RECENT ACTIVITY ----------------
with activity_col:

    st.markdown(
        '<div class="section">Recent Activity</div>',
        unsafe_allow_html=True
    )

    activities = [
        ("✅", "Drone Survey - Sector 15", "Integrated successfully", "10 min ago"),
        ("🟡", "Orthorectified Imagery - Zone A", "Processing...", "25 min ago"),
        ("⬆️", "Ground Truth - Block 7", "Upload completed", "1 hr ago"),
        ("✅", "Feature Extraction - Roads", "Completed", "2 hr ago"),
        ("🔄", "Synchronization", "1.24M records synced", "3 hr ago")
    ]

    for icon, title, desc, time in activities:

        st.markdown(
            f"""
            <div style="
                background:white;
                padding:14px;
                border-bottom:1px solid #e5e7eb;
            ">
                <b>{icon} &nbsp; {title}</b>
                <br>
                <span style="color:#64748b;font-size:13px;">
                {desc}
                </span>
                <span style="
                    float:right;
                    color:#94a3b8;
                    font-size:12px;
                ">
                {time}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )


st.markdown("<br>", unsafe_allow_html=True)


# ---------------- DATASETS ----------------
st.markdown(
    '<div class="section">📁 Datasets</div>',
    unsafe_allow_html=True
)

data = pd.DataFrame({
    "Dataset": [
        "Drone Survey - Sector 15",
        "Orthorectified Imagery - Zone A",
        "Ground Truth - Block 7",
        "Revenue Land Records - District X"
    ],
    "Source": [
        "Drone",
        "Imagery",
        "Field Survey",
        "DoLR"
    ],
    "Type": [
        "Spatial",
        "Raster",
        "Vector",
        "Tabular"
    ],
    "Records": [
        "245,678",
        "120 GB",
        "15,432",
        "856,321"
    ],
    "Status": [
        "Integrated",
        "Processing",
        "Uploaded",
        "Integrated"
    ],
    "Last Updated": [
        "10 min ago",
        "25 min ago",
        "1 hr ago",
        "2 hr ago"
    ]
})

st.dataframe(
    data,
    use_container_width=True,
    hide_index=True
)


# ---------------- AI FEATURE EXTRACTION ----------------
st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    '<div class="section">🧠 AI Feature Extraction</div>',
    unsafe_allow_html=True
)

a, b, c = st.columns(3)

with a:
    st.metric(
        "Buildings Detected",
        "8,421",
        "+8.2%"
    )

with b:
    st.metric(
        "Roads Extracted",
        "1,284 km",
        "+4.5%"
    )

with c:
    st.metric(
        "Parcels Matched",
        "92.7%",
        "+3.1%"
    )


# ---------------- DEMO PROCESS BUTTON ----------------
st.markdown("<br>", unsafe_allow_html=True)

if st.button("🚀 Run AI Integration Demo", use_container_width=True):

    progress = st.progress(0)

    import time

    for i in range(101):
        time.sleep(0.015)
        progress.progress(i)

    st.success(
        "Integration completed successfully! "
        "Datasets validated, harmonized and synchronized."
    )

    st.balloons()