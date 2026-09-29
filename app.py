# ============================================================
# AquaShield
# AI-Powered Water Intelligence & Conservation Platform
# ============================================================

import streamlit as st
import pandas as pd
import altair as alt
import html
from google.cloud import bigquery
from google import genai

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AquaShield",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# CONSTANTS
# ============================================================

PROJECT_ID = "aquashield-bengaluru"
DATASET_ID = "aquashield"
INSIGHTS_TABLE = "aquashield_daily_insights"

FULL_TABLE_ID = f"{PROJECT_ID}.{DATASET_ID}.{INSIGHTS_TABLE}"

GEMINI_LOCATION = "global"
GEMINI_MODEL = "gemini-2.5-flash"


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Soft water-blue app background */
    .stApp {
        background: linear-gradient(
            135deg,
            #f4fbff 0%,
            #eef8ff 45%,
            #f8fcff 100%
        );
    }

    /* Main page */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1450px;
    }

    /* Hide Streamlit header/footer */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

    /* AquaShield title */
    .aquashield-title {
        font-size: 2.7rem;
        font-weight: 750;
        margin-bottom: 0px;
        letter-spacing: -1px;

        background: linear-gradient(
            90deg,
            #0369a1,
            #0891b2
        );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .aquashield-subtitle {
        font-size: 1.05rem;
        opacity: 0.70;
        margin-top: 0px;
        margin-bottom: 25px;
    }

    /* KPI / Risk Cards */
    .risk-card {
        border-radius: 18px;
        padding: 22px 24px;
        border: 1px solid rgba(14, 116, 144, 0.14);

        height: 178px;
        box-sizing: border-box;

        display: flex;
        flex-direction: column;
        justify-content: flex-start;

        background: rgba(255, 255, 255, 0.82);

        box-shadow:
            0 8px 25px rgba(14, 116, 144, 0.07);

        backdrop-filter: blur(8px);
    }

    .card-label {
        font-size: 0.82rem;
        font-weight: 650;
        opacity: 0.65;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        margin-bottom: 12px;
    }

    .card-value {
        font-size: 2rem;
        font-weight: 750;
        margin-bottom: 7px;
    }

    .card-description {
        font-size: 0.88rem;
        opacity: 0.68;
    }

    /* Risk colours */
    .risk-low {
        border-left: 6px solid #22c55e;
    }

    .risk-medium {
        border-left: 6px solid #f59e0b;
    }

    .risk-high {
        border-left: 6px solid #ef4444;
    }

    .risk-critical {
        border-left: 6px solid #b91c1c;
    }

    .metric-blue {
        border-left: 6px solid #3b82f6;
    }

    .metric-cyan {
        border-left: 6px solid #06b6d4;
    }

    /* AI Action */
    .ai-action-card {
        border-radius: 18px;
        padding: 24px 28px;

        border: 1px solid rgba(14, 116, 144, 0.22);

        background: linear-gradient(
            135deg,
            rgba(255,255,255,0.92),
            rgba(224,247,255,0.88)
        );

        box-shadow:
            0 10px 30px rgba(14, 116, 144, 0.08);

        margin-top: 12px;
        margin-bottom: 15px;
    }

    .ai-action-title {
        font-size: 0.83rem;
        font-weight: 700;
        opacity: 0.72;
        letter-spacing: 0.8px;
        margin-bottom: 10px;
    }

    .ai-action-text {
        font-size: 1.07rem;
        line-height: 1.6;
        font-weight: 500;
    }

    /* Section heading */
    .section-heading {
        font-size: 1.35rem;
        font-weight: 700;
        margin-top: 10px;
        margin-bottom: 5px;
    }

    .section-description {
        opacity: 0.65;
        margin-bottom: 20px;
    }

    /* Tab spacing */
    button[data-baseweb="tab"] {
        font-size: 0.95rem;
        padding-left: 18px;
        padding-right: 18px;
    }

    /* Filter row alignment */
    div[data-testid="stHorizontalBlock"] > div {
        align-self: end;
    }

    /* Refresh button sizing/alignment */
    div[data-testid="stButton"] > button {
        min-height: 34px;
        height: 34px;
        padding: 0 14px;
        border-radius: 9px;
        margin-top: 0px;
        white-space: nowrap;

        background: #0f5f8f;
        color: white;
        border: 1px solid #0b4f78;

        font-size: 0.88rem;
        font-weight: 650;
    }

    div[data-testid="stButton"] > button:hover {
        background: #0b4f78;
        color: white;
        border-color: #083f61;
    }

    /* Compact filter controls */
    div[data-baseweb="select"] > div {
        min-height: 38px;
    }

    div[data-testid="stSelectbox"] label {
        margin-bottom: 4px;
    }


    /* AquaShield tab styling */
    div[data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
        padding: 4px 0 8px 0;
    }

    /* All tabs use the same dark AquaShield blue */
    button[data-baseweb="tab"] {
        min-height: 38px;
        padding: 0 16px;
        border-radius: 9px;

        background: #0f5f8f !important;
        border: 1px solid #0b4f78 !important;

        color: white !important;
        font-size: 0.90rem;
        font-weight: 650;

        box-shadow: 0 2px 8px rgba(15, 95, 143, 0.12);

        transition: all 0.18s ease;
    }

    button[data-baseweb="tab"] * {
        color: white !important;
    }

    button[data-baseweb="tab"]:hover {
        background: #0b4f78 !important;
        border-color: #083f61 !important;
        color: white !important;
    }

    /* Selected tab is slightly stronger, not a different color family */
    button[data-baseweb="tab"][aria-selected="true"] {
        background: #083f61 !important;
        border-color: #062f49 !important;
        color: white !important;

        box-shadow:
            0 4px 12px rgba(8, 63, 97, 0.24);
    }

    button[data-baseweb="tab"][aria-selected="true"] * {
        color: white !important;
    }

    button[data-baseweb="tab"][aria-selected="true"]:hover {
        background: #062f49 !important;
        color: white !important;
    }

    /* Remove Streamlit default tab underline/highlight */
    div[data-baseweb="tab-highlight"] {
        display: none !important;
    }

    /* Streamlit metric cards */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.78);
        padding: 15px;
        border-radius: 12px;
        border: 1px solid rgba(14, 116, 144, 0.12);
        box-shadow: 0 5px 18px rgba(14, 116, 144, 0.05);
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CLIENTS
# ============================================================

