import streamlit as st
import pandas as pd
import plotly.express as px

# Load Dataset from S3 or Local File
S3_DATA_URL = "https://althealth.s3.us-east-1.amazonaws.com/Synthetic_Dataset_Metrics_Final_Fixed.xlsx"

@st.cache_data
def load_data():
    df = pd.read_excel(S3_DATA_URL)
    df["RecordDate"] = pd.to_datetime(df["RecordDate"], errors='coerce')
    df["Week"] = df["RecordDate"].dt.to_period("W").astype(str)
    df["Month"] = df["RecordDate"].dt.to_period("M").astype(str)
    return df


# Load the dataset
with st.spinner("Loading data, please wait..."):
    df = load_data()

# Sidebar Filters
st.sidebar.header("🔍 Filters")
org_filter = st.sidebar.selectbox("Select Organization", ["All"] + list(df["OrganizationName"].dropna().unique()), key="org_filter")
filtered_df = df[df["OrganizationName"] == org_filter] if org_filter != "All" else df

cohort_filter = st.sidebar.selectbox("Select Cohort", ["All"] + list(filtered_df["CohortName"].dropna().unique()), key="cohort_filter")
filtered_df = filtered_df[filtered_df["CohortName"] == cohort_filter] if cohort_filter != "All" else filtered_df

program_filter = st.sidebar.selectbox("Select Program", ["All"] + list(filtered_df["ProgramName"].dropna().unique()), key="program_filter")
filtered_df = filtered_df[filtered_df["ProgramName"] == program_filter] if program_filter != "All" else filtered_df

gender_filter = st.sidebar.selectbox("Select Gender", ["All"] + list(filtered_df["ParticipantGender"].dropna().unique()), key="gender_filter")
filtered_df = filtered_df[filtered_df["ParticipantGender"] == gender_filter] if gender_filter != "All" else filtered_df

ethnicity_filter = st.sidebar.selectbox("Select Ethnicity", ["All"] + list(filtered_df["Ethnicity"].dropna().unique()), key="ethnicity_filter")
filtered_df = filtered_df[filtered_df["Ethnicity"] == ethnicity_filter] if ethnicity_filter != "All" else filtered_df

age_group_filter = st.sidebar.selectbox("Select Age Group", ["All"] + list(filtered_df["AgeGroup"].dropna().unique()), key="age_group_filter")
filtered_df = filtered_df[filtered_df["AgeGroup"] == age_group_filter] if age_group_filter != "All" else filtered_df

city_filter = st.sidebar.selectbox("Select City", ["All"] + list(filtered_df["City"].dropna().unique()), key="city_filter")
filtered_df = filtered_df[filtered_df["City"] == city_filter] if city_filter != "All" else filtered_df

# Range Filters
weight_range = st.sidebar.slider("Select Weight (Kg) Range", 10, 200, (10, 200), key="weight_filter")
filtered_df = filtered_df[(filtered_df["WeightKg"] >= weight_range[0]) & (filtered_df["WeightKg"] <= weight_range[1])]

height_range = st.sidebar.slider("Select Height (Cm) Range", 70, 220, (70, 220), key="height_filter")
filtered_df = filtered_df[(filtered_df["HeightCm"] >= height_range[0]) & (filtered_df["HeightCm"] <= height_range[1])]

# Date Range Filter (Fixed to 2024-2025)
from_date = st.sidebar.date_input("From Date", pd.to_datetime("2024-01-01"), key="from_date")
to_date = st.sidebar.date_input("To Date", pd.to_datetime("2025-12-31"), key="to_date")

if from_date > to_date:
    st.sidebar.error("❌ 'From Date' cannot be greater than 'To Date'. Please adjust the selection.")
else:
    filtered_df = filtered_df[(filtered_df["RecordDate"] >= pd.to_datetime(from_date)) & (filtered_df["RecordDate"] <= pd.to_datetime(to_date))]

# Main Page Navigation
st.title("Wellness & Activity Tracking Dashboard")
page = st.radio("Select Analysis", ["Main Dashboard", "Steps Analysis", "Sleep Analysis", "Heart Rate Analysis", "Comparison Analysis"], horizontal=True)

