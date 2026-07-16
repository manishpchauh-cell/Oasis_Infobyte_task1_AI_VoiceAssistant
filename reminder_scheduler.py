
import threading
import time
from datetime import datetime
from reminder_service import ReminderService


class ReminderScheduler:
    def __init__(self, callback_function):
        self.reminder_service = ReminderService()
        self.callback_function = callback_function
        self.is_running = False
        self.thread = None

    def start(self):
        if self.is_running:
            return

        self.is_running = True
        self.thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.thread.start()

    def stop(self):
        self.is_running = False

    def run_scheduler(self):
        while self.is_running:
            try:
                current_time = datetime.now().strftime("%I:%M %p")
                due_reminders = self.reminder_service.get_due_reminders(current_time)

                for reminder in due_reminders:
                    self.callback_function(reminder)
                    self.reminder_service.mark_triggered(reminder["id"])

            except Exception as e:
                print("Reminder scheduler error:", e)

            time.sleep(20)