@st.cache_resource
def get_bigquery_client():
    return bigquery.Client(project=PROJECT_ID)


@st.cache_resource
def get_gemini_client():
    return genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location=GEMINI_LOCATION,
    )


bq_client = get_bigquery_client()


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data(ttl=300)
def load_aquashield_data():

    query = f"""
        SELECT *
        FROM `{FULL_TABLE_ID}`
        ORDER BY date DESC, apartment_name
    """

    df = bq_client.query(query).to_dataframe()

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"]).dt.date

    return df


try:
    df = load_aquashield_data()

except Exception as e:
    st.error("Unable to load AquaShield data from BigQuery.")
    st.exception(e)
    st.stop()


if df.empty:
    st.warning("No AquaShield intelligence data is currently available.")
    st.stop()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_value(row, column, default=None):
    if column not in row.index:
        return default

    value = row[column]

    if pd.isna(value):
        return default

    return value


def format_number(value, decimals=0):
    if value is None:
        return "—"

    try:
        return f"{float(value):,.{decimals}f}"
    except Exception:
        return str(value)


def normalize_risk(value):
    if value is None:
        return "UNKNOWN"

    return str(value).strip().upper()


RISK_ORDER = {
    "UNKNOWN": 0,
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}


def max_risk(*risks):
    normalized = [normalize_risk(r) for r in risks]
    return max(normalized, key=lambda r: RISK_ORDER.get(r, 0))


