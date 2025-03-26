# import streamlit as st
# import pandas as pd
# import plotly.express as px

import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_survey_data():
    """Load survey dataset from the uploaded Excel file."""
    file_path = "https://althealth.s3.us-east-1.amazonaws.com/survey_responses_singlesheet_PowerBI_Friendly.xlsx"
    df = pd.read_excel(file_path, sheet_name=None)
    return df['Survey Responses'], df['Survey Scores']

# Load the survey dataset
survey_responses, survey_scores = load_survey_data()

# Define function for displaying the survey analysis page
def show_page():
    # ---- Sidebar Filters ----
    st.sidebar.header("🔍 Survey Filters")

    # Hierarchical Filters
    org_filter = st.sidebar.selectbox("Select Organization", ["All"] + list(survey_responses["OrganizationName"].dropna().unique()), key="org_filter_survey")
    filtered_df = survey_responses[survey_responses["OrganizationName"] == org_filter] if org_filter != "All" else survey_responses

    cohort_filter = st.sidebar.selectbox("Select Cohort", ["All"] + list(filtered_df["CohortName"].dropna().unique()), key="cohort_filter_survey")
    filtered_df = filtered_df[filtered_df["CohortName"] == cohort_filter] if cohort_filter != "All" else filtered_df

    physician_filter = st.sidebar.selectbox("Select Physician", ["All"] + list(filtered_df["PhysicianName"].dropna().unique()), key="physician_filter_survey")
    filtered_df = filtered_df[filtered_df["PhysicianName"] == physician_filter] if physician_filter != "All" else filtered_df

    program_filter = st.sidebar.selectbox("Select Program", ["All"] + list(filtered_df["ProgramName"].dropna().unique()), key="program_filter_survey")
    filtered_df = filtered_df[filtered_df["ProgramName"] == program_filter] if program_filter != "All" else filtered_df

    participant_filter = st.sidebar.selectbox("Select Participant", ["All"] + list(filtered_df["Participant Name"].dropna().unique()), key="participant_filter_survey")
    filtered_df = filtered_df[filtered_df["Participant Name"] == participant_filter] if participant_filter != "All" else filtered_df

    # Independent Filters
    gender_filter = st.sidebar.selectbox("Select Gender", ["All"] + list(filtered_df["ParticipantGender"].dropna().unique()), key="gender_filter_survey")
    filtered_df = filtered_df[filtered_df["ParticipantGender"] == gender_filter] if gender_filter != "All" else filtered_df

    ethnicity_filter = st.sidebar.selectbox("Select Ethnicity", ["All"] + list(filtered_df["Ethnicity"].dropna().unique()), key="ethnicity_filter_survey")
    filtered_df = filtered_df[filtered_df["Ethnicity"] == ethnicity_filter] if ethnicity_filter != "All" else filtered_df

    age_group_filter = st.sidebar.selectbox("Select Age Group", ["All"] + list(filtered_df["AgeGroup"].dropna().unique()), key="age_group_filter_survey")
    filtered_df = filtered_df[filtered_df["AgeGroup"] == age_group_filter] if age_group_filter != "All" else filtered_df

    city_filter = st.sidebar.selectbox("Select City", ["All"] + list(filtered_df["City"].dropna().unique()), key="city_filter_survey")
    filtered_df = filtered_df[filtered_df["City"] == city_filter] if city_filter != "All" else filtered_df

    # Survey-Specific Filters
    survey_filter = st.sidebar.selectbox("Select Survey", ["All"] + ["GAD-7", "SUS", "SF-12"], key="survey_filter")
    filtered_df = filtered_df[filtered_df["SurveyName"] == survey_filter] if survey_filter != "All" else filtered_df

    timepoint_filter = st.sidebar.selectbox("Select Timepoint", ["All"] + ["START", "MID", "END"], key="timepoint_filter")
    filtered_df = filtered_df[filtered_df["SurveyTimepoint"] == timepoint_filter] if timepoint_filter != "All" else filtered_df

    # ---- Key Metrics ----
    st.title("📊 Survey Analysis Dashboard")
    st.markdown("### Key Metrics")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Participants", filtered_df["ParticipantID"].nunique())
        st.metric("Total Surveys", filtered_df["SurveyName"].nunique())

    with col2:
        st.metric("Total Submissions", filtered_df.groupby(['ParticipantID', 'SurveyName', 'SurveyTimepoint']).ngroups)
        st.metric("Unique Cohorts", filtered_df["CohortName"].nunique())

    with col3:
        st.metric("Programs Covered", filtered_df.groupby(['OrganizationName', 'CohortName', 'ProgramName']).ngroups)
        st.metric("Physicians Involved", filtered_df.groupby(['OrganizationName', 'PhysicianName']).ngroups)

     # ---- Display Selected Physician & Participant Photos ----
    col1, col2 = st.columns(2)
    if physician_filter != "All":
        physician_photo_url = filtered_df["PhysicianPhoto"].dropna().iloc[0].strip("'")
        with col1:
            st.image(physician_photo_url, width=150, caption=f"Physician: {physician_filter}")
    
    if participant_filter != "All":
        participant_photo_url = filtered_df["ParticipantPhotoURL"].dropna().iloc[0].strip("'")
        with col2:
            st.image(participant_photo_url, width=150, caption=f"Participant: {participant_filter}")
    


    st.subheader("📊 Survey Outcome Category Distribution")

    if filtered_df.empty:
        st.warning("No data available for the selected filters.")
        return

    # Get unique survey names for dropdown
    survey_options = filtered_df["SurveyName"].unique()
    selected_survey = st.selectbox("Select Survey", ["All"] + list(survey_options), key="survey_outcome_filter")

    # Apply filter based on selected survey
    if selected_survey != "All":
        filtered_df = filtered_df[filtered_df["SurveyName"] == selected_survey]

    # ✅ Corrected Grouping: Count each submission only once per survey & timepoint
    grouped_df = (
        filtered_df
        .drop_duplicates(subset=["ParticipantID", "SurveyName", "SurveyTimepoint"])  # Ensures one count per submission
        .groupby(["SurveyName", "SurveyTimepoint", "Outcome Category"])
        .size()
        .reset_index(name="Submission Count")
    )

    # Aggregate to get total submissions per Outcome Category
    outcome_summary = (
        grouped_df
        .groupby(["Outcome Category"])
        ["Submission Count"]
        .sum()
        .reset_index()
    )

    if outcome_summary.empty:
        st.warning("No data available for the selected survey.")
        return

    # ✅ Corrected Bar Chart with Proper Summed Counts
    fig_outcome = px.bar(
        outcome_summary, 
        x="Outcome Category", 
        y="Submission Count",  # ✅ Now matches Total Submissions logic
        color="Outcome Category",
        title=f"Survey Outcome Distribution ({selected_survey})",
        labels={"Outcome Category": "Survey Outcome", "Submission Count": "Number of Submissions"},
        text_auto=True
    )

    # ✅ Adjust Y-axis to correctly reflect large counts
    fig_outcome.update_layout(yaxis=dict(title="Total Submissions", tickformat=","))  # Adds comma formatting

    st.plotly_chart(fig_outcome)
    
    
    st.subheader("📉 Survey Outcome Progression (Start → Mid → End)")

    if filtered_df.empty:
        st.warning("No data available for the selected filters.")
        return

    # Ensure correct grouping to track progression over time
    progression_df = (
        filtered_df
        .groupby(["SurveyName", "SurveyTimepoint", "Outcome Category"])
        .size()
        .reset_index(name="Submission Count")
    )

    if progression_df.empty:
        st.warning("No data available after grouping.")
        return

    # Create a line chart to show how outcome categories progress over time
    fig_progression = px.line(
        progression_df,
        x="SurveyTimepoint",
        y="Submission Count",
        color="Outcome Category",
        markers=True,
        title="Survey Outcome Progression Over Time",
        labels={"SurveyTimepoint": "Survey Phase", "Submission Count": "Number of Submissions"}
    )

    st.plotly_chart(fig_progression)
    
    
    # # Display Selected Physician & Participant Info Side-by-Side
    # if physician_filter != "All" or participant_filter != "All":
        # col1, col2 = st.columns(2)
        
        # with col1:
            # if physician_filter != "All":
                # selected_physician = filtered_df[filtered_df["PhysicianName"] == physician_filter].iloc[0]
                # st.image(selected_physician["PhysicianPhoto"].strip("'"), width=150)
                # st.markdown(f"### {selected_physician['PhysicianName']}")
                # st.markdown(f"Physician")
                # #st.markdown(f"**Gender:** {selected_physician['PhysicianGender']}")
        
        # with col2:
            # if participant_filter != "All":
                # selected_participant = filtered_df[filtered_df["Participant Name"] == participant_filter].iloc[0]
                # st.image(selected_participant["ParticipantPhotoURL"].strip("'"), width=150)
                # st.markdown(f"### {selected_participant['Participant Name']}")
                # st.markdown(f"Participant")
                # st.markdown(f"**Age:** {selected_participant['Age']}, **Gender:** {selected_participant['ParticipantGender']}")
                # st.markdown(f"**Height:** {selected_participant['HeightCm']} cm, **Weight:** {selected_participant['WeightKg']} kg")

    #st.plotly_chart(fig_outcome)
    # ---- Outcome Category Distribution ----
    # st.subheader("📈 Survey Outcome Category Distribution")
    # if not filtered_df.empty:
        # fig_outcome = px.bar(filtered_df, x="Outcome Category", title="Survey Outcome Distribution", color="Outcome Category")
        # st.plotly_chart(fig_outcome)

        # # ---- Survey Score Progression ----
        # st.subheader("📉 Survey Score Progression Over Time")
        # fig_progression = px.line(filtered_df, x="SurveyTimepoint", y="Total Score", color="SurveyName", markers=True, title="Survey Score Trends")
        # st.plotly_chart(fig_progression)

        # # ---- Survey Outcome by Organization ----
        # st.subheader("🏢 Outcome Distribution by Organization")
        # fig_org_outcome = px.bar(filtered_df, x="OrganizationName", y="Total Score", color="Outcome Category", title="Survey Outcome by Organization")
        # st.plotly_chart(fig_org_outcome)

        # # ---- Demographic-Based Trends ----
        # st.subheader("👥 Outcome Category by Age Group")
        # fig_agegroup = px.bar(filtered_df, x="AgeGroup", y="Total Score", color="Outcome Category", title="Survey Outcome by Age Group")
        # st.plotly_chart(fig_agegroup)

        # st.subheader("⚤ Outcome Category by Gender")
        # fig_gender = px.bar(filtered_df, x="ParticipantGender", y="Total Score", color="Outcome Category", title="Survey Outcome by Gender")
        # st.plotly_chart(fig_gender)

        # st.subheader("🌎 Outcome Category by Ethnicity")
        # fig_ethnicity = px.bar(filtered_df, x="Ethnicity", y="Total Score", color="Outcome Category", title="Survey Outcome by Ethnicity")
        # st.plotly_chart(fig_ethnicity)

    # else:
        # st.warning("No data available for the selected filters.")

    # ---- Reset Filters ----
    if st.button("🔄 Reset Filters"):
        st.rerun()


