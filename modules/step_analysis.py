import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def aggregate_steps(filtered_df, time_interval):
    """ Aggregates steps based on selected time interval. """
    if time_interval == "Weekly" and "Week" in filtered_df.columns:
        return filtered_df.groupby("Week")["Steps"].mean().reset_index(), "Week"
    elif time_interval == "Monthly" and "Month" in filtered_df.columns:
        return filtered_df.groupby("Month")["Steps"].mean().reset_index(), "Month"
    return filtered_df.groupby("RecordDate")["Steps"].mean().reset_index(), "RecordDate"

def show_page(filtered_df):
    """ Displays the Steps Analysis Page with Hierarchical Filtering. """
    if filtered_df.empty:
        st.warning("⚠️ No data available for the selected filters.")
        return

    # ---- Hierarchical Filters ----
    st.sidebar.header("🔍 Filter Selection")

    # 1️⃣ Organization Filter (Unique Key)
    org_filter = st.sidebar.selectbox("Select Organization", ["All"] + list(filtered_df["OrganizationName"].dropna().unique()), key="org_filter_steps")
    if org_filter != "All":
        filtered_df = filtered_df[filtered_df["OrganizationName"] == org_filter]

    # 2️⃣ Physician Filter (Unique Key, Dependent on Organization)
    physician_list = filtered_df["PhysicianName"].dropna().unique()
    physician_filter = st.sidebar.selectbox("Select Physician", ["All"] + list(physician_list), key="physician_filter_steps")
    if physician_filter != "All":
        filtered_df = filtered_df[filtered_df["PhysicianName"] == physician_filter]

    # 3️⃣ Participant Filter (Unique Key, Dependent on Physician)
    participant_list = filtered_df["Participant Name"].dropna().unique()
    participant_filter = st.sidebar.selectbox("Select Participant", ["All"] + list(participant_list), key="participant_filter_steps")
    if participant_filter != "All":
        filtered_df = filtered_df[filtered_df["Participant Name"] == participant_filter]

    # ---- Display Selected Profiles ----
    st.subheader("👤 Selected Profiles")
    col1, col2 = st.columns(2)

    if physician_filter != "All":
        physician_photo_url = filtered_df["PhysicianPhoto"].dropna().iloc[0].strip("'")  # Remove single quote prefix
        with col1:
            st.image(physician_photo_url, width=150, caption=f"Physician: {physician_filter}")

    if participant_filter != "All":
        participant_photo_url = filtered_df["ParticipantPhotoURL"].dropna().iloc[0].strip("'")  # Remove single quote prefix
        with col2:
            st.image(participant_photo_url, width=150, caption=f"Participant: {participant_filter}")

    # ---- User selection for aggregation level ----
    time_interval = st.radio("Select Time Interval", ["Daily", "Weekly", "Monthly"], horizontal=True)

    # Ensure the filtered dataset is used for calculations
    grouped_df, x_col = aggregate_steps(filtered_df, time_interval)

    # ---- Steps Trends Visualization ----
    st.subheader("📈 Steps Trends")
    fig_steps = px.line(grouped_df, x=x_col, y="Steps", title=f"Average Steps ({time_interval})")
    st.plotly_chart(fig_steps)

    # ---- Steps Distribution ----
    st.subheader("📊 Steps Distribution")
    fig_dist = px.histogram(filtered_df, x="Steps", title="Steps Distribution (Histogram)", nbins=20)
    st.plotly_chart(fig_dist)

    # ---- Steps by Organization ----
    st.subheader("🏢 Steps by Organization")
    org_steps = filtered_df.groupby("OrganizationName")["Steps"].mean().reset_index()
    fig_org_steps = px.bar(org_steps, x="OrganizationName", y="Steps", color="OrganizationName", title="Average Steps per Organization")
    st.plotly_chart(fig_org_steps)

    # ---- Steps by Age Group ----
    st.subheader("👥 Steps by Age Group")
    age_steps = filtered_df.groupby("AgeGroup")["Steps"].mean().reset_index()
    fig_age_steps = px.bar(age_steps, x="AgeGroup", y="Steps", color="AgeGroup", title="Average Steps per Age Group")
    st.plotly_chart(fig_age_steps)

    # ---- Steps by Gender ----
    st.subheader("⚤ Steps by Gender")
    gender_steps = filtered_df.groupby("ParticipantGender")["Steps"].mean().reset_index()
    fig_gender_steps = px.bar(gender_steps, x="ParticipantGender", y="Steps", color="ParticipantGender", title="Average Steps per Gender")
    st.plotly_chart(fig_gender_steps)

    # ---- Steps by Ethnicity ----
    st.subheader("🌎 Steps by Ethnicity")
    ethnicity_steps = filtered_df.groupby("Ethnicity")["Steps"].mean().reset_index()
    fig_ethnicity_steps = px.bar(ethnicity_steps, x="Ethnicity", y="Steps", color="Ethnicity", title="Average Steps per Ethnicity")
    st.plotly_chart(fig_ethnicity_steps)

    # ---- City-Wise Steps Comparison ----
    st.subheader("🏙️ Steps by City")
    city_steps = filtered_df.groupby("City")["Steps"].mean().reset_index()
    fig_city_steps = px.bar(city_steps, x="City", y="Steps", color="City", title="Average Steps per City")
    st.plotly_chart(fig_city_steps)

    # ---- Top 10 Participants by Steps ----
    st.subheader("🏆 Top 10 Participants with Highest Steps")
    top_participants = filtered_df.groupby("Participant Name")["Steps"].sum().reset_index().nlargest(10, "Steps")
    fig_top_participants = px.bar(top_participants, x="Participant Name", y="Steps", color="Participant Name", title="Top 10 Participants")
    st.plotly_chart(fig_top_participants)