def derive_shortage_risk(row):
    """
    Use the authoritative shortage risk calculated in BigQuery.
    The rebuilt aquashield_daily_insights table already combines
    tank fill percentage and estimated days remaining coherently.
    """
    return normalize_risk(
        safe_value(
            row,
            "shortage_risk",
            "UNKNOWN",
        )
    )



def risk_css_class(risk):
    risk = normalize_risk(risk)

    if risk == "LOW":
        return "risk-low"

    if risk == "MEDIUM":
        return "risk-medium"

    if risk == "HIGH":
        return "risk-high"

    if risk == "CRITICAL":
        return "risk-critical"

    return "metric-blue"


def risk_icon(risk):
    risk = normalize_risk(risk)

    if risk == "LOW":
        return "✅"

    if risk == "MEDIUM":
        return "⚠️"

    if risk == "HIGH":
        return "🔴"

    if risk == "CRITICAL":
        return "🚨"

    return "ℹ️"


def risk_description(risk, risk_type):
    risk = normalize_risk(risk)

    if risk_type == "leak":
        descriptions = {
            "LOW": "Consumption is currently within the expected range.",
            "MEDIUM": "Some abnormal consumption behaviour has been detected.",
            "HIGH": "Consumption is significantly above the expected pattern.",
            "CRITICAL": "Strong evidence of abnormal water consumption requires attention.",
        }

    else:
        descriptions = {
            "LOW": "Current water availability appears sufficient.",
            "MEDIUM": "Available water should be monitored closely.",
            "HIGH": "Water availability is approaching a potentially unsafe level.",
            "CRITICAL": "Immediate action may be required to prevent water shortage.",
        }

    return descriptions.get(
        risk,
        "Risk information is currently unavailable."
    )


