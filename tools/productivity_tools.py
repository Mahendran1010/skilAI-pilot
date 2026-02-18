from crewai.tools import BaseTool
import re
from datetime import datetime, timedelta

class TimeUsageCalculator(BaseTool):
    name: str = "TimeUsageCalculator"
    description: str = "Calculates total time used in a schedule (FREE tool)"

    def _run(self, task_log: str) -> str:
        try:
            # Find hours
            hours = re.findall(r'(\d+\.?\d*)h', task_log.lower())
            total = sum(float(h) for h in hours)
            
            # Find minutes
            minutes = re.findall(r'(\d+\.?\d*)m', task_log.lower())
            total += sum(float(m) / 60 for m in minutes)
            
            return f"Total time identified: {total:.1f} hours. (Calculated using FREE tool)"
        except Exception as e:
            return f"Error calculating time: {str(e)}"

class AutomationPotentialSearch(BaseTool):
    name: str = "AutomationPotentialSearch"
    description: str = "Suggests ways to automate tasks using FREE tools only"

    def _run(self, task_type: str) -> str:
        # Only FREE tools and services
        free_suggestions = {
            "email": "📧 Use FREE tools: Gmail filters, Thunderbird, or Mailspring for email management",
            "data entry": "📊 Use FREE tools: Google Forms, Airtable (free tier), or LibreOffice Calc",
            "scheduling": "📅 Use FREE tools: Google Calendar, Calendly (free tier), or Doodle",
            "meetings": "🎥 Use FREE tools: Google Meet, Jitsi, or Zoom (free 40-min limit)",
            "coding": "💻 Use FREE tools: VS Code, GitHub Copilot (free for students), or CodePen",
            "research": "🔍 Use FREE tools: Google Scholar, Connected Papers, or Zotero",
            "documentation": "📝 Use FREE tools: Google Docs, Notion (free tier), or Obsidian",
            "task management": "✅ Use FREE tools: Trello, Asana (free tier), or Todoist (free tier)",
            "note taking": "📓 Use FREE tools: Google Keep, OneNote, or Standard Notes",
            "file storage": "☁️ Use FREE tools: Google Drive (15GB), OneDrive (5GB), or Dropbox (2GB)"
        }
        
        suggestion = free_suggestions.get(
            task_type.lower(),
            f"🔍 Search for FREE tools for {task_type} at: alternativeto.net or producthunt.com"
        )
        
        return f"[FREE SOLUTION] {suggestion}"

class StudyPlanGenerator(BaseTool):
    name: str = "StudyPlanGenerator"
    description: str = "Creates study plans using FREE learning resources"

    def _run(self, study_goal: str, duration: str, available_hours: int) -> str:
        """Generate study plan with FREE resources"""
        
        # FREE learning resources by category
        free_resources = {
            "python": "🐍 FREE: Python.org, Google's Python Class, freeCodeCamp, Codecademy (free tier)",
            "machine learning": "🤖 FREE: fast.ai, Google's ML Crash Course, Kaggle Learn, Coursera (audit)",
            "web development": "🌐 FREE: MDN Web Docs, The Odin Project, freeCodeCamp, W3Schools",
            "data science": "📊 FREE: Kaggle Learn, Google Data Analytics, IBM Data Science (audit)",
            "javascript": "📜 FREE: JavaScript.info, Eloquent JavaScript (online), freeCodeCamp",
            "spanish": "🇪🇸 FREE: Duolingo, SpanishDict, Language Transfer, Tandem",
            "french": "🇫🇷 FREE: Duolingo, Lawless French, TV5MONDE, Coffee Break French",
            "german": "🇩🇪 FREE: Duolingo, Deutsche Welle, Goethe Institut (free resources)",
            "excel": "📈 FREE: Excel Easy, GCFGlobal, Microsoft's Excel Training, YouTube tutorials"
        }
        
        # Find matching resource or provide general suggestion
        resource = "📚 FREE: YouTube tutorials, Coursera (audit), edX (audit), MIT OpenCourseWare"
        for key in free_resources:
            if key in study_goal.lower():
                resource = free_resources[key]
                break
        
        # Parse duration
        try:
            duration_num = int(duration.split()[0]) if duration else 3
        except:
            duration_num = 3
        
        weekly_hours = available_hours or 5
        
        plan = f"""
        📚 FREE STUDY PLAN: {study_goal}
        Duration: {duration} | Weekly commitment: {weekly_hours} hours
        
        📅 WEEKLY SCHEDULE (using FREE resources):
        
        Monday-Friday:
        • Morning (20 min): Quick review using flashcards or apps
        • Lunch (15 min): Watch tutorial videos
        • Evening (30-45 min): Deep practice with exercises
        
        Weekend:
        • 2-hour block for projects and review
        
        🎯 LEARNING RESOURCES (100% FREE):
        {resource}
        
        📱 FREE APPS TO USE:
        • Anki (flashcards) - Completely free
        • Notion (notes) - Free tier
        • Google Keep (quick notes) - Free
        • YouTube (tutorials) - Free
        
        💡 PROGRESS TRACKING (FREE):
        • Google Sheets for tracking hours
        • GitHub for code projects (free)
        • Portfolio using GitHub Pages (free)
        
        Remember: All resources suggested are COMPLETELY FREE!
        """
        
        return plan

class NotificationScheduler(BaseTool):
    name: str = "NotificationScheduler"
    description: str = "Schedules notifications using FREE tools"

    def _run(self, task_name: str, task_time: str) -> str:
        """Schedule notifications using FREE tools"""
        
        return f"""
        🔔 FREE NOTIFICATION OPTIONS FOR: {task_name} at {task_time}
        
        📱 Using FREE tools:
        
        1. Google Calendar (FREE):
           • Create event: {task_name}
           • Set reminder: {task_time}
           • Get notifications via email/popup
        
        2. Task Apps (FREE tiers):
           • Todoist: Set recurring reminders
           • Microsoft To Do: Task reminders
           • Google Tasks: Integrated with Calendar
        
        3. Browser Extensions (FREE):
           • Reminder Fox
           • Simple Reminder
           • Alarm Clock for Chrome
        
        To set up: Just add to your Google Calendar with a reminder!
        """