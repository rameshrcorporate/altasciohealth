import streamlit as st
import pandas as pd
import plotly.express as px

# Load Dataset


# Ensure filtered_df is initialized properly
if 'filtered_df' not in globals():
    st.error("Error: filtered_df is not available. Ensure it is passed from the main app.")
    st.stop()

# Use the already filtered dataset from the main app
filtered_df["RecordDate"] = pd.to_datetime(filtered_df["RecordDate"], errors='coerce')
filtered_df["Week"] = filtered_df["RecordDate"].dt.to_period("W").astype(str)
filtered_df["Month"] = filtered_df["RecordDate"].dt.to_period("M").astype(str)
df = filtered_df

# Use existing filters from main app
# st.sidebar.header("🔍 Filters")
# org_filter = st.sidebar.selectbox("Select Organization", ["All"] + list(df["OrganizationName"].dropna().unique()), key="org_filter")
# filtered_df = df[df["OrganizationName"] == org_filter] if org_filter != "All" else df

# User selection for aggregation level
time_interval = st.radio("Select Time Interval", ["Daily", "Weekly", "Monthly"], horizontal=True)

if time_interval == "Weekly":
    grouped_df = filtered_df.groupby("Week")["Steps"].mean().reset_index()
    x_col = "Week"
elif time_interval == "Monthly":
    grouped_df = filtered_df.groupby("Month")["Steps"].mean().reset_index()
    x_col = "Month"
else:
    grouped_df = filtered_df.groupby("RecordDate")["Steps"].mean().reset_index()
    x_col = "RecordDate"

# Steps Trends Visualization
st.subheader("Steps Trends")
fig_steps = px.line(grouped_df, x=x_col, y="Steps", title=f"Average Steps ({time_interval})")
st.plotly_chart(fig_steps)

# Steps Distribution
st.subheader("Steps Distribution")
fig_dist = px.histogram(filtered_df, x="Steps", title="Steps Distribution (Histogram)", nbins=20)
st.plotly_chart(fig_dist)

# Steps by Organization
st.subheader("Steps by Organization")
org_steps = filtered_df.groupby("OrganizationName")["Steps"].mean().reset_index()
fig_org_steps = px.bar(org_steps, x="OrganizationName", y="Steps", color="OrganizationName", title="Average Steps per Organization")
st.plotly_chart(fig_org_steps)

# Steps by Age Group
st.subheader("Steps by Age Group")
age_steps = filtered_df.groupby("AgeGroup")["Steps"].mean().reset_index()
fig_age_steps = px.bar(age_steps, x="AgeGroup", y="Steps", color="AgeGroup", title="Average Steps per Age Group")
st.plotly_chart(fig_age_steps)

# Steps by Gender
st.subheader("Steps by Gender")
gender_steps = filtered_df.groupby("ParticipantGender")["Steps"].mean().reset_index()
fig_gender_steps = px.bar(gender_steps, x="ParticipantGender", y="Steps", color="ParticipantGender", title="Average Steps per Gender")
st.plotly_chart(fig_gender_steps)

# Steps by Ethnicity
st.subheader("Steps by Ethnicity")
ethnicity_steps = filtered_df.groupby("Ethnicity")["Steps"].mean().reset_index()
fig_ethnicity_steps = px.bar(ethnicity_steps, x="Ethnicity", y="Steps", color="Ethnicity", title="Average Steps per Ethnicity")
st.plotly_chart(fig_ethnicity_steps)

# City-Wise Steps Comparison
st.subheader("Steps by City")
city_steps = filtered_df.groupby("City")["Steps"].mean().reset_index()
fig_city_steps = px.bar(city_steps, x="City", y="Steps", color="City", title="Average Steps per City")
st.plotly_chart(fig_city_steps)

# Top 10 Participants by Steps
st.subheader("Top 10 Participants with Highest Steps")
top_participants = filtered_df.groupby("Participant Name")["Steps"].sum().reset_index().nlargest(10, "Steps")
fig_top_participants = px.bar(top_participants, x="Participant Name", y="Steps", color="Participant Name", title="Top 10 Participants")
st.plotly_chart(fig_top_participants)
