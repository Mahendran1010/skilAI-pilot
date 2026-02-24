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
from services.calendar_service import GoogleCalendarService

st.set_page_config(
    page_title="FREE AI Workflow Optimizer",
    page_icon="🚀",
    layout="wide"
)

#--------------------------------------------------------------------------
# SESSION STATE INIT
#--------------------------------------------------------------------------
if "user" not in st.session_state:
    st.session_state.user = None
if "calendar_connected" not in st.session_state:
    st.session_state.calendar_connected = False
if "calendar_tasks" not in st.session_state:
    st.session_state.calendar_tasks = []
if "calendar_service" not in st.session_state:
    st.session_state.calendar_service = None
if "generated_schedule" not in st.session_state:
    st.session_state.generated_schedule = None
if "schedule_generated" not in st.session_state:
    st.session_state.schedule_generated = False
if "calendar_action_triggered" not in st.session_state:
    st.session_state.calendar_action_triggered = False
if "calendar_action_result" not in st.session_state:
    st.session_state.calendar_action_result = None

#--------------------------------------------------------------------------
# LOGIN / SIGNUP SCREEN
#--------------------------------------------------------------------------
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

#--------------------------------------------------------------------------
# AFTER LOGIN → YOUR ORIGINAL UI STARTS
#--------------------------------------------------------------------------
user = st.session_state.user
st.sidebar.success(f"Logged in as {user.email}")

if st.sidebar.button("Logout"):
    st.session_state.user = None
    st.session_state.calendar_connected = False
    st.session_state.calendar_tasks = []
    st.session_state.calendar_service = None
    st.session_state.generated_schedule = None
    st.session_state.schedule_generated = False
    st.rerun()

#--------------------------------------------------------------------------
# GOOGLE CALENDAR SIDEBAR SECTION
#--------------------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### 📅 Google Calendar")

if not st.session_state.calendar_connected:
    if st.sidebar.button("🔗 Connect Google Calendar", key="connect_calendar"):
        with st.spinner("Connecting to Google Calendar..."):
            try:
                calendar_service = GoogleCalendarService()
                if calendar_service and calendar_service.service:
                    st.session_state.calendar_connected = True
                    st.session_state.calendar_service = calendar_service
                    st.sidebar.success("✅ Calendar connected!")
                    st.rerun()
                else:
                    st.sidebar.error("❌ Failed to connect calendar. Check credentials.json")
            except Exception as e:
                st.sidebar.error(f"❌ Connection error: {str(e)}")
else:
    st.sidebar.success("✅ Calendar Connected")
    
    # Fetch tasks button
    if st.sidebar.button("📥 Fetch Calendar Tasks", key="fetch_tasks"):
        with st.spinner("Fetching your calendar events..."):
            try:
                tasks = st.session_state.calendar_service.fetch_tasks_from_calendar(days_ahead=7)
                if tasks:
                    st.session_state.calendar_tasks = tasks
                    st.sidebar.success(f"✅ Found {len(tasks)} events!")
                else:
                    st.sidebar.info("No upcoming events found")
            except Exception as e:
                st.sidebar.error(f"❌ Error fetching tasks: {str(e)}")
    
    # Clear AI events button
    if st.sidebar.button("🗑️ Clear AI Events", key="clear_ai"):
        with st.spinner("Clearing AI-generated events..."):
            try:
                deleted = st.session_state.calendar_service.clear_ai_generated_events()
                st.sidebar.success(f"✅ Deleted {deleted} AI events")
            except Exception as e:
                st.sidebar.error(f"❌ Error clearing events: {str(e)}")
    
    # Disconnect button
    if st.sidebar.button("🔌 Disconnect Calendar", key="disconnect"):
        st.session_state.calendar_connected = False
        st.session_state.calendar_tasks = []
        st.session_state.calendar_service = None
        st.rerun()

#--------------------------------------------------------------------------
# CUSTOM CSS
#--------------------------------------------------------------------------
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
    .calendar-task {
        padding: 8px;
        margin: 5px 0;
        background-color: #e8f0fe;
        border-radius: 5px;
        border-left: 3px solid #4285F4;
    }
    div[data-testid="stButton"] button {
        transition: all 0.3s ease;
    }
    div[data-testid="stButton"] button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    </style>