# # Load the Survey Dataset
# @st.cache_data
# def load_survey_data():
    # survey_data_url = "https://althealth.s3.us-east-1.amazonaws.com/survey_responses_singlesheet_PowerBI_Friendly.xlsx"
    # df = pd.read_excel(survey_data_url)
    # return df['Survey Responses'], df['Survey Scores']
    
# survey_responses, survey_scores = load_survey_data()
    

# # Define function for displaying the survey analysis page
# def show_page():
    # # ---- Sidebar Filters ----
    # st.sidebar.header("🔍 Survey Filters")

    # # Hierarchical Filters
    # org_filter = st.sidebar.selectbox("Select Organization", ["All"] + list(survey_responses["OrganizationName"].dropna().unique()), key="org_filter_survey")
    # filtered_df = survey_responses[survey_responses["OrganizationName"] == org_filter] if org_filter != "All" else survey_responses

    # cohort_filter = st.sidebar.selectbox("Select Cohort", ["All"] + list(filtered_df["CohortName"].dropna().unique()), key="cohort_filter_survey")
    # filtered_df = filtered_df[filtered_df["CohortName"] == cohort_filter] if cohort_filter != "All" else filtered_df

    # physician_filter = st.sidebar.selectbox("Select Physician", ["All"] + list(filtered_df["PhysicianName"].dropna().unique()), key="physician_filter_survey")
    # filtered_df = filtered_df[filtered_df["PhysicianName"] == physician_filter] if physician_filter != "All" else filtered_df

    # program_filter = st.sidebar.selectbox("Select Program", ["All"] + list(filtered_df["ProgramName"].dropna().unique()), key="program_filter_survey")
    # filtered_df = filtered_df[filtered_df["ProgramName"] == program_filter] if program_filter != "All" else filtered_df

    # participant_filter = st.sidebar.selectbox("Select Participant", ["All"] + list(filtered_df["ParticipantID"].dropna().unique()), key="participant_filter_survey")
    # filtered_df = filtered_df[filtered_df["ParticipantID"] == participant_filter] if participant_filter != "All" else filtered_df

    # # Independent Filters
    # gender_filter = st.sidebar.selectbox("Select Gender", ["All"] + list(filtered_df["ParticipantGender"].dropna().unique()), key="gender_filter_survey")
    # filtered_df = filtered_df[filtered_df["ParticipantGender"] == gender_filter] if gender_filter != "All" else filtered_df

    # ethnicity_filter = st.sidebar.selectbox("Select Ethnicity", ["All"] + list(filtered_df["Ethnicity"].dropna().unique()), key="ethnicity_filter_survey")
    # filtered_df = filtered_df[filtered_df["Ethnicity"] == ethnicity_filter] if ethnicity_filter != "All" else filtered_df

    # age_group_filter = st.sidebar.selectbox("Select Age Group", ["All"] + list(filtered_df["AgeGroup"].dropna().unique()), key="age_group_filter_survey")
    # filtered_df = filtered_df[filtered_df["AgeGroup"] == age_group_filter] if age_group_filter != "All" else filtered_df

    # city_filter = st.sidebar.selectbox("Select City", ["All"] + list(filtered_df["City"].dropna().unique()), key="city_filter_survey")
    # filtered_df = filtered_df[filtered_df["City"] == city_filter] if city_filter != "All" else filtered_df

    # # Survey-Specific Filters
    # survey_filter = st.sidebar.selectbox("Select Survey", ["All"] + ["GAD-7", "SUS", "SF-12"], key="survey_filter")
    # filtered_df = filtered_df[filtered_df["SurveyName"] == survey_filter] if survey_filter != "All" else filtered_df

    # timepoint_filter = st.sidebar.selectbox("Select Timepoint", ["All"] + ["START", "MID", "END"], key="timepoint_filter")
    # filtered_df = filtered_df[filtered_df["SurveyTimepoint"] == timepoint_filter] if timepoint_filter != "All" else filtered_df

    # # ---- Key Metrics ----
    # st.title("📊 Survey Analysis Dashboard")

    # st.markdown("### Key Metrics")
    # col1, col2, col3 = st.columns(3)

    # with col1:
        # st.metric("Total Participants", filtered_df["ParticipantID"].nunique())
        # st.metric("Total Surveys", filtered_df["SurveyName"].nunique())

    # with col2:
        # st.metric("Total Submissions", len(filtered_df))
        # st.metric("Unique Cohorts", filtered_df["CohortName"].nunique())

    # with col3:
        # st.metric("Programs Covered", filtered_df["ProgramName"].nunique())
        # st.metric("Physicians Involved", filtered_df["PhysicianName"].nunique())

    # # ---- Outcome Category Distribution ----
    # st.subheader("📈 Survey Outcome Category Distribution")
    # fig_outcome = px.bar(filtered_df, x="Outcome Category", title="Survey Outcome Distribution", color="Outcome Category")
    # st.plotly_chart(fig_outcome)

    # # ---- Survey Score Progression ----
    # st.subheader("📉 Survey Score Progression Over Time")
    # fig_progression = px.line(filtered_df, x="SurveyTimepoint", y="Total Score", color="SurveyName", markers=True, title="Survey Score Trends")
    # st.plotly_chart(fig_progression)

    # # ---- Survey Outcome by Organization ----
    # st.subheader("🏢 Outcome Distribution by Organization")
    # fig_org_outcome = px.bar(filtered_df, x="OrganizationName", y="Total Score", color="Outcome Category", title="Survey Outcome by Organization")
    # st.plotly_chart(fig_org_outcome)

    # # ---- Demographic-Based Trends ----
    # st.subheader("👥 Outcome Category by Age Group")
    # fig_agegroup = px.bar(filtered_df, x="AgeGroup", y="Total Score", color="Outcome Category", title="Survey Outcome by Age Group")
    # st.plotly_chart(fig_agegroup)

    # st.subheader("⚤ Outcome Category by Gender")
    # fig_gender = px.bar(filtered_df, x="ParticipantGender", y="Total Score", color="Outcome Category", title="Survey Outcome by Gender")
    # st.plotly_chart(fig_gender)

    # st.subheader("🌎 Outcome Category by Ethnicity")
    # fig_ethnicity = px.bar(filtered_df, x="Ethnicity", y="Total Score", color="Outcome Category", title="Survey Outcome by Ethnicity")
    # st.plotly_chart(fig_ethnicity)

    # # ---- Reset Filters ----
    # if st.button("🔄 Reset Filters"):
        # st.experimental_rerun()
    # # # Load Data
    # # st.title("📊 Survey Analysis Dashboard")
    # # df_survey = load_survey_data()
    
    # # # st.write(f"Total records in full dataset: {df_survey.shape[0]}")
    # # # #st.write("First few rows before filtering:", df_survey.head())
    # # # st.write("Unique Organizations:", df_survey["OrganizationName"].unique())
    # # # st.write("Unique Cohorts:", df_survey["CohortName"].unique())
    # # # st.write("Unique Programs:", df_survey["ProgramName"].unique())
    # # # st.write("Unique Surveys:", df_survey["SurveyName"].unique())
    # # # st.write("Unique Timepoints:", df_survey["SurveyTimepoint"].unique())
    
       # # # # Display Key Summary Metrics
    # # # col1, col2, col3 = st.columns(3)
    
    # # # with col1:
        # # # total_participants = df_survey.groupby(["OrganizationName","CohortName","ProgramName","ProgramDurationWeeks", "ProgramStartDate", "ProgramEndDate",
        # # # "PhysicianName", "PhysicianGender", "PhysicianPhoto", "ParticipantID", "Participant Name", "Email",
        # # # "ParticipantGender", "ParticipantPhotoURL", "WeightKg", "HeightCm", "Ethnicity", "MedicalCondition",
        # # # "City", "Country", "BirthDate", "Age", "AgeGroup"])["Participant Name"].nunique().sum()
        # # # st.metric(label="🧑‍🤝‍🧑 Total Participants", value=total_participants)
    
    # # # with col2:
        # # # total_surveys = df_survey["SurveyName"].nunique()
        # # # st.metric(label="📋 Total Surveys Conducted", value=total_surveys)
    
    # # # with col3:
        # # # total_records = len(df_survey)
        # # # st.metric(label="📊 Total Survey Records", value=total_records)

    # # # Sidebar Filters
    # # st.sidebar.header("🔍 Survey Filters")
    # # organization = st.sidebar.selectbox("Select Organization", ["All"] + list(df_survey["OrganizationName"].dropna().unique()))
    # # cohort = st.sidebar.selectbox("Select Cohort",  ["All"] +list(df_survey[df_survey["OrganizationName"] == organization]["CohortName"].dropna().unique()) if organization != "All" else list(df_survey["CohortName"].dropna().unique()), index=None)
    # # # program = st.sidebar.selectbox("Select Program", ["All"] + list(df_survey[(df_survey["OrganizationName"] == organization) & (df_survey["CohortName"] == cohort)]["ProgramName"].dropna().unique()) if organization != "All" and cohort != "All" else list(df_survey["ProgramName"].dropna().unique()))
    # # # physician = st.sidebar.selectbox("Select Physician", ["All"] + list(df_survey[df_survey["OrganizationName"] == organization]["PhysicianName"].dropna().unique()) if organization != "All" else list(df_survey["PhysicianName"].dropna().unique()))
    # # # participant = st.sidebar.selectbox("Select Participant", ["All"] + list(df_survey[(df_survey["OrganizationName"] == organization) & (df_survey["CohortName"] == cohort) & (df_survey["ProgramName"] == program) & (df_survey["PhysicianName"] == physician)]["Participant Name"].dropna().unique()) if organization != "All" and cohort != "All" and program != "All" and physician != "All" else list(df_survey["Participant Name"].dropna().unique()))
    # # # Ensure "All" is preselected for dependent filters
    # # program_options = ["All"] + list(df_survey[(df_survey["OrganizationName"] == organization) & (df_survey["CohortName"] == cohort)]["ProgramName"].dropna().unique()) if organization != "All" and cohort != "All" else ["All"] + list(df_survey["ProgramName"].dropna().unique())
    # # program = st.sidebar.selectbox("Select Program", program_options, index=0)

    # # # physician_options = ["All"] + list(df_survey[df_survey["OrganizationName"] == organization]["PhysicianName"].dropna().unique()) if organization != "All" else ["All"] + list(df_survey["PhysicianName"].dropna().unique())
    # # # physician = st.sidebar.selectbox("Select Physician", physician_options, index=0)

    # # # participant_options = ["All"] + list(df_survey[(df_survey["OrganizationName"] == organization) & (df_survey["CohortName"] == cohort) & (df_survey["ProgramName"] == program) & (df_survey["PhysicianName"] == physician)]["Participant Name"].dropna().unique()) if organization != "All" and cohort != "All" and program != "All" and physician != "All" else ["All"] + list(df_survey["Participant Name"].dropna().unique())
    # # # participant = st.sidebar.selectbox("Select Participant", participant_options, index=0)    
    
    # # # survey_type = st.sidebar.multiselect("Select Survey Type", df_survey["SurveyName"].unique(), default=[])
    # # # timepoint = st.sidebar.multiselect("Select Timepoint", df_survey["SurveyTimepoint"].unique(), default=[])
    
    # # # # survey_type = st.sidebar.multiselect("Select Survey Type", df_survey["SurveyName"].unique(), default=df_survey["SurveyName"].unique(), default=[])
    # # # # timepoint = st.sidebar.multiselect("Select Timepoint", df_survey["SurveyTimepoint"].unique(), default=df_survey["SurveyTimepoint"].unique(), default=[])

    # # # # Additional Filters
    # # # gender = st.sidebar.selectbox("Select Gender", ["All"] + list(df_survey["ParticipantGender"].dropna().unique()))
    # # # ethnicity = st.sidebar.selectbox("Select Ethnicity", ["All"] + list(df_survey["Ethnicity"].dropna().unique()))
    # # # age_group = st.sidebar.selectbox("Select Age Group", ["All"] + list(df_survey["AgeGroup"].dropna().unique()))
    # # # city = st.sidebar.selectbox("Select City", ["All"] + list(df_survey["City"].dropna().unique()))
    # # # country = st.sidebar.selectbox("Select Country", ["All"] + list(df_survey["Country"].dropna().unique()))
    # # # height_range = st.sidebar.slider("Select Height (Cm) Range", 70, 220, (70, 220))
    # # # weight_range = st.sidebar.slider("Select Weight (Kg) Range", 10, 200, (10, 200))

    # # # Filter Data
    # # filtered_df = df_survey.copy()

    # # if organization and organization != "All" and organization in df_survey["OrganizationName"].values:
        # # filtered_df = filtered_df[filtered_df["OrganizationName"] == organization]

    # # if cohort and cohort != "All" and cohort in df_survey["CohortName"].values:
        # # filtered_df = filtered_df[filtered_df["CohortName"] == cohort]

    # # if program and program != "All" and program in df_survey["ProgramName"].values:
        # # filtered_df = filtered_df[filtered_df["ProgramName"] == program]

    # # if survey_type:
        # # valid_surveys = set(df_survey["SurveyName"].unique())  # Get all valid survey names
        # # survey_type = [s for s in survey_type if s in valid_surveys]  # Keep only valid selections
        # # if survey_type:
            # # filtered_df = filtered_df[filtered_df["SurveyName"].isin(survey_type)]

    # # if timepoint:
        # # valid_timepoints = set(df_survey["SurveyTimepoint"].unique())  # Get all valid timepoints
        # # timepoint = [t for t in timepoint if t in valid_timepoints]  # Keep only valid selections
        # # if timepoint:
            # # filtered_df = filtered_df[filtered_df["SurveyTimepoint"].isin(timepoint)]

    # # #st.write(f"Total records after filtering: {filtered_df.shape[0]}")
    
    
   # # # st.title("📊 Survey Analysis Dashboard")
    # # df_survey = load_survey_data()

    # # # st.write("Columns in filtered_df:", filtered_df.columns.tolist())
    # # # st.write("First few rows of filtered_df:", filtered_df.head())

    # # # Display Key Summary Metrics
    # # col1, col2, col3 = st.columns(3)
    
    # # with col1:
        # # if "Participant Name" in filtered_df.columns:
            # # total_participants = filtered_df["Participant Name"].dropna().nunique()
        # # else:
            # # total_participants = 130  # For testing

        # # # Debugging output
        # # st.write(f"Debug: Total Participants = {total_participants}")

        # # # Ensure it's an integer before displaying
        # # st.metric(label="🧑‍🤝‍🧑 Total Participants", value=int(total_participants))
        # # # total_participants = df_survey.groupby(["OrganizationName","CohortName","ProgramName","ProgramDurationWeeks", "ProgramStartDate", "ProgramEndDate",
        # # # "PhysicianName", "PhysicianGender", "PhysicianPhoto", "ParticipantID", "Participant Name", "Email",
        # # # "ParticipantGender", "ParticipantPhotoURL", "WeightKg", "HeightCm", "Ethnicity", "MedicalCondition",
        # # # "City", "Country", "BirthDate", "Age", "AgeGroup"])["Participant Name"].nunique().sum()
        # # #st.metric(label="🧑‍🤝‍🧑 Total Participants", value=total_participants)
 
    
    # # with col2:
        # # total_surveys = df_survey["SurveyName"].nunique()
        # # st.metric(label="📋 Total Surveys Conducted", value=total_surveys)
    
    # # with col3:
        # # total_records = len(df_survey)
        # # st.metric(label="📊 Total Survey Records", value=total_records)
    
    # # # Survey-Specific Summary Stats
    # # st.subheader("📈 Survey Score Summary")
    # # survey_cols = st.columns(3)
    
    # # # GAD-7 Scores
    # # gad7_avg = df_survey[df_survey["SurveyName"] == "GAD-7"].groupby("SurveyTimepoint")["Total Score"].mean()
    # # with survey_cols[0]:
        # # st.metric(label="GAD-7 Avg Score (Start)", value=round(gad7_avg.get("Start", 0), 2))
        # # st.metric(label="GAD-7 Avg Score (Mid)", value=round(gad7_avg.get("Mid", 0), 2))
        # # st.metric(label="GAD-7 Avg Score (End)", value=round(gad7_avg.get("End", 0), 2))
    
    # # # SF-12 Scores
    # # sf12_avg = df_survey[df_survey["SurveyName"] == "SF-12"].groupby("SurveyTimepoint")["Total Score"].mean()
    # # with survey_cols[1]:
        # # st.metric(label="SF-12 Avg Score (Start)", value=round(sf12_avg.get("Start", 0), 2))
        # # st.metric(label="SF-12 Avg Score (Mid)", value=round(sf12_avg.get("Mid", 0), 2))
        # # st.metric(label="SF-12 Avg Score (End)", value=round(sf12_avg.get("End", 0), 2))
    
    # # # SUS Scores
    # # sus_avg = df_survey[df_survey["SurveyName"] == "SUS"].groupby("SurveyTimepoint")["Total Score"].mean()
    # # with survey_cols[2]:
        # # st.metric(label="SUS Avg Score (Start)", value=round(sus_avg.get("Start", 0), 2))
        # # st.metric(label="SUS Avg Score (Mid)", value=round(sus_avg.get("Mid", 0), 2))
        # # st.metric(label="SUS Avg Score (End)", value=round(sus_avg.get("End", 0), 2))

    # # # Visualization: Survey Outcome Distribution