def render_card(label, value, description, css_class="metric-blue"):
    st.markdown(
        f"""
        <div class="risk-card {css_class}">
            <div class="card-label">{label}</div>
            <div class="card-value">{value}</div>
            <div class="card-description">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# GEMINI RECOMMENDATION
# ============================================================

def generate_gemini_recommendation(row):

    apartment_name = safe_value(
        row,
        "apartment_name",
        "Selected apartment"
    )

    date = safe_value(
        row,
        "date",
        ""
    )

    actual = safe_value(
        row,
        "actual_consumption_litres",
        0
    )

    predicted = safe_value(
        row,
        "predicted_consumption_litres",
        0
    )

    variance = safe_value(
        row,
        "consumption_variance_pct",
        0
    )

    water_available = safe_value(
        row,
        "water_available_litres",
        0
    )

    tank_fill = safe_value(
        row,
        "tank_fill_percentage",
        None
    )

    days_remaining = safe_value(
        row,
        "estimated_days_remaining",
        None
    )

    leak_risk = normalize_risk(
        safe_value(
            row,
            "leak_risk",
            safe_value(row, "leak_risk_score", "UNKNOWN")
        )
    )

    shortage_risk = derive_shortage_risk(row)

    conservation = safe_value(
        row,
        "conservation_opportunity_litres",
        0
    )

    prompt = f"""
You are AquaShield, an AI water-management assistant for apartment
facility managers.

Analyze the following water intelligence signals.

Apartment:
{apartment_name}

Date:
{date}

Actual consumption:
{actual} litres

Predicted normal consumption:
{predicted} litres

Consumption variance:
{variance} percent

Current water available:
{water_available} litres

Tank fill:
{f"{tank_fill} percent" if tank_fill is not None else "Not available"}

Estimated water remaining:
{f"{days_remaining} days" if days_remaining is not None else "Not available"}

Leak risk:
{leak_risk}

Shortage risk:
{shortage_risk}

Potential conservation opportunity:
{conservation} litres

Provide ONE concise operational recommendation for the apartment manager.

Rules:

1. Prioritize the most urgent risk.
2. Clearly distinguish leak risk from shortage risk.
3. Do not claim that a leak definitely exists.
4. If leak risk is elevated, recommend investigation of abnormal
   consumption or plumbing/common-area usage.
5. If shortage risk is elevated, focus on water availability,
   replenishment and conservation.
6. If both are elevated, explain that both abnormal consumption and
   supply/storage conditions require attention.
7. If both risks are low, say conditions are currently stable.
8. Use plain English.
9. Maximum 80 words.
10. Do not mention that you are an AI model.
"""

    try:
        client = get_gemini_client()

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )

        if response.text:
            return response.text.strip()

    except Exception:
        pass

    if leak_risk in ["HIGH", "CRITICAL"] and shortage_risk in [
        "HIGH",
        "CRITICAL",
    ]:
        return (
            "Both abnormal consumption and water availability require "
            "attention. Investigate possible leakage or unusual usage "
            "while also reviewing supply, tank storage and immediate "
            "conservation measures."
        )

    if leak_risk in ["HIGH", "CRITICAL"]:
        return (
            "Abnormal consumption is significantly above the expected "
            "pattern. Inspect plumbing, common-area usage and other "
            "possible sources of unexplained water consumption."
        )

    if shortage_risk in ["HIGH", "CRITICAL"]:
        return (
            "Water availability is approaching a critical level. "
            "Review incoming supply, tank storage and expected demand, "
            "and consider immediate conservation measures."
        )

    if leak_risk == "MEDIUM":
        return (
            "Some abnormal consumption has been detected. Continue "
            "monitoring and inspect unusual usage if the pattern persists."
        )

    if shortage_risk == "MEDIUM":
        return (
            "Water availability should be monitored closely. Review "
            "expected demand and upcoming supply before conditions worsen."
        )

    return (
        "Water conditions are currently within the expected operating "
        "range. Continue monitoring consumption and storage conditions."
    )


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="aquashield-title">
        💧 AquaShield
    </div>

    <div class="aquashield-subtitle">
        AI-Powered Water Intelligence & Conservation Platform
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# APARTMENT + DATE SELECTORS
# ============================================================

apartments = sorted(
    df["apartment_name"]
    .dropna()
    .unique()
    .tolist()
)

filter_col1, filter_col2, filter_col3, filter_spacer = st.columns(
    [1.65, 1.25, 0.95, 4.15],
    vertical_alignment="bottom",
)

with filter_col1:
    selected_apartment = st.selectbox(
        "Apartment",
        apartments,
    )


apartment_df = df[
    df["apartment_name"] == selected_apartment
].copy()


available_dates = sorted(
    apartment_df["date"]
    .dropna()
    .unique()
    .tolist(),
    reverse=True,
)


with filter_col2:
    selected_date = st.selectbox(
        "Date",
        available_dates,
        format_func=lambda x: pd.Timestamp(x).strftime(
            "%d %b %Y"
        ),
    )


with filter_col3:
    if st.button(
        "↻ Refresh Data",
        use_container_width=True,
    ):
        st.cache_data.clear()
        st.rerun()


# ============================================================
# SELECT CURRENT RECORD
# ============================================================

selected_rows = apartment_df[
    apartment_df["date"] == selected_date
]


if selected_rows.empty:
    st.warning(
        "No intelligence record exists for the selected apartment/date."
    )

    st.stop()


current = selected_rows.iloc[0]


# ============================================================
# CURRENT METRICS
# ============================================================

leak_risk = normalize_risk(
    safe_value(
        current,
        "leak_risk",
        safe_value(
            current,
            "leak_risk_score",
            "UNKNOWN",
        ),
    )
)


shortage_risk = derive_shortage_risk(current)


tank_fill = safe_value(
    current,
    "tank_fill_percentage",
    None,
)


days_remaining = safe_value(
    current,
    "estimated_days_remaining",
    None,
)


actual_consumption = safe_value(
    current,
    "actual_consumption_litres",
    None,
)


predicted_consumption = safe_value(
    current,
    "predicted_consumption_litres",
    None,
)


variance_pct = safe_value(
    current,
    "consumption_variance_pct",
    None,
)


water_available = safe_value(
    current,
    "water_available_litres",
    None,
)


conservation_opportunity = safe_value(
    current,
    "conservation_opportunity_litres",
    None,
)


deterministic_action = safe_value(
    current,
    "recommended_action",
    None,
)


rule_explanation = safe_value(
    current,
    "ai_explanation",
    None,
)


# ============================================================
# NAVIGATION TABS
# ============================================================

st.divider()

(
    overview_tab,
    leak_tab,
    shortage_tab,
    forecast_tab,
    insights_tab,
) = st.tabs(
    [
        "🏠 Overview",
        "💧 Leak Analysis",
        "🚰 Shortage Analysis",
        "📈 Consumption Forecast",
        "✨ AI Insights",
    ]
)


# ============================================================
# OVERVIEW TAB
# ============================================================

with overview_tab:

    st.markdown(
        '<div class="section-heading">Water Intelligence Overview</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="section-description">
            Current operational status and priority signals for the
            selected apartment.
        </div>
        """,
        unsafe_allow_html=True,
    )

    card1, card2, card3, card4 = st.columns(4)

    with card1:
        render_card(
            "Leak Risk",
            f"{risk_icon(leak_risk)} {leak_risk}",
            risk_description(
                leak_risk,
                "leak",
            ),
            risk_css_class(leak_risk),
        )

    with card2:
        render_card(
            "Shortage Risk",
            f"{risk_icon(shortage_risk)} {shortage_risk}",
            risk_description(
                shortage_risk,
                "shortage",
            ),
            risk_css_class(shortage_risk),
        )

    with card3:
        tank_display = (
            f"{format_number(tank_fill, 0)}%"
            if tank_fill is not None
            else "—"
        )

        render_card(
            "Tank Level",
            tank_display,
            "Current end-of-day tank fill from AquaShield intelligence.",
            "metric-blue",
        )

    with card4:
        days_display = (
            f"{format_number(days_remaining, 2)} days"
            if days_remaining is not None
            else "—"
        )

        render_card(
            "Water Remaining",
            days_display,
            "Estimated supply duration at current usage.",
            "metric-cyan",
        )

    st.write("")

    st.markdown(
        '<div class="section-heading">✨ Recommended Action</div>',
        unsafe_allow_html=True,
    )

    gemini_recommendation = generate_gemini_recommendation(
        current
    )

    # Escape generated text before inserting it inside HTML.
    # This keeps the recommendation card stable if Gemini returns
    # characters such as <, > or &.
    gemini_recommendation_html = html.escape(gemini_recommendation)

    st.markdown(
        f"""<div class="ai-action-card">
<div class="ai-action-title">GEMINI WATER INTELLIGENCE</div>
<div class="ai-action-text">{gemini_recommendation_html}</div>
</div>""",
        unsafe_allow_html=True,
    )

    st.write("")

    st.markdown(
        '<div class="section-heading">Today at a Glance</div>',
        unsafe_allow_html=True,
    )

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.metric(
            "Actual Consumption",
            (
                f"{format_number(actual_consumption)} L"
                if actual_consumption is not None
                else "—"
            ),
        )

    with m2:
        st.metric(
            "Expected Consumption",
            (
                f"{format_number(predicted_consumption)} L"
                if predicted_consumption is not None
                else "—"
            ),
        )

    with m3:
        variance_display = (
            f"{format_number(variance_pct, 1)}%"
            if variance_pct is not None
            else "—"
        )

        st.metric(
            "Consumption Variance",
            variance_display,
        )

    with m4:
        st.metric(
            "Water Available",
            (
                f"{format_number(water_available)} L"
                if water_available is not None
                else "—"
            ),
        )


