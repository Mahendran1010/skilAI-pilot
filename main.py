from dotenv import load_dotenv
load_dotenv()

import os
import re
import json
import threading
from datetime import datetime, timedelta
import streamlit as st
from crew import WorkflowCrew
from auth.auth_service import AuthService
from services.email_service import EmailService
from services.job_service import fetch_remoteok_jobs

st.set_page_config(
    page_title="FREE AI Workflow Optimizer",
    page_icon="🚀",
    layout="wide"
)

# ------------------------------------------------
# SESSION STATE INIT
# ------------------------------------------------
if "user" not in st.session_state:
    st.session_state.user = None

# ------------------------------------------------
# LOGIN / SIGNUP SCREEN
# ------------------------------------------------
if st.session_state.user is None:
    st.title("🔐 Login to Continue")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            success, result = AuthService.login_user(email, password)
            if success:
                st.session_state.user = result
                st.success("Login successful!")
                st.rerun()
            else:
                st.error(result)

    with tab2:
        new_email = st.text_input("New Email")
        new_password = st.text_input("New Password", type="password")
        if st.button("Create Account"):
            success, message = AuthService.register_user(new_email, new_password)
            if success:
                st.success(message)
            else:
                st.error(message)

    st.stop()

# ------------------------------------------------
# AFTER LOGIN → YOUR ORIGINAL UI STARTS
# ------------------------------------------------
user = st.session_state.user
st.sidebar.success(f"Logged in as {user.email}")
if st.sidebar.button("Logout"):
    st.session_state.user = None
    st.rerun()

# ------------------------------------------------
# CUSTOM CSS
# ------------------------------------------------
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #4285F4, #34A853, #FBBC05, #EA4335);
        color: white;
        font-size: 18px;
        padding: 10px;
        border: none;
    }
    .free-badge {
        background: linear-gradient(90deg, #4285F4, #EA4335);
        color: white;
        padding: 8px 16px;
        border-radius: 25px;
        font-size: 14px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 10px;
    }
    .feature-box {
        padding: 15px;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------
# HEADER
# ------------------------------------------------
st.markdown('<div class="free-badge">✨ 100% FREE - Powered by Google Gemini ✨</div>', unsafe_allow_html=True)
st.title("🤖 AI Workflow Optimizer SkillPilot AI")
st.markdown("**No payment required - Just your Google account!**")

# ------------------------------------------------
# CHECK GOOGLE API KEY
# ------------------------------------------------
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    st.error("❌ GOOGLE_API_KEY not found in .env file")
    st.stop()
st.success("✅ Google Gemini connected successfully!")

# ------------------------------------------------
# MAIN INTERFACE
# ------------------------------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📋 Your Daily Tasks")
    template = st.selectbox(
        "Load a sample template (or enter your own below)",
        ["", "Work Day", "Student Day", "Busy Professional", "Custom"]
    )

    templates = {
        "Work Day": """9:00 - Team meeting
10:30 - Project work
1:30 - Client calls
3:00 - Report writing""",
        "Student Day": """10:00 - Class
2:00 - Study time
4:00 - Assignment work
7:00 - Group project""",
        "Busy Professional": """8:00 - Emails
9:30 - Meeting
11:00 - Deep work
2:00 - Client work
4:00 - Planning"""
    }

    default_text = templates.get(template, "")
    user_data = st.text_area(
        "Enter your tasks with times",
        value=default_text,
        height=200
    )

with col2:
    st.subheader("🎯 Learning Goals (FREE)")
    enable_study = st.checkbox("Add study plan", value=True)
    if enable_study:
        study_goal = st.text_input("What to learn?")
        study_duration = st.selectbox(
            "Goal duration",
            ["1 month", "2 months", "3 months", "6 months"],
            index=2
        )
        weekly_hours = st.slider("Hours/week for study", 1, 10, 5)
    else:
        study_goal = None
        study_duration = None
        weekly_hours = 0

# ------------------------------------------------
# OPTIMIZE BUTTON
# ------------------------------------------------
if st.button("🚀 Generate FREE Optimized Schedule", use_container_width=True):
    if not user_data:
        st.warning("⚠️ Please enter your tasks!")
        st.stop()

    with st.spinner("🤖 Google Gemini is optimizing your schedule..."):
        try:
            if enable_study and study_goal:
                full_input = f"""
CURRENT SCHEDULE:
{user_data}

LEARNING GOAL:
Study: {study_goal}
Duration: {study_duration}
Available: {weekly_hours} hours/week
"""
            else:
                full_input = user_data

            # -----------------------------------------
            # GENERATE SCHEDULE
            # -----------------------------------------
            crew_instance = WorkflowCrew(
                full_input,
                study_goal if enable_study else None,
                study_duration if enable_study else None
            )

            result = crew_instance.build().kickoff()

            # Extract human-readable text
            try:
                if hasattr(result, 'raw'):
                    raw_output = result.raw
                else:
                    raw_output = str(result)
                data = json.loads(raw_output)
                schedule_text = data.get("study_plan", raw_output)
            except:
                schedule_text = raw_output

            # Display schedule in a card
            st.markdown(f"""
            <div style="padding:15px; border-radius:10px; background-color:#f0f2f6;">
            <h3>📋 Your Optimized Schedule</h3>
            <pre style="white-space:pre-wrap;">{schedule_text}</pre>
            </div>
            """, unsafe_allow_html=True)

            # Download button
            st.download_button(
                label="📥 Download Schedule",
                data=schedule_text,
                file_name="optimized_schedule.txt"
            )

            # -----------------------------------------
            # EMAIL SENDING + REMINDERS
            # -----------------------------------------
            email_service = EmailService()
            user_email = st.session_state.user.email

            # Send full schedule immediately
            email_service.send_schedule_email(user_email, schedule_text)

            # Schedule reminders for tasks
            email_service.schedule_task_reminders(user_email, schedule_text)

            st.success("📧 Schedule sent and reminders scheduled successfully!")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# ------------------------------------------------
# JOB LISTINGS IN RIGHT SIDEBAR
# ------------------------------------------------
if enable_study and study_goal:
    st.sidebar.markdown(f"### 💼 Jobs for {study_goal}")
    jobs = fetch_remoteok_jobs(study_goal)

    for job in jobs:
        with st.sidebar.container():
            st.markdown(f"**{job['title']}**")
            st.write(f"🏢 {job['company']}")
            st.write(f"🌍 Mode: {job['mode']}")
            st.markdown(f"[🚀 Apply Here]({job['apply_link']})")
            st.markdown("---")

