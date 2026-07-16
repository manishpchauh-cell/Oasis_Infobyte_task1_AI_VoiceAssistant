
from datetime import datetime
from database import DatabaseManager


class ReminderService:
    def __init__(self):
        self.db = DatabaseManager()

    def normalize_time(self, time_text):
        """
        Convert user time like:
        6 pm, 6:30 pm, 11:05 AM
        into standard format:
        06:00 PM, 06:30 PM, 11:05 AM
        """
        if not time_text:
            return None

        time_text = time_text.strip().upper().replace(".", ":")

        possible_formats = [
            "%I:%M %p",   # 06:30 PM
            "%I %p",      # 6 PM
            "%I:%M%p",    # 6:30PM
            "%I%p"        # 6PM
        ]

        for fmt in possible_formats:
            try:
                parsed = datetime.strptime(time_text, fmt)
                return parsed.strftime("%I:%M %p")
            except ValueError:
                continue

        return time_text  # if not recognized, keep original

    def extract_reminder_data(self, command):
        command = command.strip()
        lower_command = command.lower()

        # remind me to <task> at <time>
        if lower_command.startswith("remind me to ") and " at " in lower_command:
            task_part = command[13:].strip()
            parts = task_part.rsplit(" at ", 1)
            if len(parts) == 2:
                reminder_text = parts[0].strip()
                reminder_time = self.normalize_time(parts[1].strip())
                return reminder_text, reminder_time

        # set reminder to <task> at <time>
        if lower_command.startswith("set reminder to ") and " at " in lower_command:
            task_part = command[16:].strip()
            parts = task_part.rsplit(" at ", 1)
            if len(parts) == 2:
                reminder_text = parts[0].strip()
                reminder_time = self.normalize_time(parts[1].strip())
                return reminder_text, reminder_time

        # remind me to <task>
        if lower_command.startswith("remind me to "):
            reminder_text = command[13:].strip()
            return reminder_text, None

        # set reminder to <task>
        if lower_command.startswith("set reminder to "):
            reminder_text = command[16:].strip()
            return reminder_text, None

        return None, None

    def add_reminder_from_command(self, command):
        reminder_text, reminder_time = self.extract_reminder_data(command)

        if not reminder_text:
            return {
                "success": False,
                "response_text": "I could not understand the reminder command. Example: remind me to drink water."
            }

        self.db.add_reminder(reminder_text, reminder_time)

        if reminder_time:
            response = f"Reminder saved: {reminder_text} at {reminder_time}."
        else:
            response = f"Reminder saved: {reminder_text}."

        return {
            "success": True,
            "response_text": response,
            "reminder_text": reminder_text,
            "reminder_time": reminder_time
        }

    def get_all_reminders(self):
        reminders = self.db.get_all_reminders()
        formatted_reminders = []

        for reminder in reminders:
            reminder_id, reminder_text, reminder_time, is_triggered, created_at = reminder
            formatted_reminders.append({
                "id": reminder_id,
                "text": reminder_text,
                "time": reminder_time,
                "is_triggered": is_triggered,
                "created_at": created_at
            })

        return formatted_reminders

    def delete_reminder_by_id(self, reminder_id):
        try:
            reminder_id = int(reminder_id)
            self.db.delete_reminder(reminder_id)
            return {
                "success": True,
                "response_text": f"Reminder {reminder_id} deleted successfully."
            }
        except Exception:
            return {
                "success": False,
                "response_text": "Invalid reminder ID."
            }

    def clear_all_reminders(self):
        reminders = self.db.get_all_reminders()

        for reminder in reminders:
            reminder_id = reminder[0]
            self.db.delete_reminder(reminder_id)

        return {
            "success": True,
            "response_text": "All reminders cleared successfully."
        }

    def get_due_reminders(self, current_time_str):
        due_reminders = []
        reminders = self.db.get_pending_timed_reminders()

        current_time = self.normalize_time(current_time_str)

        for reminder in reminders:
            reminder_id, reminder_text, reminder_time, is_triggered, created_at = reminder

            if not reminder_time:
                continue

            saved_time = self.normalize_time(reminder_time)

            if saved_time == current_time:
                due_reminders.append({
                    "id": reminder_id,
                    "text": reminder_text,
                    "time": reminder_time
                })

        return due_reminders

    def mark_triggered(self, reminder_id):
        self.db.mark_reminder_triggered(reminder_id)
