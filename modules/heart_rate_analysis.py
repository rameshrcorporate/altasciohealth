import streamlit as st
import pandas as pd
import plotly.express as px
import ast  # To safely parse HeartRateSamples & HRVValues from string format

@st.cache_data
def aggregate_heart_rate(filtered_df, time_interval):
    """ Aggregates heart rate (avg) based on selected time interval. """
    if time_interval == "Weekly" and "Week" in filtered_df.columns:
        return filtered_df.groupby("Week")["HeartRateAvg"].mean().reset_index(), "Week"
    elif time_interval == "Monthly" and "Month" in filtered_df.columns:
        return filtered_df.groupby("Month")["HeartRateAvg"].mean().reset_index(), "Month"
    return filtered_df.groupby("RecordDate")["HeartRateAvg"].mean().reset_index(), "RecordDate"

def parse_heart_rate_samples(sample_str):
    """ Parses heart rate samples from stored string format to a DataFrame. """
    try:
        heart_rate_list = ast.literal_eval(sample_str)
        df = pd.DataFrame(heart_rate_list, columns=["Timestamp", "HeartRate"])
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit='s')
        return df
    except:
        return pd.DataFrame(columns=["Timestamp", "HeartRate"])

def parse_hrv_values(hrv_dict_str, record_date):
    """ Parses HRV values stored as {seconds_since_midnight: HRV_value} into a DataFrame. """
    try:
        hrv_dict = ast.literal_eval(hrv_dict_str)
        hrv_df = pd.DataFrame(list(hrv_dict.items()), columns=["SecondsSinceMidnight", "HRV"])
        hrv_df["Timestamp"] = pd.to_datetime(record_date) + pd.to_timedelta(hrv_df["SecondsSinceMidnight"], unit="s")
        return hrv_df
    except:
        return pd.DataFrame(columns=["Timestamp", "HRV"])

def show_page(filtered_df):
    """ Displays the Heart Rate Analysis Page with hierarchical filtering and meaningful visualizations. """
    if filtered_df.empty:
        st.warning("⚠️ No data available for the selected filters.")
        return

    # ---- Hierarchical Filters ----
    st.sidebar.header("🔍 Filter Selection")

    org_filter = st.sidebar.selectbox("Select Organization", ["All"] + list(filtered_df["OrganizationName"].dropna().unique()), key="org_filter_hr")
    if org_filter != "All":
        filtered_df = filtered_df[filtered_df["OrganizationName"] == org_filter]

    physician_list = filtered_df["PhysicianName"].dropna().unique()
    physician_filter = st.sidebar.selectbox("Select Physician", ["All"] + list(physician_list), key="physician_filter_hr")
    if physician_filter != "All":
        filtered_df = filtered_df[filtered_df["PhysicianName"] == physician_filter]

    participant_list = filtered_df["Participant Name"].dropna().unique()
    participant_filter = st.sidebar.selectbox("Select Participant", ["All"] + list(participant_list), key="participant_filter_hr")
    if participant_filter != "All":
        filtered_df = filtered_df[filtered_df["Participant Name"] == participant_filter]

    # ---- Display Selected Profiles ----
    st.subheader("👤 Selected Profiles")
    col1, col2 = st.columns(2)

    if physician_filter != "All":
        physician_photo_url = filtered_df["PhysicianPhoto"].dropna().iloc[0].strip("'")
        with col1:
            st.image(physician_photo_url, width=150, caption=f"Physician: {physician_filter}")

    if participant_filter != "All":
        participant_photo_url = filtered_df["ParticipantPhotoURL"].dropna().iloc[0].strip("'")
        with col2:
            st.image(participant_photo_url, width=150, caption=f"Participant: {participant_filter}")

    # ---- User selection for aggregation level ----
    time_interval = st.radio("Select Time Interval", ["Daily", "Weekly", "Monthly"], horizontal=True)

    # Ensure the filtered dataset is used for calculations
    grouped_df, x_col = aggregate_heart_rate(filtered_df, time_interval)

    # ---- Key Metrics ----
    st.subheader("📊 Key Heart Rate Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Average HR", round(filtered_df["HeartRateAvg"].mean(), 2))
        st.metric("Max HR", round(filtered_df["maxHR"].mean(), 2))
    with col2:
        st.metric("Resting HR", round(filtered_df["RestingHeartRate"].mean(), 2))
        st.metric("Min HR", round(filtered_df["minHR"].mean(), 2))
    with col3:
        st.metric("Fat Burn Zone %", round(filtered_df["HRZones_Fatburn"].mean(), 2))
        st.metric("Cardio Zone %", round(filtered_df["HRZones_Cardio"].mean(), 2))

    # ---- Heart Rate Trends ----
    st.subheader("💓 Heart Rate Trends")
    fig_hr = px.line(grouped_df, x=x_col, y="HeartRateAvg", title=f"Average Heart Rate ({time_interval})")
    st.plotly_chart(fig_hr)

    # ---- HRV Time-Series Visualization ----
    if participant_filter != "All":
        st.subheader("📈 HRV Sample Trends")
        hrv_values_str = filtered_df["HRVValues"].dropna().iloc[0]
        record_date = filtered_df["RecordDate"].dropna().iloc[0]
        hrv_values_df = parse_hrv_values(hrv_values_str, record_date)

        if not hrv_values_df.empty:
            fig_hrv_samples = px.line(hrv_values_df, x="Timestamp", y="HRV", title="HRV Trends Throughout the Day")
            st.plotly_chart(fig_hrv_samples)
        else:
            st.warning("No valid HRV samples available for this participant.")

    # ---- HR Distribution Histogram ----
    st.subheader("📊 Heart Rate Distribution")
    fig_hr_hist = px.histogram(filtered_df, x="HeartRateAvg", title="Heart Rate Distribution (Histogram)", nbins=20)
    st.plotly_chart(fig_hr_hist)

    # ---- Multi-Participant HR Comparison ----
    st.subheader("📌 Heart Rate Comparison Across Participants")
    fig_hr_comp = px.line(filtered_df, x="RecordDate", y="HeartRateAvg", color="Participant Name", title="Heart Rate Trends Across Participants")
    st.plotly_chart(fig_hr_comp)

    # ---- HRV vs. Resting HR Scatter Plot ----
    st.subheader("📉 HRV vs. Resting Heart Rate")
    fig_hrv_scatter = px.scatter(filtered_df, x="RestingHeartRate", y="HRV-avgHRV", title="HRV vs. Resting HR")
    st.plotly_chart(fig_hrv_scatter)

    # ---- HR Zones Stacked Bar Chart ----
    st.subheader("⚡ HR Zone Distribution Across Participants")
    hr_zones_df = filtered_df[["Participant Name", "HRZones_Fatburn", "HRZones_Cardio", "HRZones_Peak"]]
    hr_zones_melted = hr_zones_df.melt(id_vars=["Participant Name"], var_name="HR Zone", value_name="Percentage")
    fig_hr_zones = px.bar(hr_zones_melted, x="Participant Name", y="Percentage", color="HR Zone", barmode="stack", title="HR Zone Distribution")
    st.plotly_chart(fig_hr_zones)
