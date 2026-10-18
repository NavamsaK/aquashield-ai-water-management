# ============================================================
# AquaShield
# AI-Powered Water Intelligence & Conservation Platform
# ============================================================

import streamlit as st
import pandas as pd
import altair as alt
import html
import calendar
import inspect
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

TOOLTIPS = {
    "apartment": (
        "Choose the apartment community whose water conditions you want to analyse."
    ),
    "date": (
        "Choose an available historical date for the selected apartment."
    ),
    "refresh": (
        "Reload the latest AquaShield intelligence records from BigQuery."
    ),
    "leak_risk": (
        "AquaShield's assessment of abnormal or persistent water consumption. "
        "An elevated signal suggests investigation; it does not by itself confirm "
        "that a physical leak exists."
    ),
    "shortage_risk": (
        "AquaShield's assessment of whether current storage and expected demand "
        "could lead to a water shortage."
    ),
    "tank_fill": (
        "Current end-of-day tank fill percentage for the selected apartment and date."
    ),
    "days_remaining": (
        "Estimated number of days the currently available water may last at the "
        "current usage pattern."
    ),
    "actual_consumption": (
        "Measured water consumption for the selected apartment and date."
    ),
    "predicted_consumption": (
        "Expected daily water consumption predicted by AquaShield's BigQuery ML model."
    ),
    "variance": (
        "Percentage difference between actual consumption and AquaShield's predicted "
        "consumption baseline."
    ),
    "water_available": (
        "Estimated usable water currently available for the selected apartment."
    ),
    "current_daily_consumption": (
        "Measured daily consumption used when assessing current water availability."
    ),
    "conservation": (
        "Estimated excess consumption that may represent a water-conservation opportunity."
    ),
    "calendar_year": (
        "Choose the year shown in the AquaShield calendar."
    ),
    "calendar_month": (
        "Choose the month shown in the AquaShield calendar."
    ),
    "navigation": {
        "Overview": "View current water status and the most important operational signals.",
        "Leak Analysis": "Review the evidence and trends behind AquaShield's leak-risk signal.",
        "Shortage Analysis": "Review storage, available water and shortage-risk evidence.",
        "Consumption Forecast": "Compare actual consumption with the BigQuery ML prediction.",
        "AI Insights": "Review Gemini recommendations and AquaShield operational guidance.",
    },
}


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

    /* Streamlit metric cards */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.78);
        padding: 15px;
        border-radius: 12px;
        border: 1px solid rgba(14, 116, 144, 0.12);
        box-shadow: 0 5px 18px rgba(14, 116, 144, 0.05);
    }

    
/* ===== AquaShield custom button navigation ===== */
/* IMPORTANT: scoped only to our navigation container so Streamlit's
   date-picker/calendar controls keep their native styling. */

.st-key-aquashield_nav button[kind="secondary"],
.st-key-aquashield_nav button[kind="primary"] {
    border-radius: 9px !important;
    min-height: 40px !important;
    font-weight: 650 !important;
    transition: all 0.15s ease !important;
}

/* Inactive navigation buttons */
.st-key-aquashield_nav button[kind="secondary"] {
    background-color: #0f5f8f !important;
    border: 1px solid #0b4f78 !important;
    color: #ffffff !important;
    box-shadow: 0 2px 8px rgba(15, 95, 143, 0.14) !important;
}

.st-key-aquashield_nav button[kind="secondary"]:hover {
    background-color: #0b4f78 !important;
    border-color: #083f61 !important;
    color: #ffffff !important;
}

/* Active navigation button */
.st-key-aquashield_nav button[kind="primary"] {
    background-color: #083f61 !important;
    border: 1px solid #062f49 !important;
    color: #ffffff !important;
    box-shadow:
        0 4px 12px rgba(8, 63, 97, 0.24),
        inset 0 -3px 0 rgba(255,255,255,0.18) !important;
}

.st-key-aquashield_nav button[kind="primary"]:hover {
    background-color: #062f49 !important;
    border-color: #05263b !important;
    color: #ffffff !important;
}

.st-key-aquashield_nav button[kind="secondary"] p,
.st-key-aquashield_nav button[kind="primary"] p {
    color: #ffffff !important;
    font-weight: inherit !important;
}

/* Date picker: preserve native calendar behavior but make the field
   visually consistent with the AquaShield filters. */
div[data-testid="stDateInput"] input {
    min-height: 38px !important;
}

div[data-testid="stDateInput"] label {
    margin-bottom: 4px;
}

/* Keep calendar icon visible */
div[data-testid="stDateInput"] svg {
    opacity: 1 !important;
}


