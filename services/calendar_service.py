import os
import pickle
import datetime
import json
import streamlit as st
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import traceback

# If modifying these scopes, delete the token.pickle file
SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleCalendarService:
    def __init__(self):
        self.creds = None
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate and get Google Calendar service using Streamlit secrets"""
        try:
            # Try to authenticate using service account from secrets
            if self._authenticate_with_service_account():
                return True
            
            # Fallback to OAuth if service account fails (for development)
            if self._authenticate_with_oauth():
                return True
            
            st.error("❌ Failed to authenticate with Google Calendar")
            return False
            
        except Exception as e:
            st.error(f"❌ Authentication error: {str(e)}")
            return False
    
    def _authenticate_with_service_account(self):
        """Authenticate using service account from Streamlit secrets"""
        try:
            # Check if credentials exist in secrets
            if "google_credentials" in st.secrets:
                # Load credentials from st.secrets
                credentials_info = dict(st.secrets["google_credentials"])
                
                # Create credentials object
                self.creds = service_account.Credentials.from_service_account_info(
                    credentials_info,
                    scopes=SCOPES
                )
                
                # Build the service
                self.service = build('calendar', 'v3', credentials=self.creds)
                return True
            else:
                return False
                
        except Exception as e:
            st.warning(f"Service account authentication failed: {str(e)}")
            return False
    
    def _authenticate_with_oauth(self):
        """Fallback authentication using OAuth (for local development)"""
        try:
            # Check if credentials.json exists locally
            if not os.path.exists('credentials.json'):
                return False
            
            # Token file to store user's access and refresh tokens
            token_file = f'token_{st.session_state.user.email}.pickle' if st.session_state.get('user') else 'token.pickle'
            
            if os.path.exists(token_file):
                with open(token_file, 'rb') as token:
                    self.creds = pickle.load(token)
            
            # If there are no (valid) credentials available, let the user log in
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    # Create flow using credentials.json
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                    
                    # Run local server
                    self.creds = flow.run_local_server(
                        port=0,
                        open_browser=True,
                        success_message="Authentication successful! You can close this window."
                    )
                
                # Save the credentials for the next run
                with open(token_file, 'wb') as token:
                    pickle.dump(self.creds, token)
            
            # Build the service
            self.service = build('calendar', 'v3', credentials=self.creds)
            return True
            
        except Exception as e:
            return False
    
    def fetch_tasks_from_calendar(self, days_ahead=7):
        """
        Fetch events/tasks from Google Calendar for the next X days
        """
        try:
            if not self.service:
                if not self.authenticate():
                    return []
            
            # Get the current time and time range
            now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            end_time = (datetime.datetime.utcnow() + 
                       datetime.timedelta(days=days_ahead)).isoformat() + 'Z'
            
            # Fetch events from primary calendar
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                timeMax=end_time,
                singleEvents=True,
                orderBy='startTime',
                maxResults=50  # Limit to 50 events
            ).execute()
            
            events = events_result.get('items', [])
            
            if not events:
                return []
            
            # Convert events to task format
            tasks = []
            for event in events:
                # Get start time
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                # Format time for display
                if 'T' in start:  # DateTime
                    start_time = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
                    time_str = start_time.strftime('%I:%M %p')
                    date_str = start_time.strftime('%Y-%m-%d')
                else:  # All day event
                    time_str = "All day"
                    date_str = start
                
                tasks.append({
                    'id': event['id'],
                    'title': event['summary'],
                    'description': event.get('description', ''),
                    'date': date_str,
                    'time': time_str,
                    'duration': self._calculate_duration(start, end),
                    'location': event.get('location', ''),
                    'attendees': len(event.get('attendees', [])),
                    'raw_event': event
                })
            
            return tasks
            
        except HttpError as error:
            st.error(f"An error occurred: {error}")
            return []
        except Exception as e:
            st.error(f"Error fetching tasks: {str(e)}")
            return []
    
    def _calculate_duration(self, start, end):
        """Calculate duration between start and end times"""
        try:
            if 'T' not in start or 'T' not in end:
                return 24  # All day event
            
            start_dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
            end_dt = datetime.datetime.fromisoformat(end.replace('Z', '+00:00'))
            
            duration = (end_dt - start_dt).total_seconds() / 3600
            return round(duration, 1)
        except:
            return 1  # Default to 1 hour
    
    def add_schedule_to_calendar(self, schedule_text):
        """
        Add optimized schedule to Google Calendar
        """
        try:
            if not self.service:
                if not self.authenticate():
                    return False, 0
            
            # Parse schedule and create events
            events_created = 0
            current_date = datetime.datetime.now().date()
            
            # Parse the schedule text to extract events
            lines = schedule_text.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                
                # Detect sections
                if 'MORNING' in line.upper():
                    current_section = 'morning'
                elif 'AFTERNOON' in line.upper():
                    current_section = 'afternoon'
                elif 'EVENING' in line.upper():
                    current_section = 'evening'
                
                # Parse tasks with time (format: • [Time] - [Activity])
                if line.startswith('•') and ' - ' in line:
                    parts = line.replace('•', '').strip().split(' - ', 1)
                    if len(parts) == 2:
                        time_str = parts[0].strip()
                        activity = parts[1].strip()
                        
                        # Create event in calendar
                        event_time = self._parse_time(time_str, current_section)
                        if event_time:
                            event = {
                                'summary': activity[:100],  # Truncate long titles
                                'description': f'From AI Optimized Schedule\n\n{activity}',
                                'start': {
                                    'dateTime': event_time['start'].isoformat(),
                                    'timeZone': 'UTC',
                                },
                                'end': {
                                    'dateTime': event_time['end'].isoformat(),
                                    'timeZone': 'UTC',
                                },
                                'reminders': {
                                    'useDefault': True,
                                },
                                'colorId': '2',  # Green color for AI-scheduled events
                            }
                            
                            created_event = self.service.events().insert(
                                calendarId='primary', 
                                body=event
                            ).execute()
                            
                            events_created += 1
            
            return True, events_created
            
        except Exception as e:
            st.error(f"Error adding to calendar: {str(e)}")
            return False, 0
    
    def _parse_time(self, time_str, section):
        """Parse time string and return datetime objects"""
        try:
            now = datetime.datetime.now()
            
            # Clean time string - remove bullets and extra spaces
            time_str = time_str.replace('•', '').strip()
            
            # Extract time part (handle formats like "9:00 AM" or "14:30")
            import re
            time_pattern = r'(\d{1,2}:\d{2}\s*(?:AM|PM)?)'
            time_match = re.search(time_pattern, time_str, re.IGNORECASE)
            
            if time_match:
                time_part = time_match.group(1)
                
                # Parse the time
                if 'AM' in time_part.upper() or 'PM' in time_part.upper():
                    # 12-hour format
                    time_obj = datetime.datetime.strptime(time_part, '%I:%M %p')
                    hour = time_obj.hour
                    minute = time_obj.minute
                else:
                    # 24-hour format
                    time_obj = datetime.datetime.strptime(time_part, '%H:%M')
                    hour = time_obj.hour
                    minute = time_obj.minute
                
                # Set start time (use today's date)
                start_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                # If the time has already passed today, schedule for tomorrow
                if start_time < now:
                    start_time = start_time + datetime.timedelta(days=1)
                
                # Default duration based on section
                if section == 'morning':
                    duration = 1  # 1 hour for morning tasks
                elif section == 'afternoon':
                    duration = 1.5  # 1.5 hours for afternoon tasks
                else:  # evening
                    duration = 2  # 2 hours for evening tasks
                
                end_time = start_time + datetime.timedelta(hours=duration)
                
                return {'start': start_time, 'end': end_time}
            
            return None
            
        except Exception as e:
            print(f"Error parsing time {time_str}: {e}")
            return None
    
    def create_study_reminders(self, study_goal, duration):
        """Create study session reminders in calendar"""
        try:
            if not self.service:
                if not self.authenticate():
                    return False
            
            # Create recurring study events
            start_date = datetime.datetime.now()
            
            # Parse duration
            if 'month' in duration:
                months = int(duration.split()[0])
                end_date = start_date + datetime.timedelta(days=30 * months)
            else:
                end_date = start_date + datetime.timedelta(days=30)  # Default 1 month
            
            # Weekly study sessions (Monday, Wednesday, Friday)
            study_days = [0, 2, 4]  # Monday, Wednesday, Friday
            events_created = 0
            
            current_date = start_date
            while current_date <= end_date:
                if current_date.weekday() in study_days:
                    # Morning study session (1 hour)
                    study_time = current_date.replace(hour=9, minute=0, second=0, microsecond=0)
                    
                    # Only create if it's in the future
                    if study_time > datetime.datetime.now():
                        event = {
                            'summary': f'📚 Study: {study_goal}',
                            'description': f'Regular study session for {study_goal}\n\nPart of your AI-optimized learning plan',
                            'start': {
                                'dateTime': study_time.isoformat(),
                                'timeZone': 'UTC',
                            },
                            'end': {
                                'dateTime': (study_time + datetime.timedelta(hours=1)).isoformat(),
                                'timeZone': 'UTC',
                            },
                            'reminders': {
                                'useDefault': False,
                                'overrides': [
                                    {'method': 'email', 'minutes': 60},
                                    {'method': 'popup', 'minutes': 15},
                                ],
                            },
                            'colorId': '5',  # Yellow for study events
                        }
                        
                        self.service.events().insert(calendarId='primary', body=event).execute()
                        events_created += 1
                
                current_date += datetime.timedelta(days=1)
            
            if events_created > 0:
                st.success(f"✅ Created {events_created} study sessions in your calendar!")
            return True
            
        except Exception as e:
            st.error(f"Error creating study reminders: {str(e)}")
            return False
    
    def clear_ai_generated_events(self):
        """Clear previously AI-generated events from calendar"""
        try:
            if not self.service:
                if not self.authenticate():
                    return 0
            
            # Get events from today onwards
            now = datetime.datetime.utcnow().isoformat() + 'Z'
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Delete events that were created by AI (identified by color or description)
            deleted_count = 0
            for event in events:
                # Check if this is an AI-generated event
                description = event.get('description', '')
                color_id = event.get('colorId', '')
                
                if color_id in ['2', '5'] or 'AI Optimized' in description:
                    self.service.events().delete(calendarId='primary', eventId=event['id']).execute()
                    deleted_count += 1
            
            return deleted_count
            
        except Exception as e:
            st.error(f"Error clearing calendar: {str(e)}")
            return 0