""", unsafe_allow_html=True)

#--------------------------------------------------------------------------
# HEADER
#--------------------------------------------------------------------------
st.markdown('<div class="free-badge">✨ 100% FREE - Powered by Google Gemini ✨</div>', unsafe_allow_html=True)
st.title("🤖 AI Workflow Optimizer SkillPilot AI")
st.markdown("**No payment required - Just your Google account!**")

#--------------------------------------------------------------------------
# CHECK GOOGLE API KEY
#--------------------------------------------------------------------------
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    st.error("❌ GOOGLE_API_KEY not found in .env file")
    st.stop()

st.success("✅ Google Gemini connected successfully!")

#--------------------------------------------------------------------------
# MAIN INTERFACE
#--------------------------------------------------------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📋 Your Daily Tasks")
    
    # Option to use calendar tasks or manual input
    use_calendar = st.checkbox("Use tasks from Google Calendar", 
                               value=len(st.session_state.calendar_tasks) > 0,
                               disabled=not st.session_state.calendar_connected,
                               key="use_calendar_checkbox")
    
    if use_calendar and st.session_state.calendar_tasks:
        # Display and select calendar tasks
        st.markdown("**Select tasks to include:**")
        
        selected_tasks = []
        calendar_task_text = "TASKS FROM CALENDAR:\n"
        
        for i, task in enumerate(st.session_state.calendar_tasks[:10]):  # Show first 10
            task_desc = f"{task['title']} - {task['date']} at {task['time']} ({task['duration']}h)"
            col_a, col_b = st.columns([0.1, 0.9])
            with col_a:
                selected = st.checkbox("", key=f"task_{task['id']}_{i}", value=True, label_visibility="collapsed")
            with col_b:
                st.markdown(f"<div class='calendar-task'>{task_desc}</div>", unsafe_allow_html=True)
            
            if selected:
                selected_tasks.append(task)
                calendar_task_text += f"• {task['title']} at {task['time']} on {task['date']} ({task['duration']} hours)\n"
        
        if selected_tasks:
            # Combine with manual input if any
            manual_tasks = st.text_area("Additional tasks (optional):", height=100, 
                                       placeholder="Add any tasks not in your calendar...",
                                       key="manual_tasks_input")
            
            if manual_tasks:
                user_data = calendar_task_text + "\nADDITIONAL TASKS:\n" + manual_tasks
            else:
                user_data = calendar_task_text
            
            st.info(f"📊 Selected {len(selected_tasks)} tasks from calendar")
        else:
            user_data = ""
            st.warning("⚠️ Please select at least one task to continue")
    
    else:
        # Original task input
        template = st.selectbox(
            "Load a sample template (or enter your own below)",
            ["", "Work Day", "Student Day", "Busy Professional", "Custom"],
            key="template_select"
        )
        
        templates = {
            "Work Day": """9:00 AM - Team meeting
10:30 AM - Project work
1:30 PM - Client calls
3:00 PM - Report writing""",
            "Student Day": """10:00 AM - Class
2:00 PM - Study time
4:00 PM - Assignment work
7:00 PM - Group project""",
            "Busy Professional": """8:00 AM - Emails
