from dotenv import load_dotenv
load_dotenv()

import os
import streamlit as st

# Minimal dummy values (never used)
os.environ["OPENAI_API_KEY"] = ""
os.environ["OPENAI_MODEL_NAME"] = "gpt-3.5-turbo"

from crew import WorkflowCrew

st.set_page_config(
    page_title="SKILLPILOT  AI", 
    page_icon="🚀",
    layout="wide"
)

# Custom CSS
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

# Header
st.markdown('<div class="free-badge">✨ 100% FREE - Powered by Google Gemini ✨</div>', unsafe_allow_html=True)
st.title("🤖 AI Workflow Optimizer")
st.markdown("**No payment required - Just your Google account!**")

# Check Google API key
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    st.error("❌ GOOGLE_API_KEY not found in .env file")
    
    with st.expander("📝 Get your FREE Google API Key (2 minutes)"):
        st.markdown("""
        ### Step-by-Step Guide:
        
        1. **Go to** [Google AI Studio](https://makersuite.google.com/app/apikey)
        2. **Sign in** with your Google account
        3. **Click** "Create API Key" button
        4. **Copy** the generated key (starts with "AIza...")
        5. **Add it to your `.env` file**:
        ```
        GOOGLE_API_KEY=AIzaSyBxxxxxxxxxxxxxx
        ```
        
        🎉 **That's it! No credit card required!**
        """)
    st.stop()

# Show API key status
st.success(f"✅ Google Gemini connected successfully!")

# Main interface
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📋 Your Daily Tasks")
    
    # Sample templates
    template = st.selectbox(
        "Load a sample template (or enter your own below)",
        ["", "Work Day", "Student Day", "Busy Professional", "Custom"]
    )
    
    templates = {
        "Work Day": """9:00 AM - 10:30 AM: Team meeting
10:30 AM - 12:30 PM: Project work
1:30 PM - 3:00 PM: Client calls
3:00 PM - 5:00 PM: Report writing""",
        "Student Day": """10:00 AM - 12:00 PM: Class
2:00 PM - 4:00 PM: Study time
4:00 PM - 6:00 PM: Assignment work
7:00 PM - 9:00 PM: Group project""",
        "Busy Professional": """8:00 AM - 9:00 AM: Emails
9:30 AM - 11:00 AM: Meeting
11:00 AM - 1:00 PM: Deep work
2:00 PM - 4:00 PM: Client work
4:00 PM - 6:00 PM: Planning"""
    }
    
    if template in templates:
        default_text = templates[template]
    else:
        default_text = ""
    
    user_data = st.text_area(
        "Enter your tasks with times",
        value=default_text,
        height=200,
        placeholder="Format: [Time] - [Task]\nExample:\n9:00 AM - Emails\n11:00 AM - Meeting\n2:00 PM - Project work"
    )

with col2:
    st.subheader("🎯 Learning Goals (FREE)")
    st.markdown("*All resources suggested will be FREE*")
    
    enable_study = st.checkbox("Add study plan", value=True)
    
    if enable_study:
        study_goal = st.text_input(
            "What to learn?",
            placeholder="e.g., Python, Spanish, Data Science"
        )
        
        study_duration = st.selectbox(
            "Goal duration",
            ["1 month", "2 months", "3 months", "6 months"],
            index=2
        )
        
        weekly_hours = st.slider(
            "Hours/week for study",
            min_value=1,
            max_value=10,
            value=5,
            help="How many hours can you dedicate weekly?"
        )
        
        st.info("💡 All study resources will be FREE - YouTube, freeCodeCamp, Duolingo, etc.")
    else:
        study_goal = None
        study_duration = None
        weekly_hours = 0

# FREE tools info
with st.expander("🔧 FREE Tools That Will Be Suggested"):
    st.markdown("""
    - **📧 Email**: Gmail filters, Thunderbird
    - **📅 Scheduling**: Google Calendar, Calendly free
    - **📝 Notes**: Google Keep, Notion free
    - **🎥 Meetings**: Google Meet, Jitsi
    - **💻 Coding**: VS Code, GitHub free
    - **📊 Data**: Google Sheets, Airtable free
    - **🗣️ Language**: Duolingo, Language Transfer
    """)

# Optimize button
if st.button("🚀 Generate FREE Optimized Schedule", use_container_width=True):
    if user_data:
        with st.spinner("🤖 Google Gemini is optimizing your schedule for FREE..."):
            try:
                # Progress tracking
                progress_bar = st.progress(0)
                status = st.empty()
                
                status.text("Initializing FREE AI agent...")
                progress_bar.progress(25)
                
                # Prepare input
                if enable_study and study_goal:
                    full_input = f"""
                    CURRENT SCHEDULE:
                    {user_data}
                    
                    LEARNING GOAL (use FREE resources only):
                    Study: {study_goal}
                    Duration: {study_duration}
                    Available: {weekly_hours} hours/week
                    
                    IMPORTANT: Only suggest FREE tools and resources!
                    """
                else:
                    full_input = user_data + "\n\nIMPORTANT: Only suggest FREE tools!"
                
                status.text("Analyzing schedule with Google Gemini...")
                progress_bar.progress(50)
                
                # Run crew
                crew_instance = WorkflowCrew(
                    full_input,
                    study_goal if enable_study else None,
                    study_duration if enable_study else None
                )
                
                result = crew_instance.build().kickoff()
                
                progress_bar.progress(100)
                status.text("✅ Done!")
                
                # Display results
                st.success("✅ Your FREE optimized schedule is ready!")
                
                st.markdown("### 📋 Your Optimized Schedule")
                
                # Show result
                if hasattr(result, 'raw'):
                    st.markdown(result.raw)
                else:
                    st.markdown(str(result))
                
                # Download
                st.download_button(
                    label="📥 Download Schedule (FREE)",
                    data=str(result),
                    file_name="free_optimized_schedule.txt"
                )
                
                # Cost summary
                st.info("💰 **Cost: $0.00** - Generated with Google Gemini FREE tier!")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("This is a FREE service. If you see quota errors, wait a minute and try again.")
    else:
        st.warning("⚠️ Please enter your tasks!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>🚀 <b>100% FREE</b> - Powered by Google Gemini | No OpenAI costs | No credit card needed</p>
    <p style='font-size: 12px; color: gray'>All suggestions use only free tools and resources</p>
</div>
""", unsafe_allow_html=True)