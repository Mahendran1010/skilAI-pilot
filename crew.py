import os
from dotenv import load_dotenv
load_dotenv()

from crewai import Process, Agent, Task, Crew
from tools.productivity_tools import (
    TimeUsageCalculator,
    AutomationPotentialSearch,
    StudyPlanGenerator,
    NotificationScheduler
)
from langchain_google_genai import ChatGoogleGenerativeAI

# Initialize Google Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
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

        planner = Agent(
            role="Workflow Planner",
            goal="Convert raw tasks into an optimized daily schedule with integrated study time",
            backstory="""You are an expert productivity strategist specializing in time management 
            and learning optimization. You ONLY use Google Gemini.""",
            llm=llm,
            tools=[time_tool, automation_tool, study_tool, notification_tool],
            allow_delegation=False,
            verbose=True,
            max_rpm=15,
            memory=True
        )

        study_context = ""
        if self.study_goal and self.study_duration:
            study_context = f"""
            ADDITIONAL LEARNING GOAL:
            - Goal: {self.study_goal}
            - Duration: {self.study_duration}

            IMPORTANT: Integrate this study goal intelligently.
            """

        task = Task(
            description=f"""
            USER'S CURRENT TASKS:
            {self.user_input}

            {study_context}

            CRITICAL INSTRUCTIONS:
            1. Analyze the schedule and find free time slots
            2. If study goal exists, add study sessions
            3. Suggest automation using free tools only
            4. Create a balanced schedule with breaks

            FORMAT YOUR RESPONSE EXACTLY AS:

            📅 OPTIMIZED DAILY SCHEDULE
            ============================

            🌅 MORNING (6:00 AM - 12:00 PM)
            • [Time] - [Activity]

            ☀️ AFTERNOON (12:00 PM - 5:00 PM)
            • [Time] - [Activity]

            🌙 EVENING (5:00 PM - 10:00 PM)
            • [Time] - [Activity]

            💡 FREE PRODUCTIVITY TIPS:
            • Tip 1
            • Tip 2

            ⏰ TOTAL FOCUS TIME: X hours
            📚 STUDY TIME: X hours (if applicable)
            """,
            expected_output="Optimized daily schedule",
            agent=planner
        )

        crew = Crew(
            agents=[planner],
            tasks=[task],
            process=Process.sequential,
            verbose=True,
            manager_llm=llm
        )

        return crew
