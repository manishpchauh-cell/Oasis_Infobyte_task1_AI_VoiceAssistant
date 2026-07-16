
import sqlite3


class DatabaseManager:
    def __init__(self, db_name="jarvis.db"):
        self.db_name = db_name
        self.create_reminders_table()

    def connect(self):
        return sqlite3.connect(self.db_name)

    def create_reminders_table(self):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reminder_text TEXT NOT NULL,
                reminder_time TEXT,
                is_triggered INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Add is_triggered column for old databases if missing
        try:
            cursor.execute("ALTER TABLE reminders ADD COLUMN is_triggered INTEGER DEFAULT 0")
        except:
            pass

        conn.commit()
        conn.close()

    def add_reminder(self, reminder_text, reminder_time=None):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO reminders (reminder_text, reminder_time, is_triggered)
            VALUES (?, ?, 0)
        """, (reminder_text, reminder_time))

        conn.commit()
        conn.close()

    def get_all_reminders(self):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, reminder_text, reminder_time, is_triggered, created_at
            FROM reminders
            ORDER BY id DESC
        """)

        reminders = cursor.fetchall()
        conn.close()
        return reminders

    def delete_reminder(self, reminder_id):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
        conn.commit()
        conn.close()

    def mark_reminder_triggered(self, reminder_id):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE reminders
            SET is_triggered = 1
            WHERE id = ?
        """, (reminder_id,))

        conn.commit()
        conn.close()

    def get_pending_timed_reminders(self):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, reminder_text, reminder_time, is_triggered, created_at
            FROM reminders
            WHERE reminder_time IS NOT NULL
              AND reminder_time != ''
              AND is_triggered = 0
            ORDER BY id ASC
        """)

        reminders = cursor.fetchall()
        conn.close()
        return reminders