# ============================================================
# LEAK ANALYSIS TAB
# ============================================================

with leak_tab:

    st.markdown(
        '<div class="section-heading">💧 Leak Analysis</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="section-description">
            Understand why AquaShield detected abnormal consumption
            and review the supporting evidence.
        </div>
        """,
        unsafe_allow_html=True,
    )

    leak_col1, leak_col2, leak_col3 = st.columns(3)

    with leak_col1:
        st.metric(
            "Current Leak Risk",
            leak_risk,
        )

    with leak_col2:
        st.metric(
            "Actual Consumption",
            (
                f"{format_number(actual_consumption)} L"
                if actual_consumption is not None
                else "—"
            ),
        )

    with leak_col3:
        st.metric(
            "Variance vs Expected",
            (
                f"{format_number(variance_pct, 1)}%"
                if variance_pct is not None
                else "—"
            ),
        )

    st.write("")

    st.subheader("Why was this risk detected?")

    if (
        variance_pct is not None
        and float(variance_pct) > 0
    ):
        st.write(
            f"""
            AquaShield predicted approximately
            **{format_number(predicted_consumption)} litres**
            for this apartment.

            Actual consumption was
            **{format_number(actual_consumption)} litres**,
            which is approximately
            **{format_number(variance_pct, 1)}% above the expected level**.

            AquaShield combines this consumption deviation with recent
            usage patterns before assigning the leak-risk signal.
            """
        )

    else:
        st.write(
            """
            Current consumption does not show a significant positive
            deviation from AquaShield's expected consumption pattern.
            """
        )

    st.info(
        "AquaShield identifies possible abnormal consumption patterns. "
        "A leak-risk signal does not by itself confirm that a physical "
        "leak exists."
    )

    st.subheader("Recent Consumption Pattern")

    history_df = (
        apartment_df[
            apartment_df["date"] <= selected_date
        ]
        .sort_values("date")
        .tail(30)
        .copy()
    )

    chart_columns = [
        col
        for col in [
            "actual_consumption_litres",
            "predicted_consumption_litres",
        ]
        if col in history_df.columns
    ]

    if (
        "actual_consumption_litres" in history_df.columns
        and "predicted_consumption_litres" in history_df.columns
    ):

        history_chart = history_df[
            [
                "date",
                "actual_consumption_litres",
                "predicted_consumption_litres",
            ]
        ].copy()

        history_chart = history_chart.rename(
            columns={
                "actual_consumption_litres": "Actual Consumption",
                "predicted_consumption_litres": "Predicted Consumption",
            }
        )

        history_long = history_chart.melt(
            id_vars=["date"],
            var_name="Series",
            value_name="Litres",
        )

        recent_chart = (
            alt.Chart(history_long)
            .mark_line(point=True)
            .encode(
                x=alt.X(
                    "date:T",
                    title="Date",
                ),
                y=alt.Y(
                    "Litres:Q",
                    title="Consumption (litres)",
                ),
                color=alt.Color(
                    "Series:N",
                    title="",
                ),
                tooltip=[
                    alt.Tooltip(
                        "date:T",
                        title="Date",
                        format="%d %b %Y",
                    ),
                    alt.Tooltip(
                        "Series:N",
                        title="Metric",
                    ),
                    alt.Tooltip(
                        "Litres:Q",
                        title="Litres",
                        format=",.0f",
                    ),
                ],
            )
            .properties(
                height=380,
            )
            .interactive()
        )

        st.altair_chart(
            recent_chart,
            use_container_width=True,
        )

        st.caption(
            "Hover over any point to see the date, metric and litre value. "
            "The legend identifies Actual Consumption and Predicted Consumption."
        )

    else:
        st.info(
            "Actual and predicted consumption history is not available."
        )

    st.subheader("Recommended Investigation")

    if leak_risk in [
        "HIGH",
        "CRITICAL",
    ]:

        st.warning(
            "Inspect plumbing, common-area usage, tank overflow and "
            "other possible sources of abnormal consumption."
        )

    elif leak_risk == "MEDIUM":

        st.info(
            "Continue monitoring. Investigate if elevated consumption "
            "persists across multiple days."
        )

    else:

        st.success(
            "No significant leak-related action is currently required."
        )


# ============================================================
# SHORTAGE ANALYSIS TAB
# ============================================================

with shortage_tab:

    st.markdown(
        '<div class="section-heading">🚰 Shortage Analysis</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="section-description">
            Review current storage, available water and expected
            supply duration.
        </div>
        """,
        unsafe_allow_html=True,
    )

    s1, s2, s3 = st.columns(3)

    with s1:
        st.metric(
            "Shortage Risk",
            shortage_risk,
        )

    with s2:
        st.metric(
            "Tank Fill",
            (
                f"{format_number(tank_fill, 1)}%"
                if tank_fill is not None
                else "—"
            ),
        )

    with s3:
        st.metric(
            "Estimated Water Remaining",
            (
                f"{format_number(days_remaining, 2)} days"
                if days_remaining is not None
                else "—"
            ),
        )

    st.write("")

    st.subheader("Current Water Position")

    p1, p2 = st.columns(2)

    with p1:
        st.metric(
            "Available Water",
            (
                f"{format_number(water_available)} L"
                if water_available is not None
                else "—"
            ),
        )

    with p2:
        st.metric(
            "Current Daily Consumption",
            (
                f"{format_number(actual_consumption)} L"
                if actual_consumption is not None
                else "—"
            ),
        )

    st.write("")

    st.subheader("Why was this risk detected?")

    if shortage_risk in [
        "HIGH",
        "CRITICAL",
    ]:

        st.warning(
            f"""
            Current water availability has fallen to a level where
            AquaShield estimates approximately
            **{format_number(days_remaining, 2)} days of supply**
            remaining at the current usage pattern.

            Tank storage and incoming supply should be reviewed.
            """
        )

    elif shortage_risk == "MEDIUM":

        st.info(
            f"""
            Available water currently represents approximately
            **{format_number(days_remaining, 2)} days of supply**.

            Conditions are not yet critical but should be monitored.
            """
        )

    else:

        st.success(
            "Current tank storage and estimated supply duration are "
            "within the normal operating range."
        )

    if "tank_fill_percentage" in apartment_df.columns:

        st.subheader("Tank Level History")

        tank_history = (
            apartment_df[
                apartment_df["date"] <= selected_date
            ][
                [
                    "date",
                    "tank_fill_percentage",
                ]
            ]
            .sort_values("date")
            .tail(30)
            .set_index("date")
        )

        st.line_chart(
            tank_history,
            use_container_width=True,
        )


