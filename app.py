import streamlit as st
import pandas as pd
from google.cloud import bigquery
from google import genai

# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="AQUASHIELD",
    page_icon="💧",
    layout="wide"
)

st.title("💧 AQUASHIELD")
st.subheader("AI-Powered Water Management Dashboard")

# --------------------------------------------------
# BigQuery client
# --------------------------------------------------
bq_client = bigquery.Client()

query = """
SELECT *
FROM `aquashield-bengaluru.aquashield.aquashield_daily_insights`
ORDER BY date
"""

# --------------------------------------------------
# Gemini client
# --------------------------------------------------
gemini_client = genai.Client(
    vertexai=True,
    project="aquashield-bengaluru",
    location="global"
)

# --------------------------------------------------
# Load BigQuery data
# --------------------------------------------------
@st.cache_data(ttl=300)
def load_data():
    return bq_client.query(query).to_dataframe()


# --------------------------------------------------
# Gemini recommendation function
# --------------------------------------------------
def generate_ai_recommendation(record):

    prompt = f"""
You are AQUASHIELD, an AI-powered water management assistant.

Analyze the following apartment water monitoring data.

Apartment: {record['apartment_name']}
Date: {record['date']}
Actual consumption: {record['actual_consumption_litres']:.0f} litres
Predicted consumption: {record['predicted_consumption_litres']:.0f} litres
Consumption variance: {record['consumption_variance_pct']:.1f}%
Water available: {record['water_available_litres']:.0f} litres
Tank fill: {record['tank_fill_percentage']:.1f}%
Estimated days remaining: {record['estimated_days_remaining']:.2f}
Leak risk: {record['leak_risk']}
Shortage risk: {record['shortage_risk']}
Conservation opportunity: {record['conservation_opportunity_litres']:.0f} litres

Provide:

1. A concise explanation of the current water situation.
2. Up to two practical actions for the facility manager.

Important:
- Base the answer only on the supplied values.
- Do not invent sensor readings, causes, or external facts.
- Clearly distinguish leak risk from shortage risk.
- If leak risk is HIGH, mention abnormal or excess consumption.
- If shortage risk is HIGH, mention low water availability.
- If both are HIGH, address both conditions separately.
- Keep the entire response under 80 words.
"""

    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text


# --------------------------------------------------
# Main dashboard
# --------------------------------------------------
try:
    df = load_data()

    st.success("Connected to BigQuery successfully!")

    df["date"] = pd.to_datetime(df["date"])

    # --------------------------------------------------
    # Apartment selector
    # --------------------------------------------------
    apartments = sorted(
        df["apartment_name"].dropna().unique()
    )

    selected_apartment = st.selectbox(
        "Select Apartment",
        apartments
    )

    apartment_df = df[
        df["apartment_name"] == selected_apartment
    ].copy()

    apartment_df = apartment_df.sort_values("date")

    # --------------------------------------------------
    # Date selector
    # --------------------------------------------------
    available_dates = sorted(
        apartment_df["date"].dt.date.unique(),
        reverse=True
    )

    selected_date = st.selectbox(
        "Select Date",
        available_dates
    )

    selected_row_df = apartment_df[
        apartment_df["date"].dt.date == selected_date
    ]

    selected_record = selected_row_df.iloc[-1]

    st.caption(
        f"Showing data for "
        f"{selected_apartment} — "
        f"{selected_record['date'].strftime('%d %b %Y')}"
    )

    # --------------------------------------------------
    # Operational KPIs
    # --------------------------------------------------
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Tank Fill",
            f"{selected_record['tank_fill_percentage']:.1f}%"
        )

    with col2:
        st.metric(
            "Estimated Days Remaining",
            f"{selected_record['estimated_days_remaining']:.2f} days"
        )

    with col3:
        st.metric(
            "Leak Risk",
            str(selected_record["leak_risk"])
        )

    with col4:
        st.metric(
            "Shortage Risk",
            str(selected_record["shortage_risk"])
        )

    st.divider()

    # --------------------------------------------------
    # Actual vs predicted consumption chart
    # --------------------------------------------------
    st.subheader("Actual vs Predicted Water Consumption")

    chart_df = (
        apartment_df[
            [
                "date",
                "actual_consumption_litres",
                "predicted_consumption_litres"
            ]
        ]
        .set_index("date")
    )

    st.line_chart(chart_df)

    # --------------------------------------------------
    # Consumption KPIs
    # --------------------------------------------------
    col5, col6, col7 = st.columns(3)

    with col5:
        st.metric(
            "Actual Consumption",
            f"{selected_record['actual_consumption_litres']:,.0f} L"
        )

    with col6:
        st.metric(
            "Predicted Consumption",
            f"{selected_record['predicted_consumption_litres']:,.0f} L"
        )

    with col7:
        st.metric(
            "Conservation Opportunity",
            f"{selected_record['conservation_opportunity_litres']:,.0f} L"
        )

    st.divider()

    # --------------------------------------------------
    # AQUASHIELD rule-based recommendation
    # --------------------------------------------------
    st.subheader("AQUASHIELD Rule-Based Recommendation")

    st.caption(
        "Generated from AQUASHIELD's deterministic risk logic "
        "and threshold-based analysis."
    )

    st.info(
        str(selected_record["recommended_action"])
    )

    # --------------------------------------------------
    # Rule-based risk explanation
    # --------------------------------------------------
    if "ai_explanation" in apartment_df.columns:
        st.subheader("Rule-Based Risk Explanation")

        st.write(
            str(selected_record["ai_explanation"])
        )

    # --------------------------------------------------
    # Gemini-powered recommendation
    # --------------------------------------------------
    st.subheader("✨ Gemini AI Recommendation")

    st.caption(
        "Generated by Gemini using AQUASHIELD's selected "
        "consumption, tank and risk signals."
    )

    if st.button(
        "Generate AI Recommendation",
        type="primary"
    ):
        try:
            with st.spinner(
                "Gemini is analyzing the water conditions..."
            ):
                ai_response = generate_ai_recommendation(
                    selected_record
                )

            st.success(ai_response)

        except Exception as gemini_error:
            st.error(
                "Unable to generate Gemini recommendation."
            )
            st.exception(gemini_error)

    st.divider()

    # --------------------------------------------------
    # Recent monitoring history
    # --------------------------------------------------
    st.subheader("Recent Monitoring History")

    display_columns = [
        "date",
        "actual_consumption_litres",
        "predicted_consumption_litres",
        "consumption_variance_pct",
        "water_available_litres",
        "tank_fill_percentage",
        "estimated_days_remaining",
        "leak_risk",
        "shortage_risk",
        "conservation_opportunity_litres"
    ]

    st.dataframe(
        apartment_df[display_columns]
        .sort_values(
            "date",
            ascending=False
        )
        .head(10),
        use_container_width=True,
        hide_index=True
    )

except Exception as e:
    st.error("Unable to load AQUASHIELD data")
    st.exception(e)