/* ===== AquaShield precise compact calendar ===== */

.calendar-field-label {
    font-size: 0.84rem;
    font-weight: 500;
    color: #1f2937;
    margin-bottom: 4px;
}

.calendar-month-heading {
    text-align: center;
    font-size: 0.82rem;
    font-weight: 750;
    color: #0f5f8f;
    line-height: 1.25;
    margin: 5px 0 8px 0;
    min-height: 20px;
}

.calendar-weekday {
    text-align: center;
    font-size: 0.57rem;
    line-height: 1;
    font-weight: 700;
    color: #64748b;
    padding: 0;
}

.calendar-empty-day {
    height: 24px;
}

/* -------------------------------------------------
   DATE TRIGGER: narrow field, no unused right space
   ------------------------------------------------- */
div[data-testid="stPopover"] > div > button,
div[data-testid="stPopover"] > button {
    width: 150px !important;
    max-width: 150px !important;
    min-width: 150px !important;
    height: 36px !important;
    min-height: 36px !important;
    padding: 0 8px !important;
    justify-content: flex-start !important;
    border-radius: 8px !important;
    white-space: nowrap !important;
}

/* Remove Streamlit's native popover chevron / down-arrow.
   The calendar emoji in the button label remains visible because it is text. */
div[data-testid="stPopover"] > div > button span[data-testid="stIconMaterial"],
div[data-testid="stPopover"] > button span[data-testid="stIconMaterial"],
div[data-testid="stPopover"] > div > button svg,
div[data-testid="stPopover"] > button svg {
    display: none !important;
}

/* Date label tooltip icon - visually aligned with Streamlit's help icon */
.calendar-field-label-row {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 4px;
}

.calendar-help-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 15px;
    height: 15px;
    border: 1px solid #8b98a5;
    border-radius: 50%;
    color: #6b7280;
    font-size: 10px;
    font-weight: 700;
    line-height: 1;
    cursor: help;
}

/* -------------------------------------------------
   POPOVER BODY
   Cover multiple Streamlit DOM versions.
   ------------------------------------------------- */
.stPopoverBody,
div[data-testid="stPopoverBody"],
div[data-testid="stPopoverContent"] {
    width: 285px !important;
    min-width: 285px !important;
    max-width: 285px !important;
    padding: 8px 10px !important;
}

/* Some Streamlit versions wrap the popover in BaseWeb */
div[data-baseweb="popover"] {
    max-width: 285px !important;
}

div[data-baseweb="popover"] > div {
    max-width: 285px !important;
}

/* Tight vertical layout */
.stPopoverBody [data-testid="stVerticalBlock"],
div[data-testid="stPopoverBody"] [data-testid="stVerticalBlock"],
div[data-testid="stPopoverContent"] [data-testid="stVerticalBlock"] {
    gap: 0.10rem !important;
}

/* Year / Month select controls */
.stPopoverBody div[data-baseweb="select"] > div,
div[data-testid="stPopoverBody"] div[data-baseweb="select"] > div,
div[data-testid="stPopoverContent"] div[data-baseweb="select"] > div {
    min-height: 28px !important;
    height: 28px !important;
    font-size: 0.68rem !important;
}

.stPopoverBody label,
div[data-testid="stPopoverBody"] label,
div[data-testid="stPopoverContent"] label {
    font-size: 0.64rem !important;
    margin-bottom: 0 !important;
}

/* Tight row spacing */
.stPopoverBody div[data-testid="stHorizontalBlock"],
div[data-testid="stPopoverBody"] div[data-testid="stHorizontalBlock"],
div[data-testid="stPopoverContent"] div[data-testid="stHorizontalBlock"] {
    gap: 0.12rem !important;
}

/* Compact day buttons */
.stPopoverBody button[kind="secondary"],
.stPopoverBody button[kind="primary"],
div[data-testid="stPopoverBody"] button[kind="secondary"],
div[data-testid="stPopoverBody"] button[kind="primary"],
div[data-testid="stPopoverContent"] button[kind="secondary"],
div[data-testid="stPopoverContent"] button[kind="primary"] {
    min-width: 30px !important;
    width: 30px !important;
    max-width: 30px !important;
    min-height: 24px !important;
    height: 24px !important;
    padding: 0 !important;
    border-radius: 5px !important;
    font-size: 0.61rem !important;
    line-height: 1 !important;
    box-shadow: none !important;
}

