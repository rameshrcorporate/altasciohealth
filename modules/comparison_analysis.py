import streamlit as st
import pandas as pd
import plotly.express as px
import ast

@st.cache_data
def filter_data_by_date(df, start_date, end_date):
    return df[(df['RecordDate'] >= start_date) & (df['RecordDate'] <= end_date)]

def show_page(filtered_df):
    if filtered_df.empty:
        st.warning("⚠️ No data available for the selected filters.")
        return

    # ---- Hierarchical Filters ----
    st.sidebar.header("🔍 Filter Selection")
    
    # Organization filter
    org_filter = st.sidebar.selectbox("Select Organization", ["All"] + list(filtered_df["OrganizationName"].dropna().unique()), key="org_filter_cmp")
    if org_filter != "All":
        filtered_df = filtered_df[filtered_df["OrganizationName"] == org_filter]
    
    # Physician filter
    physician_list = filtered_df["PhysicianName"].dropna().unique()
    physician_filter = st.sidebar.selectbox("Select Physician", ["All"] + list(physician_list), key="physician_filter_cmp")
    if physician_filter != "All":
        filtered_df = filtered_df[filtered_df["PhysicianName"] == physician_filter]
    
    # Select up to 5 participants for comparison under selected physician
    participants_selected = st.sidebar.multiselect("Select Participants", list(filtered_df["Participant Name"].dropna().unique()), key="participant_filter_cmp")
    if participants_selected:
        filtered_df = filtered_df[filtered_df["Participant Name"].isin(participants_selected)]
    
    # ---- Display Selected Profiles ----
    st.subheader("👤 Selected Profiles")
    col1, col2 = st.columns(2)

    if physician_filter != "All":
        physician_photo_url = filtered_df["PhysicianPhoto"].dropna().iloc[0].strip("'")
        with col1:
            st.image(physician_photo_url, width=150, caption=f"Physician: {physician_filter}")

    if participants_selected:
        with col2:
            for participant in participants_selected:
                participant_photo_url = filtered_df[filtered_df["Participant Name"] == participant]["ParticipantPhotoURL"].dropna().iloc[0].strip("'")
                st.image(participant_photo_url, width=100, caption=participant)
    
    # ---- Date Range Selection ----
    st.sidebar.header("📅 Select Date Ranges for Comparison")
    col1, col2 = st.sidebar.columns(2)
    
    start_date_1 = col1.date_input("Start Date - Period 1", pd.to_datetime(filtered_df["RecordDate"].min()))
    end_date_1 = col1.date_input("End Date - Period 1", pd.to_datetime(filtered_df["RecordDate"].max()))
    
    start_date_2 = col2.date_input("Start Date - Period 2", pd.to_datetime(filtered_df["RecordDate"].min()))
    end_date_2 = col2.date_input("End Date - Period 2", pd.to_datetime(filtered_df["RecordDate"].max()))
    
    # Filter datasets by selected date ranges
    df_period_1 = filter_data_by_date(filtered_df, str(start_date_1), str(end_date_1))
    df_period_2 = filter_data_by_date(filtered_df, str(start_date_2), str(end_date_2))

    # ---- Key Metrics Comparison ----
    st.subheader("📊 Key Metrics Comparison")
    metrics = ["HeartRateAvg", "RestingHeartRate", "Steps", "DurationAsleep", "Calories"]
    
    for metric in metrics:
        if metric in df_period_1.columns and metric in df_period_2.columns:
            st.subheader(f"📌 {metric} Comparison")
            col1, col2 = st.columns(2)
            with col1:
                for participant in participants_selected:
                    participant_value_1 = df_period_1[df_period_1["Participant Name"] == participant][metric].mean()
                    st.metric(f"{participant} - Period 1", round(participant_value_1, 2))
            with col2:
                for participant in participants_selected:
                    participant_value_2 = df_period_2[df_period_2["Participant Name"] == participant][metric].mean()
                    st.metric(f"{participant} - Period 2", round(participant_value_2, 2))
    
    # ---- Trend Line Comparison ----
    st.subheader("📈 Trends Over Time")
    for metric in metrics:
        if metric in df_period_1.columns and metric in df_period_2.columns:
            df_period_1["Period"] = "Period 1"
            df_period_2["Period"] = "Period 2"
            df_combined = pd.concat([df_period_1, df_period_2])
            fig_trend = px.line(df_combined, x="RecordDate", y=metric, color="Participant Name", title=f"{metric} Over Time")
            st.plotly_chart(fig_trend)
    
    # ---- Side-by-Side Bar Charts ----
    st.subheader("📊 Side-by-Side Participant Comparison")
    for metric in metrics:
        if metric in df_period_1.columns and metric in df_period_2.columns:
            avg_values_1 = df_period_1.groupby("Participant Name")[metric].mean().reset_index()
            avg_values_2 = df_period_2.groupby("Participant Name")[metric].mean().reset_index()
            avg_values_1["Period"] = "Period 1"
            avg_values_2["Period"] = "Period 2"
            df_avg_combined = pd.concat([avg_values_1, avg_values_2])
            fig_bar = px.bar(df_avg_combined, x="Participant Name", y=metric, color="Period", barmode="group", title=f"{metric} Comparison")
            st.plotly_chart(fig_bar)
