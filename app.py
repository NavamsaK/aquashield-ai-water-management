import streamlit as st
import pandas as pd
from google.cloud import bigquery

st.set_page_config(
    page_title="AQUASHIELD",
    page_icon="💧",
    layout="wide"
)

st.title("💧 AQUASHIELD")
st.subheader("AI-Powered Water Management Dashboard")

client = bigquery.Client()

query = """
SELECT *
FROM `aquashield-bengaluru.aquashield.aquashield_daily_insights`
ORDER BY date
"""

@st.cache_data(ttl=300)
def load_data():
    return client.query(query).to_dataframe()

try:
    df = load_data()

    st.success("Connected to BigQuery successfully!")

    # --------------------------------------------------
    # Prepare dates
    # --------------------------------------------------
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
    # Main operational KPIs
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
    # Consumption chart
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
    # Consumption KPIs for selected date
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
    # Recommended action
    # --------------------------------------------------
    st.subheader("Recommended Action")

    st.info(
        str(selected_record["recommended_action"])
    )

    # --------------------------------------------------
    # AI explanation
    # --------------------------------------------------
    if "ai_explanation" in apartment_df.columns:
        st.subheader("AI Explanation")

        st.write(
            str(selected_record["ai_explanation"])
        )

    # --------------------------------------------------
    # Recent history
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