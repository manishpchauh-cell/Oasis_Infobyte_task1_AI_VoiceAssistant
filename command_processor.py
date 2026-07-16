import webbrowser
from datetime import datetime
from weather_service import WeatherService
from reminder_service import ReminderService
from ai_service import AIService
from system_service import SystemService


class CommandProcessor:
    def __init__(self):
        self.weather_service = WeatherService()
        self.reminder_service = ReminderService()
        self.ai_service = AIService()
        self.system_service = SystemService()

    def extract_city_from_weather_command(self, command):
        command = command.lower().strip()

        weather_phrases = [
            "weather in",
            "what is the weather in",
            "tell me weather in",
            "tell me the weather in"
        ]

        for phrase in weather_phrases:
            if phrase in command:
                city = command.split(phrase, 1)[1].strip()
                return city.title()

        return None

    def is_reminder_command(self, command):
        command = command.lower().strip()
        return (
            command.startswith("remind me to ")
            or command.startswith("set reminder to ")
        )

    def process_command(self, command):
        original_command = command.strip()
        command = command.lower().strip()

        # -------------------------------
        # WEATHER COMMANDS
        # -------------------------------
        city = self.extract_city_from_weather_command(command)
        if city:
            weather_result = self.weather_service.get_weather(city)

            if weather_result["success"]:
                return {
                    "response": weather_result["response_text"],
                    "speak": weather_result["response_text"],
                    "action_done": True,
                    "weather_data": weather_result,
                    "refresh_reminders": False
                }
            else:
                return {
                    "response": weather_result["response_text"],
                    "speak": weather_result["response_text"],
                    "action_done": False,
                    "weather_data": None,
                    "refresh_reminders": False
                }

        elif command == "weather":
            return {
                "response": "Please say weather in city name. Example: weather in Ahmedabad.",
                "speak": "Please say weather in city name. Example: weather in Ahmedabad.",
                "action_done": False,
                "weather_data": None,
                "refresh_reminders": False
            }

        # -------------------------------
        # REMINDER COMMANDS
        # -------------------------------
        elif self.is_reminder_command(command):
            reminder_result = self.reminder_service.add_reminder_from_command(original_command)

            return {
                "response": reminder_result["response_text"],
                "speak": reminder_result["response_text"],
                "action_done": reminder_result["success"],
                "weather_data": None,
                "refresh_reminders": reminder_result["success"]
            }

        elif command == "show reminders" or command == "show reminder":
            return {
                "response": "Opening saved reminders list.",
                "speak": "Opening saved reminders list.",
                "action_done": True,
                "weather_data": None,
                "refresh_reminders": True
            }

        elif command.startswith("delete reminder "):
            reminder_id = command.replace("delete reminder ", "").strip()
            result = self.reminder_service.delete_reminder_by_id(reminder_id)

            return {
                "response": result["response_text"],
                "speak": result["response_text"],
                "action_done": result["success"],
                "weather_data": None,
                "refresh_reminders": True
            }

        elif command == "clear reminders" or command == "clear all reminders":
            result = self.reminder_service.clear_all_reminders()

            return {
                "response": result["response_text"],
                "speak": result["response_text"],
                "action_done": result["success"],
                "weather_data": None,
                "refresh_reminders": True
            }

        # -------------------------------
        # APP OPENING COMMANDS
        # -------------------------------
        elif command == "open notepad":
            result = self.system_service.open_notepad()
            return {
                "response": result["response_text"],
                "speak": result["response_text"],
                "action_done": result["success"],
                "weather_data": None,
                "refresh_reminders": False
            }

        elif command == "open calculator":
            result = self.system_service.open_calculator()
            return {
                "response": result["response_text"],
                "speak": result["response_text"],
                "action_done": result["success"],
                "weather_data": None,
                "refresh_reminders": False
            }

        elif command == "open chrome":
            result = self.system_service.open_chrome()
            return {
                "response": result["response_text"],
                "speak": result["response_text"],
                "action_done": result["success"],
                "weather_data": None,
                "refresh_reminders": False
            }

        elif command == "open vscode" or command == "open vs code":
            result = self.system_service.open_vscode()
            return {
                "response": result["response_text"],
                "speak": result["response_text"],
                "action_done": result["success"],
                "weather_data": None,
                "refresh_reminders": False
            }

        elif command == "open file explorer":
            result = self.system_service.open_file_explorer()
            return {
                "response": result["response_text"],
                "speak": result["response_text"],
                "action_done": result["success"],
                "weather_data": None,
                "refresh_reminders": False
            }

        # -------------------------------
        # SYSTEM CONTROL COMMANDS
        # -------------------------------
        elif command == "shutdown pc" or command == "shutdown computer":
            result = self.system_service.shutdown_pc()
            return {
                "response": result["response_text"],
                "speak": result["response_text"],
                "action_done": result["success"],
                "weather_data": None,
                "refresh_reminders": False
            }

        elif command == "restart pc" or command == "restart computer":
            result = self.system_service.restart_pc()
            return {
                "response": result["response_text"],
                "speak": result["response_text"],
                "action_done": result["success"],
                "weather_data": None,
                "refresh_reminders": False
            }

        elif command == "lock pc" or command == "lock computer":
            result = self.system_service.lock_pc()
            return {
                "response": result["response_text"],
                "speak": result["response_text"],
                "action_done": result["success"],
                "weather_data": None,
                "refresh_reminders": False
            }

        elif command == "take screenshot" or command == "capture screenshot":
            result = self.system_service.take_screenshot()
            return {
                "response": result["response_text"],
                "speak": result["response_text"],
                "action_done": result["success"],
                "weather_data": None,
                "refresh_reminders": False
            }

        # -------------------------------
        # Greetings / intro
        # -------------------------------
        elif "hello" in command or "hi" in command:
            return {
                "response": "Hello! I am Jarvis. How can I help you?",
                "speak": "Hello! I am Jarvis. How can I help you?",
                "action_done": True,
                "weather_data": None,
                "refresh_reminders": False
            }

        elif "how are you" in command:
            return {
                "response": "I am functioning perfectly and ready to help you.",
                "speak": "I am functioning perfectly and ready to help you.",
                "action_done": True,
                "weather_data": None,
                "refresh_reminders": False
            }

        elif "your name" in command or "who are you" in command:
            return {
                "response": "I am Jarvis, your AI voice assistant.",
                "speak": "I am Jarvis, your AI voice assistant.",
                "action_done": True,
                "weather_data": None,
                "refresh_reminders": False
            }

        elif "who made you" in command or "who created you" in command:
            return {
                "response": "I was created by my developer as an advanced AI voice assistant project.",
                "speak": "I was created by my developer as an advanced AI voice assistant project.",
                "action_done": True,
                "weather_data": None,
                "refresh_reminders": False
            }

        # -------------------------------
        # Time / date
        # -------------------------------
        elif "time" in command:
            current_time = datetime.now().strftime("%I:%M %p")
            return {
                "response": f"The current time is {current_time}.",
                "speak": f"The current time is {current_time}",
                "action_done": True,
                "weather_data": None,
                "refresh_reminders": False
            }

        elif "date" in command or "today" in command:
            current_date = datetime.now().strftime("%d %B %Y")
            return {
                "response": f"Today's date is {current_date}.",
                "speak": f"Today's date is {current_date}",
                "action_done": True,
                "weather_data": None,
                "refresh_reminders": False
            }

        # -------------------------------
        # Open websites
        # -------------------------------
        elif "open youtube" in command:
            webbrowser.open("https://www.youtube.com")
            return {
                "response": "Opening YouTube.",
                "speak": "Opening YouTube.",
                "action_done": True,
                "weather_data": None,
                "refresh_reminders": False
            }

        elif "open google" in command:
            webbrowser.open("https://www.google.com")
            return {
                "response": "Opening Google.",
                "speak": "Opening Google.",
                "action_done": True,
                "weather_data": None,
                "refresh_reminders": False
            }

        elif "open chatgpt" in command:
            webbrowser.open("https://chat.openai.com")
            return {
                "response": "Opening Chat G P T.",
                "speak": "Opening Chat G P T.",
                "action_done": True,
                "weather_data": None,
                "refresh_reminders": False
            }

        # -------------------------------
        # AI FALLBACK
        # -------------------------------
        else:
            ai_result = self.ai_service.ask_ai(original_command)

            return {
                "response": ai_result["response_text"],
                "speak": ai_result["response_text"],
                "action_done": ai_result["success"],
                "weather_data": None,
                "refresh_reminders": False
            }