/* Keep overall popup short */
.stPopoverBody,
div[data-testid="stPopoverBody"],
div[data-testid="stPopoverContent"] {
    max-height: 300px !important;
    overflow-y: auto !important;
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
    tooltip_text = html.escape(description, quote=True)

    st.markdown(
        f"""
        <div class="risk-card {css_class}" title="{tooltip_text}">
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
# PERFORMANCE HELPERS
# ============================================================

def gemini_cache_key(row):
    apartment_name = safe_value(
        row,
        "apartment_name",
        "unknown",
    )
    date_value = safe_value(
        row,
        "date",
        "unknown",
    )

    return f"{apartment_name}|{date_value}"


def get_cached_gemini_recommendation(row):
    cache = st.session_state.setdefault(
        "gemini_recommendation_cache",
        {},
    )

    return cache.get(
        gemini_cache_key(row)
    )


def generate_and_cache_gemini_recommendation(row):
    cache = st.session_state.setdefault(
        "gemini_recommendation_cache",
        {},
    )

    key = gemini_cache_key(row)

    recommendation = generate_gemini_recommendation(
        row
    )

    cache[key] = recommendation

    return recommendation


def set_active_section(section_name):
    st.session_state.active_section = section_name


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
    [1.65, 1.25, 0.15, 5.10],
    vertical_alignment="bottom",
)

with filter_col1:
    selected_apartment = st.selectbox(
        "Apartment",
        apartments,
        help=TOOLTIPS["apartment"],
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
    if not available_dates:
        st.error("No dates are available for the selected apartment.")
        st.stop()

    available_dates = sorted(
        {pd.to_datetime(d).date() for d in available_dates}
    )
    available_date_set = set(available_dates)

    # Reset calendar state when apartment changes.
    if (
        "calendar_apartment" not in st.session_state
        or st.session_state.calendar_apartment != selected_apartment
    ):
        latest_date = max(available_dates)
        st.session_state.calendar_apartment = selected_apartment
        st.session_state.calendar_selected_date = latest_date
        st.session_state.calendar_view_year = latest_date.year
        st.session_state.calendar_view_month = latest_date.month
        st.session_state.calendar_nonce = 0

    if (
        "calendar_selected_date" not in st.session_state
        or st.session_state.calendar_selected_date not in available_date_set
    ):
        st.session_state.calendar_selected_date = max(available_dates)

    if "calendar_nonce" not in st.session_state:
        st.session_state.calendar_nonce = 0

    selected_date = st.session_state.calendar_selected_date

    date_help_text = html.escape(
        TOOLTIPS["date"],
        quote=True,
    )

    st.markdown(
        f"""
<div class="calendar-field-label-row">
<span class="calendar-field-label">Date</span>
<span class="calendar-help-icon" title="{date_help_text}">?</span>
</div>
""",
        unsafe_allow_html=True,
    )

    # A changing nonce makes Streamlit create a new popover identity after
    # date selection, which closes the old open popover on rerun.
    nonce = st.session_state.calendar_nonce

    # Zero-width characters change the label identity on older Streamlit
    # versions without changing what the user sees.
    invisible_nonce = "\u200b" * (nonce % 5)

    calendar_trigger = (
        f"📅 {selected_date.strftime('%d %b %Y')}{invisible_nonce}"
    )

    popover_params = inspect.signature(st.popover).parameters
    popover_kwargs = {}

    # Keep the date field compact.
    if "width" in popover_params:
        popover_kwargs["width"] = 150
    else:
        popover_kwargs["use_container_width"] = False

    # Dynamic key guarantees the open popover is discarded after selection.
    if "key" in popover_params:
        popover_kwargs["key"] = f"aquashield_calendar_{nonce}"

    if "wrap" in popover_params:
        popover_kwargs["wrap"] = False

    with st.popover(
        calendar_trigger,
        **popover_kwargs,
    ):
        available_years = sorted({d.year for d in available_dates})

        view_year = st.session_state.get(
            "calendar_view_year",
            selected_date.year,
        )
        view_month = st.session_state.get(
            "calendar_view_month",
            selected_date.month,
        )

        if view_year not in available_years:
            view_year = selected_date.year

        # ---------------------------------------------------------------
        # Compact Month / Year controls.
        # Explicit widget widths prevent them from forcing a huge popup.
        # ---------------------------------------------------------------
        year_col, month_col = st.columns(
            [0.9, 1.15],
            gap="small",
        )

        selectbox_params = inspect.signature(st.selectbox).parameters

        with year_col:
            year_kwargs = {}
            if "width" in selectbox_params:
                year_kwargs["width"] = 92

            chosen_year = st.selectbox(
                "Year",
                available_years,
                index=available_years.index(view_year),
                key=f"aquashield_calendar_year_{nonce}",
                **year_kwargs,
                help=TOOLTIPS["calendar_year"],
            )

        with month_col:
            month_numbers = list(range(1, 13))
            month_kwargs = {}
            if "width" in selectbox_params:
                month_kwargs["width"] = 112

            chosen_month = st.selectbox(
                "Month",
                month_numbers,
                index=view_month - 1,
                format_func=lambda m: calendar.month_name[m],
                key=f"aquashield_calendar_month_{nonce}",
                **month_kwargs,
                help=TOOLTIPS["calendar_month"],
            )

        st.session_state.calendar_view_year = chosen_year
        st.session_state.calendar_view_month = chosen_month

        st.markdown(
            f'<div class="calendar-month-heading">'
            f'{calendar.month_name[chosen_month]} {chosen_year}'
            f'</div>',
            unsafe_allow_html=True,
        )

        weekday_names = ["S", "M", "T", "W", "T", "F", "S"]
        weekday_cols = st.columns(7, gap="small")
        for idx, weekday in enumerate(weekday_names):
            with weekday_cols[idx]:
                st.markdown(
                    f'<div class="calendar-weekday">{weekday}</div>',
                    unsafe_allow_html=True,
                )

        def _select_calendar_date(candidate_date):
            st.session_state.calendar_selected_date = candidate_date
            st.session_state.calendar_view_year = candidate_date.year
            st.session_state.calendar_view_month = candidate_date.month

            # Incrementing nonce changes the popover key/identity.
            # On rerun, the previous open popover disappears.
            st.session_state.calendar_nonce += 1

        month_grid = calendar.Calendar(
            firstweekday=6
        ).monthdayscalendar(
            chosen_year,
            chosen_month,
        )

        button_params = inspect.signature(st.button).parameters

        for week in month_grid:
            day_cols = st.columns(7, gap="small")

            for day_index, day_number in enumerate(week):
                with day_cols[day_index]:
                    if day_number == 0:
                        st.markdown(
                            '<div class="calendar-empty-day">&nbsp;</div>',
                            unsafe_allow_html=True,
                        )
                        continue

                    candidate_date = pd.Timestamp(
                        year=chosen_year,
                        month=chosen_month,
                        day=day_number,
                    ).date()

                    date_available = candidate_date in available_date_set
                    is_selected = candidate_date == selected_date

                    day_kwargs = {}
                    if "width" in button_params:
                        day_kwargs["width"] = 30
                    else:
                        day_kwargs["use_container_width"] = False

                    st.button(
                        str(day_number),
                        key=(
                            f"calendar_day_{selected_apartment}_"
                            f"{chosen_year}_{chosen_month}_{day_number}_{nonce}"
                        ),
                        disabled=not date_available,
                        type="primary" if is_selected else "secondary",
                        on_click=_select_calendar_date,
                        args=(candidate_date,),
                        **day_kwargs,
                    )

    selected_date = st.session_state.calendar_selected_date



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
# SHARED GEMINI RECOMMENDATION
# ============================================================

# Performance optimization:
# Do NOT call Gemini during every Streamlit rerun.
# Navigation, apartment selection and date selection should remain fast.
# Gemini is generated only when explicitly requested and then cached
# for the selected apartment/date.
gemini_recommendation = get_cached_gemini_recommendation(
    current
)

gemini_recommendation_html = (
    html.escape(gemini_recommendation)
    if gemini_recommendation
    else None
)


# ============================================================
# NAVIGATION TABS
# ============================================================

st.divider()

if "active_section" not in st.session_state:
    st.session_state.active_section = "Overview"

with st.container(key="aquashield_nav"):
    nav1, nav2, nav3, nav4, nav5 = st.columns(
        [1.0, 1.2, 1.45, 1.55, 1.0],
        gap="small",
    )

    nav_items = [
        ("Overview", nav1),
        ("Leak Analysis", nav2),
        ("Shortage Analysis", nav3),
        ("Consumption Forecast", nav4),
        ("AI Insights", nav5),
    ]

    for label, column in nav_items:
        with column:
            selected = st.session_state.active_section == label
            st.button(
                label,
                key=f"nav_{label.lower().replace(' ', '_')}",
                use_container_width=True,
                type="primary" if selected else "secondary",
                help=TOOLTIPS["navigation"].get(
                    label,
                    "Open this AquaShield section.",
                ),
                on_click=set_active_section,
                args=(label,),
            )

active_section = st.session_state.active_section


# ============================================================
# OVERVIEW TAB
# ============================================================

if active_section == "Overview":

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

    if gemini_recommendation_html:
        overview_action_title = "GEMINI WATER INTELLIGENCE"
        overview_action_text = gemini_recommendation_html
    else:
        overview_action_title = "AQUASHIELD OPERATIONAL INTELLIGENCE"

        fallback_action = (
            deterministic_action
            or rule_explanation
            or (
                "Water conditions are currently within the expected "
                "operating range. Continue monitoring consumption "
                "and storage conditions."
            )
        )

        overview_action_text = html.escape(
            str(fallback_action)
        )

    st.markdown(
        f"""<div class="ai-action-card">
<div class="ai-action-title">{overview_action_title}</div>
<div class="ai-action-text">{overview_action_text}</div>
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
            help=TOOLTIPS["actual_consumption"],
        )

    with m2:
        st.metric(
            "Expected Consumption",
            (
                f"{format_number(predicted_consumption)} L"
                if predicted_consumption is not None
                else "—"
            ),
            help=TOOLTIPS["predicted_consumption"],
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
            help=TOOLTIPS["variance"],
        )

    with m4:
        st.metric(
            "Water Available",
            (
                f"{format_number(water_available)} L"
                if water_available is not None
                else "—"
            ),
            help=TOOLTIPS["water_available"],
        )


# ============================================================
# LEAK ANALYSIS TAB
# ============================================================

elif active_section == "Leak Analysis":

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
            help=TOOLTIPS["leak_risk"],
        )

    with leak_col2:
        st.metric(
            "Actual Consumption",
            (
                f"{format_number(actual_consumption)} L"
                if actual_consumption is not None
                else "—"
            ),
            help=TOOLTIPS["actual_consumption"],
        )

    with leak_col3:
        st.metric(
            "Variance vs Expected",
            (
                f"{format_number(variance_pct, 1)}%"
                if variance_pct is not None
                else "—"
            ),
            help=TOOLTIPS["variance"],
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

elif active_section == "Shortage Analysis":

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
            help=TOOLTIPS["shortage_risk"],
        )

    with s2:
        st.metric(
            "Tank Fill",
            (
                f"{format_number(tank_fill, 1)}%"
                if tank_fill is not None
                else "—"
            ),
            help=TOOLTIPS["tank_fill"],
        )

    with s3:
        st.metric(
            "Estimated Water Remaining",
            (
                f"{format_number(days_remaining, 2)} days"
                if days_remaining is not None
                else "—"
            ),
            help=TOOLTIPS["days_remaining"],
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
            help=TOOLTIPS["water_available"],
        )

    with p2:
        st.metric(
            "Current Daily Consumption",
            (
                f"{format_number(actual_consumption)} L"
                if actual_consumption is not None
                else "—"
            ),
            help=TOOLTIPS["current_daily_consumption"],
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

elif active_section == "Consumption Forecast":

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
            help=TOOLTIPS["actual_consumption"],
        )

    with f2:
        st.metric(
            "Predicted",
            (
                f"{format_number(predicted_consumption)} L"
                if predicted_consumption is not None
                else "—"
            ),
            help=TOOLTIPS["predicted_consumption"],
        )

    with f3:
        st.metric(
            "Variance",
            (
                f"{format_number(variance_pct, 1)}%"
                if variance_pct is not None
                else "—"
            ),
            help=TOOLTIPS["variance"],
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

elif active_section == "AI Insights":

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

    if gemini_recommendation_html:
        st.markdown(
            f"""<div class="ai-action-card">
<div class="ai-action-title">CONTEXT-AWARE WATER MANAGEMENT RECOMMENDATION</div>
<div class="ai-action-text">{gemini_recommendation_html}</div>
</div>""",
            unsafe_allow_html=True,
        )

        if st.button(
            "↻ Regenerate Gemini Recommendation",
            key="regenerate_gemini_recommendation",
            help=(
                "Generate a fresh Gemini recommendation for the "
                "selected apartment and date."
            ),
        ):
            with st.spinner(
                "Gemini is analysing the selected water signals..."
            ):
                fresh_recommendation = (
                    generate_and_cache_gemini_recommendation(
                        current
                    )
                )

            st.session_state[
                "last_gemini_refresh"
            ] = gemini_cache_key(current)

            st.rerun()

    else:
        st.info(
            "Gemini is loaded on demand so AquaShield remains fast "
            "while you navigate between apartments, dates and sections."
        )

        if st.button(
            "✨ Generate Gemini Recommendation",
            key="generate_gemini_recommendation",
            type="primary",
            help=(
                "Ask Gemini to analyse the selected AquaShield signals "
                "and generate an operational recommendation."
            ),
        ):
            with st.spinner(
                "Gemini is analysing the selected water signals..."
            ):
                generate_and_cache_gemini_recommendation(
                    current
                )

            st.rerun()

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
                help=TOOLTIPS["conservation"],
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
