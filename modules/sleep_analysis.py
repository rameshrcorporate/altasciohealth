import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def aggregate_sleep(filtered_df, time_interval):
    """ Aggregates sleep duration (converted to hours) based on selected time interval. """
    filtered_df["DurationAsleepHours"] = filtered_df["DurationAsleep"] / 3600  # Convert to hours
    if time_interval == "Weekly" and "Week" in filtered_df.columns:
        return filtered_df.groupby("Week")["DurationAsleepHours"].mean().reset_index(), "Week"
    elif time_interval == "Monthly" and "Month" in filtered_df.columns:
        return filtered_df.groupby("Month")["DurationAsleepHours"].mean().reset_index(), "Month"
    return filtered_df.groupby("RecordDate")["DurationAsleepHours"].mean().reset_index(), "RecordDate"

def show_page(filtered_df):
    """ Displays the Sleep Analysis Page with hierarchical filtering and sleep duration in hours. """
    if filtered_df.empty:
        st.warning("⚠️ No data available for the selected filters.")
        return
    filtered_df = filtered_df.copy()
    filtered_df["DurationAsleepHours"] = filtered_df["DurationAsleep"] / 3600  # Convert to hours

    # ---- Hierarchical Filters ----
    st.sidebar.header("🔍 Filter Selection")

    # 1️⃣ Organization Filter (Unique Key)
    org_filter = st.sidebar.selectbox("Select Organization", ["All"] + list(filtered_df["OrganizationName"].dropna().unique()), key="org_filter_sleep")
    if org_filter != "All":
        filtered_df = filtered_df[filtered_df["OrganizationName"] == org_filter]

    # 2️⃣ Physician Filter (Dependent on Organization)
    physician_list = filtered_df["PhysicianName"].dropna().unique()
    physician_filter = st.sidebar.selectbox("Select Physician", ["All"] + list(physician_list), key="physician_filter_sleep")
    if physician_filter != "All":
        filtered_df = filtered_df[filtered_df["PhysicianName"] == physician_filter]

    # 3️⃣ Participant Filter (Dependent on Physician)
    participant_list = filtered_df["Participant Name"].dropna().unique()
    participant_filter = st.sidebar.selectbox("Select Participant", ["All"] + list(participant_list), key="participant_filter_sleep")
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
    grouped_df, x_col = aggregate_sleep(filtered_df, time_interval)

    # ---- Sleep Trends Visualization ----
    st.subheader("😴 Sleep Duration Trends")
    fig_sleep = px.line(grouped_df, x=x_col, y="DurationAsleepHours", title=f"Average Sleep Duration ({time_interval}) in Hours")
    st.plotly_chart(fig_sleep)

    # ---- Sleep Efficiency ----
    st.subheader("⚡ Sleep Efficiency")
    avg_sleep_efficiency = filtered_df["SleepEfficiency"].mean()
    st.metric("Average Sleep Efficiency (%)", round(avg_sleep_efficiency, 2))

    # ---- Sleep Stages Breakdown ----
    st.subheader("🌙 Sleep Stages Breakdown (Hours)")
    sleep_stages = filtered_df[["DeepSleep", "LightSleep", "REMSleep", "AwakeTime"]].mean() / 3600  # Convert to hours
    sleep_stages_df = pd.DataFrame({"Stage": sleep_stages.index, "Duration (Hours)": sleep_stages.values})
    fig_sleep_stages = px.pie(sleep_stages_df, names="Stage", values="Duration (Hours)", title="Average Time Spent in Each Sleep Stage")
    st.plotly_chart(fig_sleep_stages)

    # ---- Sleep Duration Distribution ----
    st.subheader("📊 Sleep Duration Distribution")
    fig_sleep_dist = px.histogram(filtered_df, x="DurationAsleepHours", title="Distribution of Sleep Duration (Histogram in Hours)", nbins=20)
    st.plotly_chart(fig_sleep_dist)

    # ---- Sleep by Organization ----
    st.subheader("🏢 Sleep Duration by Organization")
    org_sleep = filtered_df.groupby("OrganizationName")["DurationAsleepHours"].mean().reset_index()
    fig_org_sleep = px.bar(org_sleep, x="OrganizationName", y="DurationAsleepHours", color="OrganizationName", title="Average Sleep Duration per Organization (Hours)")
    st.plotly_chart(fig_org_sleep)

    # ---- Sleep by Age Group ----
    st.subheader("👥 Sleep by Age Group")
    age_sleep = filtered_df.groupby("AgeGroup")["DurationAsleepHours"].mean().reset_index()
    fig_age_sleep = px.bar(age_sleep, x="AgeGroup", y="DurationAsleepHours", color="AgeGroup", title="Average Sleep Duration per Age Group (Hours)")
    st.plotly_chart(fig_age_sleep)

    # ---- Sleep by Gender ----
    st.subheader("⚤ Sleep by Gender")
    gender_sleep = filtered_df.groupby("ParticipantGender")["DurationAsleepHours"].mean().reset_index()
    fig_gender_sleep = px.bar(gender_sleep, x="ParticipantGender", y="DurationAsleepHours", color="ParticipantGender", title="Average Sleep Duration per Gender (Hours)")
    st.plotly_chart(fig_gender_sleep)

    # ---- Sleep by Ethnicity ----
    st.subheader("🌎 Sleep by Ethnicity")
    ethnicity_sleep = filtered_df.groupby("Ethnicity")["DurationAsleepHours"].mean().reset_index()
    fig_ethnicity_sleep = px.bar(ethnicity_sleep, x="Ethnicity", y="DurationAsleepHours", color="Ethnicity", title="Average Sleep Duration per Ethnicity (Hours)")
    st.plotly_chart(fig_ethnicity_sleep)

    # ---- City-Wise Sleep Comparison ----
    st.subheader("🏙️ Sleep by City")
    city_sleep = filtered_df.groupby("City")["DurationAsleepHours"].mean().reset_index()
    fig_city_sleep = px.bar(city_sleep, x="City", y="DurationAsleepHours", color="City", title="Average Sleep Duration per City (Hours)")
    st.plotly_chart(fig_city_sleep)

    # ---- Top 10 Participants with Highest Sleep ----
    st.subheader("🏆 Top 10 Participants with Highest Sleep Duration")
    top_sleepers = filtered_df.groupby("Participant Name")["DurationAsleepHours"].sum().reset_index().nlargest(10, "DurationAsleepHours")
    fig_top_sleepers = px.bar(top_sleepers, x="Participant Name", y="DurationAsleepHours", color="Participant Name", title="Top 10 Participants by Sleep Duration (Hours)")
    st.plotly_chart(fig_top_sleepers)