# ============================================================
# CONSUMPTION FORECAST TAB
# ============================================================

with forecast_tab:

    st.markdown(
        '<div class="section-heading">📈 Consumption Forecast</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="section-description">
            Compare observed water consumption with AquaShield's
            BigQuery ML expected-consumption baseline.
        </div>
        """,
        unsafe_allow_html=True,
    )

    f1, f2, f3 = st.columns(3)

    with f1:
        st.metric(
            "Actual",
            (
                f"{format_number(actual_consumption)} L"
                if actual_consumption is not None
                else "—"
            ),
        )

    with f2:
        st.metric(
            "Predicted",
            (
                f"{format_number(predicted_consumption)} L"
                if predicted_consumption is not None
                else "—"
            ),
        )

    with f3:
        st.metric(
            "Variance",
            (
                f"{format_number(variance_pct, 1)}%"
                if variance_pct is not None
                else "—"
            ),
        )

    st.write("")

    st.subheader("Actual vs Predicted Consumption")

    forecast_history = (
        apartment_df[
            apartment_df["date"] <= selected_date
        ]
        .sort_values("date")
        .tail(60)
        .copy()
    )

    forecast_columns = [
        col
        for col in [
            "actual_consumption_litres",
            "predicted_consumption_litres",
        ]
        if col in forecast_history.columns
    ]

    if (
        "actual_consumption_litres" in forecast_history.columns
        and "predicted_consumption_litres" in forecast_history.columns
    ):

        forecast_chart = forecast_history[
            [
                "date",
                "actual_consumption_litres",
                "predicted_consumption_litres",
            ]
        ].copy()

        forecast_chart = forecast_chart.rename(
            columns={
                "actual_consumption_litres": "Actual Consumption",
                "predicted_consumption_litres": "Predicted Consumption",
            }
        )

        forecast_long = forecast_chart.melt(
            id_vars=["date"],
            var_name="Series",
            value_name="Litres",
        )

        forecast_altair = (
            alt.Chart(forecast_long)
            .mark_line(point=True)
            .encode(
                x=alt.X(
                    "date:T",
                    title="Date",
                ),
                y=alt.Y(
                    "Litres:Q",
                    title="Consumption (litres)",
                ),
                color=alt.Color(
                    "Series:N",
                    title="",
                ),
                tooltip=[
                    alt.Tooltip(
                        "date:T",
                        title="Date",
                        format="%d %b %Y",
                    ),
                    alt.Tooltip(
                        "Series:N",
                        title="Metric",
                    ),
                    alt.Tooltip(
                        "Litres:Q",
                        title="Litres",
                        format=",.0f",
                    ),
                ],
            )
            .properties(
                height=420,
            )
            .interactive()
        )

        st.altair_chart(
            forecast_altair,
            use_container_width=True,
        )

    with st.expander(
        "How does AquaShield predict expected consumption?"
    ):

        st.write(
            """
            AquaShield uses a BigQuery ML consumption model to estimate
            the expected daily water demand for each apartment.

            The prediction considers factors including apartment
            characteristics, occupancy, historical baseline consumption,
            calendar patterns and weather conditions.

            AquaShield then compares actual consumption against this
            predicted baseline to identify abnormal water-use patterns.
            """
        )


# ============================================================
# AI INSIGHTS TAB
# ============================================================

with insights_tab:

    st.markdown(
        '<div class="section-heading">✨ AI Insights</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="section-description">
            Operational intelligence generated from AquaShield's
            predictive, risk and Gemini layers.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Gemini Recommendation")

    st.markdown(
        f"""<div class="ai-action-card">
<div class="ai-action-title">CONTEXT-AWARE WATER MANAGEMENT RECOMMENDATION</div>
<div class="ai-action-text">{gemini_recommendation_html}</div>
</div>""",
        unsafe_allow_html=True,
    )

    if deterministic_action:

        st.subheader(
            "AquaShield Operational Action"
        )

        st.info(
            deterministic_action
        )

    if rule_explanation:

        st.subheader(
            "Supporting Explanation"
        )

        st.write(
            rule_explanation
        )

    if conservation_opportunity is not None:

        st.subheader(
            "Conservation Opportunity"
        )

        c1, c2 = st.columns(
            [1, 2]
        )

        with c1:

            st.metric(
                "Potential Water Saving",
                (
                    f"{format_number(conservation_opportunity)} L"
                ),
            )

        with c2:

            if float(
                conservation_opportunity
            ) > 0:

                st.success(
                    "AquaShield has identified consumption above the "
                    "expected baseline that may represent an opportunity "
                    "for conservation."
                )

            else:

                st.info(
                    "No significant conservation opportunity has been "
                    "identified for the selected day."
                )

    with st.expander(
        "How AquaShield generates this intelligence"
    ):

        st.write(
            """
            **1. Water telemetry and operational data**

            AquaShield combines consumption, supply, tank, apartment and
            weather information.

            **2. BigQuery analytics**

            The data is transformed into daily operational features.

            **3. BigQuery ML**

            Expected daily consumption is predicted for each apartment.

            **4. Risk intelligence**

            AquaShield evaluates consumption deviation and storage /
            supply conditions separately to identify leak risk and
            shortage risk.

            **5. Gemini**

            Gemini converts these quantitative signals into concise,
            context-aware operational recommendations for apartment
            managers.

            Gemini does not replace AquaShield's deterministic risk
            calculations. It explains and converts those signals into
            actionable guidance.
            """
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AquaShield • AI-powered water intelligence for proactive "
    "conservation and apartment water management"
)