# # # Visualization: Survey Outcome Distribution Per Timepoint
    # # st.subheader("📊 Survey Outcome Distribution")

    # # selected_survey = st.selectbox("Select Survey for Outcome Analysis", df_survey["SurveyName"].unique())

    # # if selected_survey:
        # # outcome_counts = df_survey[df_survey["SurveyName"] == selected_survey].groupby(["SurveyTimepoint", "Outcome Category"])["Participant Name"].nunique().unstack()

        # # st.bar_chart(outcome_counts)
    
    
    
     # # # Display Selected Physician & Participant Info Side-by-Side
    # # if physician != "All" or participant != "All":
        # # col1, col2 = st.columns(2)
        
        # # with col1:
            # # if physician != "All":
                # # selected_physician = df_survey[df_survey["PhysicianName"] == physician].iloc[0]
                # # st.image(selected_physician["PhysicianPhoto"].strip("'"), width=150)
                # # st.markdown(f"### {selected_physician['PhysicianName']}")
                # # st.markdown(f"Physician")
                # # #st.markdown(f"**Gender:** {selected_physician['PhysicianGender']}")
        
        # # with col2:
            # # if participant != "All":
                # # selected_participant = df_survey[df_survey["Participant Name"] == participant].iloc[0]
                # # st.image(selected_participant["ParticipantPhotoURL"].strip("'"), width=150)
                # # st.markdown(f"### {selected_participant['Participant Name']}")
                # # st.markdown(f"Participant")
                # # st.markdown(f"**Age:** {selected_participant['Age']}, **Gender:** {selected_participant['ParticipantGender']}")
                # # st.markdown(f"**Height:** {selected_participant['HeightCm']} cm, **Weight:** {selected_participant['WeightKg']} kg")
                
                
        # # if participant != "All":
            # # st.subheader(f"📈 {participant} - Score Progression Over Time")
            # # participant_data = df_survey[df_survey["Participant Name"] == participant]
            # # if not participant_data.empty:
                # # fig = px.line(participant_data, x="SurveyTimepoint", y="Total Score", color="SurveyName", markers=True, title=f"Survey Score Trend for {participant}")
                # # st.plotly_chart(fig)
            # # else:
                # # st.warning("No data available for the selected participant.")                
    
    # # # if physician != "All":
        # # # selected_physician = df_survey[df_survey["PhysicianName"] == physician].iloc[0]
        # # # st.image(selected_physician["PhysicianPhoto"].strip("'"), width=150)
        # # # st.markdown(f"### {selected_physician['PhysicianName']}")
        # # # st.markdown(f"**Gender:** {selected_physician['PhysicianGender']}")
       # # # # st.markdown(f"**Height:** {selected_participant['HeightCm']} cm, **Weight:** {selected_participant['WeightKg']} kg")

    # # # # Display Selected Participant Info
    # # # if participant != "All":
        # # # selected_participant = df_survey[df_survey["Participant Name"] == participant].iloc[0]
        # # # st.image(selected_participant["ParticipantPhotoURL"].strip("'"), width=150)
        # # # st.markdown(f"### {selected_participant['Participant Name']}")
        # # # st.markdown(f"**Age:** {selected_participant['Age']}, **Gender:** {selected_participant['ParticipantGender']}")
        # # # st.markdown(f"**Height:** {selected_participant['HeightCm']} cm, **Weight:** {selected_participant['WeightKg']} kg")
        
        


    # # # # Survey Score Trend (Line Chart)
    # # # st.subheader("📈 Survey Score Trends Over Time")
    # # # fig_trend = px.line(filtered_df, x="SurveyTimepoint", y="Total Score", color="Participant Name", markers=True, title="Survey Score Trend by Timepoint")
    # # # st.plotly_chart(fig_trend)

    # # # # Survey Category Distribution (Stacked Bar Chart)
    # # # st.subheader("📊 Survey Category Distribution")
    # # # fig_category = px.bar(filtered_df, x="SurveyTimepoint", color="Outcome Category", title="Survey Outcome Distribution")
    # # # st.plotly_chart(fig_category)

    # # # # Organization & Program Comparisons (Bar Chart)
    # # # st.subheader("📊 Organization & Program Comparisons")
    # # # fig_org = px.bar(filtered_df, x="OrganizationName", y="Total Score", color="ProgramName", title="Survey Score by Organization and Program")
    # # # st.plotly_chart(fig_org)

    # # # # Demographic Analysis (Grouped Bar Chart)
    # # # st.subheader("📊 Demographic Analysis")
    # # # fig_demo = px.bar(filtered_df, x="AgeGroup", y="Total Score", color="ParticipantGender", barmode="group", title="Survey Scores by Age & Gender")
    # # # st.plotly_chart(fig_demo)

    # # # # Survey Trends by City & Country
    # # # st.subheader("🌍 City & Country Survey Trends")
    # # # fig_city = px.bar(filtered_df, x="City", y="Total Score", color="Country", title="Survey Scores by City & Country")
    # # # st.plotly_chart(fig_city)
