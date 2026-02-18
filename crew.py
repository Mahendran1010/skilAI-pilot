import os
from dotenv import load_dotenv
load_dotenv()

# Minimal dummy values that won't be used
os.environ["OPENAI_API_KEY"] = ""  # Just to initialize CrewAI
os.environ["OPENAI_MODEL_NAME"] = "gpt-3.5-turbo"  # Dummy value

from crewai import Process, Agent, Task, Crew
from tools.productivity_tools import TimeUsageCalculator, AutomationPotentialSearch, StudyPlanGenerator, NotificationScheduler
from langchain_google_genai import ChatGoogleGenerativeAI

# Initialize Google Gemini ONLY
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",  # Experimental but often works
    temperature=0.3,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    convert_system_message_to_human=True,
)

class WorkflowCrew:
    def __init__(self, user_input, study_goal=None, study_duration=None):
        self.user_input = user_input
        self.study_goal = study_goal
        self.study_duration = study_duration

    def build(self):
        # Initialize tools
        time_tool = TimeUsageCalculator()
        automation_tool = AutomationPotentialSearch()
        study_tool = StudyPlanGenerator()
        notification_tool = NotificationScheduler()

        # Planner Agent - Purely Google Gemini
        planner = Agent(
            role="Workflow Planner",
            goal="Convert raw tasks into an optimized daily schedule with integrated study time",
            backstory="""You are an expert productivity strategist specializing in time management 
            and learning optimization. You ONLY use Google Gemini and NEVER make OpenAI calls.""",
            llm=llm,  # Explicitly set to Google Gemini
            tools=[time_tool, automation_tool, study_tool, notification_tool],
            allow_delegation=False,
            verbose=True,
            max_rpm=15,  # Rate limit for free tier
            memory=True  # Enable memory for better context
        )

        # Create task description with clear instructions
        study_context = ""
        if self.study_goal and self.study_duration:
            study_context = f"""
            ADDITIONAL LEARNING GOAL:
            - Goal: {self.study_goal}
            - Duration: {self.study_duration}
            
            IMPORTANT: Integrate this study goal WITHOUT using any paid services.
            """

        task = Task(
            description=f"""
            You are a workflow optimization expert using Google Gemini (free).
            
            USER'S CURRENT TASKS:
            {self.user_input}
            
            {study_context}
            
            CRITICAL INSTRUCTIONS:
            1. Use ONLY Google Gemini - NO OpenAI calls
            2. Analyze the schedule and find free time slots
            3. If study goal exists, add study sessions to free slots
            4. Suggest automation using free tools only
            5. Create a balanced schedule with breaks
            
            FORMAT YOUR RESPONSE EXACTLY AS:
            
            📅 OPTIMIZED DAILY SCHEDULE
            ============================
            
            🌅 MORNING (6:00 AM - 12:00 PM)
            • [Time] - [Activity]
            • [Time] - [Activity]
            
            ☀️ AFTERNOON (12:00 PM - 5:00 PM)
            • [Time] - [Activity]
            • [Time] - [Activity]
            
            🌙 EVENING (5:00 PM - 10:00 PM)
            • [Time] - [Activity]
            • [Time] - [Activity]
            
            💡 FREE PRODUCTIVITY TIPS:
            • Tip 1 (using free tools)
            • Tip 2 (using free tools)
            
            ⏰ TOTAL FOCUS TIME: X hours
            📚 STUDY TIME: X hours (if applicable)
            
            Remember: All suggestions must use FREE tools and services only.
            """,
            expected_output="A detailed optimized daily schedule using only free tools and Google Gemini",
            agent=planner
        )

        # Crew with Google Gemini only
        crew = Crew(
            agents=[planner],
            tasks=[task],
            process=Process.sequential,
            verbose=True,
            manager_llm=llm,  # Use Gemini as manager
            output_log_file="gemini_crew_log.txt"  # Optional logging
        )

        return crew