9:30 AM - Meeting
11:00 AM - Deep work
2:00 PM - Client work
4:00 PM - Planning"""
        }
        if template in templates:
             default_text = templates[template]
        else:
             default_text = ""
    
        user_data = st.text_area(
            "Enter your tasks with times",
            value=default_text,
            height=200,
            placeholder="Format: [Time] - [Task]\nExample:\n9:00 AM - Team meeting\n2:00 PM - Project work",
            key="tasks_input"
        )

with col2:
    st.subheader("🎯 Learning Goals (FREE)")
    enable_study = st.checkbox("Add study plan", value=True, key="enable_study")
    
    create_study_calendar = False  # Default value
    
    if enable_study:
        study_goal = st.text_input("What to learn?", placeholder="e.g., Python, Java, Data Science", key="study_goal")
        study_duration = st.selectbox(
            "Goal duration",
            ["1 month", "2 months", "3 months", "6 months"],
            index=2,
            key="study_duration"
        )
        weekly_hours = st.slider("Hours/week for study", 1, 10, 5, key="weekly_hours")
        
        # Add option to create calendar reminders for study
        if st.session_state.get('calendar_connected', False):
            create_study_calendar = st.checkbox("Add study sessions to Calendar", value=True, key="study_calendar")
        else:
            create_study_calendar = False
    else:
        study_goal = None
        study_duration = None
        weekly_hours = 0
        create_study_calendar = False

#--------------------------------------------------------------------------
# OPTIMIZE BUTTON
#--------------------------------------------------------------------------
if st.button("🚀 Generate FREE Optimized Schedule", use_container_width=True, key="generate_schedule"):
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
            
            # GENERATE SCHEDULE
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
                
                # Try to parse as JSON first
                try:
                    data = json.loads(raw_output)
                    schedule_text = data.get("study_plan", raw_output)
                except:
                    schedule_text = raw_output
            except:
                schedule_text = str(result)
            
            # Store in session state
            st.session_state.generated_schedule = schedule_text
            st.session_state.schedule_generated = True
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            import traceback
            with st.expander("See error details"):
                st.code(traceback.format_exc())

#--------------------------------------------------------------------------
# DISPLAY SCHEDULE IF GENERATED
#--------------------------------------------------------------------------
if st.session_state.schedule_generated and st.session_state.generated_schedule:
    schedule_text = st.session_state.generated_schedule
    
    # Display schedule in a card
   # Display schedule in a card with theme-aware colors (works for both light and dark mode)
    st.markdown(f"""
     <div style="
         padding:20px; 
         border-radius:10px; 
         background-color: transparent;
         border: 1px solid rgba(128, 128, 128, 0.3);
         margin-top: 20px;
     ">
         <h3 style="
             color: inherit; 
             margin-top:0; 
             margin-bottom:15px;
         ">📋 Your Optimized Schedule</h3>
         <pre style="
             white-space:pre-wrap; 
             font-family: monospace;
             color: inherit;
             background-color: transparent;
             border: none;
             padding: 10px;
             margin: 0;
             font-size: 14px;
         ">{schedule_text}</pre>
     </div>
     """, unsafe_allow_html=True)
         
         # Download button
    st.download_button(
        label="📥 Download Schedule",
        data=schedule_text,
        file_name="optimized_schedule.txt",
        mime="text/plain",
        key="download_schedule"
    )
    
    # Add to Calendar options
    if st.session_state.calendar_connected:
        st.markdown("---")
        st.subheader("📅 Calendar Options")
        col3, col4 = st.columns(2)
        
        with col3:
            add_to_calendar = st.button("📅 Add Schedule to Google Calendar", 
                                       use_container_width=True, 
                                       key="add_to_calendar")
            if add_to_calendar:
                with st.spinner("Adding to calendar..."):
                    try:
                        success, count = st.session_state.calendar_service.add_schedule_to_calendar(schedule_text)
                        if success:
                            st.success(f"✅ Added {count} events to your calendar!")
                        else:
                            st.error("❌ Failed to add events to calendar")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        
        with col4:
            if enable_study and study_goal and create_study_calendar:
                create_reminders = st.button("📚 Create Study Reminders", 
                                           use_container_width=True, 
                                           key="create_reminders")
                if create_reminders:
                    with st.spinner("Creating study reminders..."):
                        try:
                            success = st.session_state.calendar_service.create_study_reminders(study_goal, study_duration)
                            if success:
                                st.success("✅ Study reminders added to calendar!")
                            else:
                                st.error("❌ Failed to create study reminders")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
    
    # EMAIL SENDING + REMINDERS
    st.markdown("---")
    st.subheader("📧 Email Options")
    
    email_service = EmailService()
    user_email = st.session_state.user.email
    
    if st.button("📧 Send Schedule via Email", use_container_width=True, key="send_email"):
        with st.spinner("Sending email..."):
            try:
                if email_service.send_schedule_email(user_email, schedule_text):
                    st.success(f"✅ Schedule sent to {user_email}!")
                    
                    # Schedule reminders for tasks
                    email_service.schedule_task_reminders(user_email, schedule_text)
                    st.info("⏰ Task reminders scheduled!")
                else:
                    st.error("❌ Failed to send email. Check email configuration.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

#--------------------------------------------------------------------------
# JOB LISTINGS IN RIGHT SIDEBAR
#--------------------------------------------------------------------------
if enable_study and study_goal:
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"### 💼 Jobs for {study_goal}")
    
    with st.sidebar:
        with st.spinner("Fetching jobs..."):
            try:
                jobs = fetch_remoteok_jobs(study_goal)
                
                if jobs:
                    for job in jobs:
                        with st.container():
                            st.markdown(f"**{job['title']}**")
                            st.write(f"🏢 {job['company']}")
                            st.write(f"🌍 Mode: {job['mode']}")
                            st.markdown(f"[🚀 Apply Here]({job['apply_link']})")
                            st.markdown("---")
                else:
                    st.info("No jobs found at the moment")
            except Exception as e:
                st.error(f"Error fetching jobs: {str(e)}")

#--------------------------------------------------------------------------
# FOOTER
#--------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "🚀 Made with ❤️ using CrewAI and Google Gemini | 100% Free Forever"
    "</div>",
    unsafe_allow_html=True
)