# Display the selected page
if page == "Main Dashboard":
    total_participants = filtered_df["ParticipantID"].nunique()
    avg_steps = filtered_df["Steps"].mean()
    avg_sleep = filtered_df["DurationAsleep"].mean() / 3600  # Convert seconds to hours
    avg_hr = filtered_df["HeartRateAvg"].mean()

    total_programs = filtered_df["ProgramName"].nunique()
    total_cohorts = filtered_df["CohortName"].nunique()
    total_cities = filtered_df["City"].nunique()
    total_age_groups = filtered_df["AgeGroup"].nunique()
    avg_weight = filtered_df["WeightKg"].mean()
    avg_height = filtered_df["HeightCm"].mean()
    
    st.markdown("### Key Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Participants", total_participants)
        st.metric("Total Programs", total_programs)
    with col2:
        st.metric("Total Cohorts", total_cohorts)
        st.metric("Cities Covered", total_cities)
    with col3:
        st.metric("Avg Steps", round(avg_steps, 2))
        st.metric("Avg Sleep Duration (hrs)", round(avg_sleep, 2))
    
    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric("Avg Heart Rate", round(avg_hr, 2))
    with col5:
        st.metric("Avg Weight", round(avg_weight, 2))
    with col6:
        st.metric("Avg Height", round(avg_height, 2))

    # Organization-Level Wellness Overview (Moved to Top)
    # st.subheader("Organization-Level Wellness Overview")
    # filtered_df["ParticipantID"] = filtered_df["ParticipantID"].astype(str)  # Ensure ParticipantID is string for visualization
    # fig_org = px.treemap(filtered_df, path=["OrganizationName"], values="Steps", color="Steps", title="Participants & Steps Levels per Organization")
    # st.plotly_chart(fig_org)
 # # Organization-Level Wellness Overview (Moved to Top)
    # st.subheader("Organization-Level Wellness Overview")
    # filtered_df["ParticipantID"] = filtered_df["ParticipantID"].astype(str)  # Ensure ParticipantID is string for visualization
    # org_avg_steps = filtered_df.groupby("OrganizationName")["Steps"].mean().reset_index()
    # fig_org = px.bar(org_avg_steps, x="OrganizationName", y="Steps", color="OrganizationName", title="Average Steps per Organization")
    # st.plotly_chart(fig_org)
    # # Additional Wellness Breakdown Visualizations
    # filtered_df["DurationAsleepHours"] = filtered_df["DurationAsleep"] / 3600  # Convert sleep duration once before the loop
    # for col, title in zip(["AgeGroup", "Ethnicity", "ParticipantGender", "City"],
                           # ["Age Group", "Ethnicity", "Gender", "City"]):
        # st.subheader(f"Wellness Breakdown by {title}")
        # filtered_df["DurationAsleepHours"] = filtered_df["DurationAsleep"] / 3600
        # fig = px.bar(filtered_df, x=col, y=["Steps", "DurationAsleepHours", "HeartRateAvg"], barmode="group", title=f"Comparison Across {title}", text="value")
        # fig.update_layout(yaxis_title='Value', showlegend=True)
        # fig.update_traces(textposition='auto')
        # fig.update_layout(yaxis_title=None, showlegend=True)
        # fig.update_traces(textposition='outside')
        # st.plotly_chart(fig)
    
      # Organization-Wise Participant Distribution
    st.subheader("Organization-Wise Participant Distribution")
    org_participants = filtered_df.groupby("OrganizationName")["ParticipantID"].nunique().reset_index()
    fig_org_part = px.bar(org_participants, x="OrganizationName", y="ParticipantID", title="Participants per Organization")
    st.plotly_chart(fig_org_part)

    # # Cohort & Program  Distribution
    # st.subheader("Cohort & Program Distribution")
    # cohort_program_counts = filtered_df.groupby(["OrganizationName","CohortName", "ProgramName"]).size().reset_index(name="Count")
    # fig_cohort_program = px.bar(cohort_program_counts, x="CohortName", y="Count", color="ProgramName", title="Programs per Cohort", barmode="stack")
    # st.plotly_chart(fig_cohort_program)
    
    # City-Wise Participant Distribution
    st.subheader("Cohort-Wise Program Distribution")
    city_participants = filtered_df.groupby(["OrganizationName","CohortName"])["ProgramName"].nunique().reset_index()
    fig_city_part = px.bar(city_participants, x="CohortName", y="ProgramName", title="ProgramName per Cohort")
    st.plotly_chart(fig_city_part)

    # City-Wise Participant Distribution
    st.subheader("City-Wise Participant Distribution")
    city_participants = filtered_df.groupby(["OrganizationName","City"])["ParticipantID"].nunique().reset_index()
    fig_city_part = px.bar(city_participants, x="City", y="ParticipantID", title="Participants per City")
    st.plotly_chart(fig_city_part)
    
        # City-Wise Participant Distribution
    st.subheader("Gender-Wise Participant Distribution")
    city_participants = filtered_df.groupby(["OrganizationName","ParticipantGender"])["ParticipantID"].nunique().reset_index()
    fig_city_part = px.bar(city_participants, x="ParticipantGender", y="ParticipantID", title="Participants per Gender")
    st.plotly_chart(fig_city_part)
    
      # City-Wise Participant Distribution
    st.subheader("AgeGroup-Wise Participant Distribution")
    city_participants = filtered_df.groupby(["OrganizationName","AgeGroup"])["ParticipantID"].nunique().reset_index()
    fig_city_part = px.bar(city_participants, x="AgeGroup", y="ParticipantID", title="Participants per AgeGroup")
    st.plotly_chart(fig_city_part)
    
       # City-Wise Participant Distribution
    st.subheader("Ethnicity-Wise Participant Distribution")
    city_participants = filtered_df.groupby(["OrganizationName","Ethnicity"])["ParticipantID"].nunique().reset_index()
    fig_city_part = px.bar(city_participants, x="Ethnicity", y="ParticipantID", title="Participants per Ethnicity")
    st.plotly_chart(fig_city_part)
    
    

    # # Physician-to-Participant Ratio
    # st.subheader("Physician-to-Participant Ratio")
    # physician_participants = filtered_df.groupby("OrganizationName")["PhysicianName"].nunique().reset_index()
    # physician_participants = physician_participants.rename(columns={"PhysicianName": "PhysicianCount"})
    # physician_participants["ParticipantCount"] = org_participants["ParticipantID"]
    # fig_physician_ratio = px.bar(physician_participants, x="OrganizationName", y=["PhysicianCount", "ParticipantCount"], barmode="group", title="Physician vs. Participant Count per Organization")
    # st.plotly_chart(fig_physician_ratio)

    # # Gender Distribution
    # st.subheader("Gender Distribution")
    # gender_counts = filtered_df["ParticipantGender"].value_counts().reset_index()
    # fig_gender = px.bar(gender_counts, x="index", y="ParticipantGender", title="Participants by Gender")
    # st.plotly_chart(fig_gender)

    # # # Ethnicity Distribution
    # # st.subheader("Ethnicity Distribution")
    # # ethnicity_counts = filtered_df["Ethnicity"].value_counts().reset_index()
    # # fig_ethnicity = px.bar(ethnicity_counts, x="index", y="Ethnicity", title="Participants by Ethnicity")
    # # st.plotly_chart(fig_ethnicity)

    # # Age Group Distribution
    # st.subheader("Age Group Distribution")
    # agegroup_counts = filtered_df["AgeGroup"].value_counts().reset_index()
    # fig_agegroup = px.bar(agegroup_counts, x="index", y="AgeGroup", title="Participants by Age Group")
    # st.plotly_chart(fig_agegroup)
    
    
    
    
    # # Overall Activity Trend
    # st.subheader("Trends - Steps")
    # fig_steps = px.line(filtered_df, x="RecordDate", y="Steps", title="Daily Steps Trend")
    # st.plotly_chart(fig_steps)

    # st.subheader("Trends - Sleep")
    # filtered_df["DurationAsleepHours"] = filtered_df["DurationAsleep"] / 3600  # Convert sleep duration to hours
    # fig_sleep = px.line(filtered_df, x="RecordDate", y="DurationAsleepHours", title="Daily Sleep Duration Trend (Hours)")
    # st.plotly_chart(fig_sleep)

    # st.subheader("Trends - Heart Rate")
    # fig_hr = px.line(filtered_df, x="RecordDate", y="HeartRateAvg", title="Daily Average Heart Rate Trend")
    # st.plotly_chart(fig_hr)
    
    # # Anomalies Over Time
    # st.subheader("Anomalies Over Time")
    # anomaly_counts = filtered_df.groupby("RecordDate")["AnomalyType"].count().reset_index()
    # fig_anomalies = px.bar(anomaly_counts, x="RecordDate", y="AnomalyType", title="Anomalies Detected Over Time")
    # st.plotly_chart(fig_anomalies)
else:
    page_mapping = {
        "Steps Analysis": "modules.step_analysis",
        "Sleep Analysis": "modules.sleep_analysis",
        "Heart Rate Analysis": "modules.heart_rate_analysis",
        "Comparison Analysis": "modules.comparison_analysis"
    }
    
    if page in page_mapping:
        module = __import__(page_mapping[page], fromlist=['show_page'])
        module.show_page(filtered_df)
