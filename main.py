
import customtkinter as ctk
import threading
from tkinter import messagebox
from speech_engine import SpeechEngine
from command_processor import CommandProcessor
from reminder_service import ReminderService
from reminder_scheduler import ReminderScheduler


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class VoiceAssistantApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Jarvis - AI Voice Assistant")
        self.geometry("1450x850")
        self.minsize(1280, 760)

        # Engines / services
        self.speech_engine = SpeechEngine()
        self.command_processor = CommandProcessor()
        self.reminder_service = ReminderService()
        self.reminder_scheduler = ReminderScheduler(self.on_reminder_triggered)

        # Colors
        self.bg_color = "#0f172a"
        self.sidebar_color = "#111827"
        self.card_color = "#1e293b"
        self.card2_color = "#172033"
        self.accent_color = "#3b82f6"
        self.green_color = "#22c55e"
        self.orange_color = "#f59e0b"
        self.red_color = "#ef4444"
        self.text_color = "#f8fafc"
        self.subtext_color = "#94a3b8"
        self.input_color = "#0f172a"
        self.list_item_color = "#111827"

        self.configure(fg_color=self.bg_color)

        self.is_listening = False

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()
        self.create_main_area()

        self.after(800, self.startup_greeting)
        self.after(1200, self.load_reminders_into_ui)
        self.after(1500, self.start_reminder_scheduler)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.chat_history = []

    # -------------------------------
    # Speech / response helpers
    # -------------------------------
    def speak_async(self, text):
        threading.Thread(target=self.speech_engine.speak, args=(text,), daemon=True).start()

    def startup_greeting(self):
        welcome_text = "Hello, I am Jarvis. Welcome to Avengers."
        self.add_response("Jarvis: " + welcome_text)
        self.speak_async(welcome_text)

    def add_response(self, text):
         # save to visible history
        self.chat_history.append(text)
        self.response_box.configure(state="normal")
        self.response_box.insert("end", text + "\n\n")
        self.response_box.see("end")
        self.response_box.configure(state="disabled")

    def set_status(self, text):
        self.status_label.configure(text=f"Status: {text}")

    # -------------------------------
    # Reminder scheduler
    # -------------------------------
    def start_reminder_scheduler(self):
        self.reminder_scheduler.start()
        self.add_response("Jarvis: Reminder scheduler started.")

    def on_reminder_triggered(self, reminder):
        self.after(0, lambda: self.show_reminder_alert(reminder))

    def show_reminder_alert(self, reminder):
        reminder_text = reminder["text"]
        reminder_time = reminder["time"]

        alert_text = f"Reminder: {reminder_text}\nTime: {reminder_time}"
        self.add_response("Jarvis: " + alert_text)
        self.speak_async(f"Reminder alert. {reminder_text}")

        messagebox.showinfo("Jarvis Reminder", alert_text)
        self.load_reminders_into_ui()

    # -------------------------------
    # Voice listening
    # -------------------------------
    def start_listening(self):
        if self.is_listening:
            return

        self.is_listening = True
        self.set_status("Listening...")
        self.add_response("Jarvis: Listening... Please speak now.")
        threading.Thread(target=self.listen_in_background, daemon=True).start()

    def stop_listening(self):
        self.is_listening = False
        self.set_status("Stopped")
        self.add_response("Jarvis: Listening stopped.")

    def listen_in_background(self):
        success, result = self.speech_engine.listen()

        if not self.is_listening:
            return

        self.is_listening = False

        if success:
            self.after(0, lambda: self.handle_recognized_text(result))
        else:
            self.after(0, lambda: self.handle_listen_error(result))

    def handle_recognized_text(self, text):
        self.set_status("Voice recognized")
        self.add_response(f"You (voice): {text}")

        self.command_entry.delete(0, "end")
        self.command_entry.insert(0, text)

        self.process_user_command(text)

    def handle_listen_error(self, error_message):
        self.set_status("Ready")
        self.add_response("Jarvis: " + error_message)
        self.speak_async(error_message)

    # -------------------------------
    # Command processing
    # -------------------------------
    def process_user_command(self, command):
        self.set_status("Processing command...")
        result = self.command_processor.process_command(command)

        response_text = result["response"]
        speak_text = result["speak"]
        weather_data = result.get("weather_data")
        refresh_reminders = result.get("refresh_reminders", False)

        self.add_response("Jarvis: " + response_text)
        self.speak_async(speak_text)

        if weather_data:
            self.update_weather_card(weather_data)

        if refresh_reminders:
            self.load_reminders_into_ui()

        self.set_status("Ready")

    # -------------------------------
    # Weather card update
    # -------------------------------
    def update_weather_card(self, weather_data):
        city = weather_data["city"]
        temp = weather_data["temperature"]
        desc = weather_data["description"]
        humidity = weather_data["humidity"]
        wind = weather_data["wind_speed"]

        self.weather_city_label.configure(text=city)
        self.weather_temp_label.configure(text=f"{temp}°C")
        self.weather_info_label.configure(
            text=f"{desc}\nHumidity: {humidity}%\nWind: {wind} m/s"
        )

    # -------------------------------
    # Reminder UI
    # -------------------------------
    def load_reminders_into_ui(self):
        reminders = self.reminder_service.get_all_reminders()

        for widget in self.reminder_list_frame.winfo_children():
            widget.destroy()

        # Top action buttons
        action_frame = ctk.CTkFrame(self.reminder_list_frame, fg_color="transparent")
        action_frame.pack(fill="x", padx=8, pady=(4, 8))

        refresh_btn = ctk.CTkButton(
            action_frame,
            text="Refresh",
            width=90,
            height=34,
            corner_radius=10,
            command=self.load_reminders_into_ui
        )
        refresh_btn.pack(side="left", padx=(0, 8))

        clear_btn = ctk.CTkButton(
            action_frame,
            text="Clear All",
            width=90,
            height=34,
            corner_radius=10,
            fg_color="#ef4444",
            hover_color="#dc2626",
            command=self.clear_all_reminders_from_ui
        )
        clear_btn.pack(side="left")

        if not reminders:
            empty_label = ctk.CTkLabel(
                self.reminder_list_frame,
                text="No reminders saved yet.",
                font=ctk.CTkFont(size=13),
                text_color=self.subtext_color
            )
            empty_label.pack(anchor="w", padx=10, pady=8)
            return

        for reminder in reminders[:20]:
            reminder_id = reminder["id"]
            reminder_text = reminder["text"]
            reminder_time = reminder["time"]
            is_triggered = reminder["is_triggered"]

            item_frame = ctk.CTkFrame(
                self.reminder_list_frame,
                fg_color=self.list_item_color,
                corner_radius=12
            )
            item_frame.pack(fill="x", padx=8, pady=6)

            text_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            text_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

            status_text = "Done" if is_triggered else "Pending"

            if reminder_time:
                display_text = (
                    f"ID: {reminder_id}\n"
                    f"{reminder_text}\n"
                    f"Time: {reminder_time}\n"
                    f"Status: {status_text}"
                )
            else:
                display_text = (
                    f"ID: {reminder_id}\n"
                    f"{reminder_text}\n"
                    f"Status: {status_text}"
                )

            label = ctk.CTkLabel(
                text_frame,
                text=display_text,
                justify="left",
                anchor="w",
                font=ctk.CTkFont(size=13),
                text_color=self.text_color
            )
            label.pack(anchor="w")

            delete_btn = ctk.CTkButton(
                item_frame,
                text="Delete",
                width=80,
                height=36,
                corner_radius=10,
                fg_color="#ef4444",
                hover_color="#dc2626",
                command=lambda rid=reminder_id: self.delete_reminder_from_ui(rid)
            )
            delete_btn.pack(side="right", padx=10, pady=10)

    def delete_reminder_from_ui(self, reminder_id):
        result = self.reminder_service.delete_reminder_by_id(reminder_id)
        self.add_response("Jarvis: " + result["response_text"])
        self.speak_async(result["response_text"])
        self.load_reminders_into_ui()

    def clear_all_reminders_from_ui(self):
        result = self.reminder_service.clear_all_reminders()
        self.add_response("Jarvis: " + result["response_text"])
        self.speak_async(result["response_text"])
        self.load_reminders_into_ui()

    # -------------------------------
    # Sidebar
    # -------------------------------
    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self,
            width=250,
            corner_radius=0,
            fg_color=self.sidebar_color
        )
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.sidebar.grid_rowconfigure(8, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="🎙 Jarvis",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.text_color
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(25, 10), sticky="w")

        self.subtitle_label = ctk.CTkLabel(
            self.sidebar,
            text="Smart Voice Automation",
            font=ctk.CTkFont(size=13),
            text_color=self.subtext_color
        )
        self.subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 25), sticky="w")

        self.dashboard_btn = ctk.CTkButton(self.sidebar, text="Dashboard", height=42, corner_radius=12, command=self.open_dashboard)
        self.dashboard_btn.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.weather_btn = ctk.CTkButton(self.sidebar, text="Weather", height=42, corner_radius=12,command=self.open_weather_from_sidebar)
        self.weather_btn.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.reminder_btn = ctk.CTkButton(self.sidebar, text="Reminders", height=42, corner_radius=12,command=self.open_reminders_from_sidebar)
        self.reminder_btn.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        self.history_btn = ctk.CTkButton(self.sidebar, text="History", height=42, corner_radius=12,command=self.open_history_window)
        self.history_btn.grid(row=5, column=0, padx=20, pady=10, sticky="ew")

        self.settings_btn = ctk.CTkButton(self.sidebar, text="Settings", height=42, corner_radius=12, command=self.open_settings_window)
        self.settings_btn.grid(row=6, column=0, padx=20, pady=10, sticky="ew")

        self.version_label = ctk.CTkLabel(
            self.sidebar,
            text="Version 1.0",
            font=ctk.CTkFont(size=12),
            text_color=self.subtext_color
        )
        self.version_label.grid(row=9, column=0, padx=20, pady=20, sticky="sw")

    # -------------------------------
    # Main Area
    # -------------------------------
    def create_main_area(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=3)
        self.main_frame.grid_columnconfigure(1, weight=2)
        self.main_frame.grid_rowconfigure(1, weight=1)

        self.create_header()
        self.create_dashboard()

    def create_header(self):
        self.header_frame = ctk.CTkFrame(
            self.main_frame,
            height=90,
            corner_radius=20,
            fg_color=self.card_color
        )
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Welcome to Jarvis",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.text_color
        )
        self.title_label.grid(row=0, column=0, padx=25, pady=(18, 5), sticky="w")

        self.status_label = ctk.CTkLabel(
            self.header_frame,
            text="Status: Ready",
            font=ctk.CTkFont(size=14),
            text_color=self.subtext_color
        )
        self.status_label.grid(row=1, column=0, padx=25, pady=(0, 15), sticky="w")

    def create_dashboard(self):
        self.left_panel = ctk.CTkFrame(self.main_frame, corner_radius=20, fg_color="transparent")
        self.left_panel.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        self.left_panel.grid_rowconfigure(1, weight=1)
        self.left_panel.grid_columnconfigure(0, weight=1)

        self.greeting_card = ctk.CTkFrame(
            self.left_panel,
            corner_radius=20,
            fg_color=self.card_color,
            height=160
        )
        self.greeting_card.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.greeting_card.grid_columnconfigure(1, weight=1)

        self.assistant_icon = ctk.CTkLabel(
            self.greeting_card,
            text="🤖",
            font=ctk.CTkFont(size=58)
        )
        self.assistant_icon.grid(row=0, column=0, rowspan=2, padx=(25, 15), pady=25)

        self.greeting_title = ctk.CTkLabel(
            self.greeting_card,
            text="Hello, I’m Jarvis",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.text_color
        )
        self.greeting_title.grid(row=0, column=1, sticky="sw", pady=(28, 5))

        self.greeting_desc = ctk.CTkLabel(
            self.greeting_card,
            text="Use voice or text commands to ask for weather, open apps, set reminders, send emails, and more.",
            font=ctk.CTkFont(size=14),
            text_color=self.subtext_color,
            justify="left",
            wraplength=550
        )
        self.greeting_desc.grid(row=1, column=1, sticky="nw", pady=(0, 25), padx=(0, 20))

        self.control_card = ctk.CTkFrame(self.left_panel, corner_radius=20, fg_color=self.card_color)
        self.control_card.grid(row=1, column=0, sticky="nsew")
        self.control_card.grid_columnconfigure(0, weight=1)

        self.control_title = ctk.CTkLabel(
            self.control_card,
            text="Jarvis Console",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.text_color
        )
        self.control_title.grid(row=0, column=0, sticky="w", padx=25, pady=(20, 5))

        self.control_subtitle = ctk.CTkLabel(
            self.control_card,
            text="Speak or type a command below.",
            font=ctk.CTkFont(size=14),
            text_color=self.subtext_color
        )
        self.control_subtitle.grid(row=1, column=0, sticky="w", padx=25, pady=(0, 20))

        self.mic_frame = ctk.CTkFrame(self.control_card, fg_color=self.card2_color, corner_radius=18)
        self.mic_frame.grid(row=2, column=0, sticky="ew", padx=25, pady=(0, 20))
        self.mic_frame.grid_columnconfigure((0, 1), weight=1)

        self.mic_button = ctk.CTkButton(
            self.mic_frame,
            text="🎤 Start Listening",
            height=58,
            corner_radius=16,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color=self.accent_color,
            hover_color="#2563eb",
            command=self.start_listening
        )
        self.mic_button.grid(row=0, column=0, padx=18, pady=18, sticky="ew")

        self.stop_button = ctk.CTkButton(
            self.mic_frame,
            text="⏹ Stop",
            height=58,
            corner_radius=16,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color=self.red_color,
            hover_color="#dc2626",
            command=self.stop_listening
        )
        self.stop_button.grid(row=0, column=1, padx=18, pady=18, sticky="ew")

        self.command_label = ctk.CTkLabel(
            self.control_card,
            text="Type Command",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.text_color
        )
        self.command_label.grid(row=3, column=0, sticky="w", padx=25, pady=(0, 10))

        self.command_entry = ctk.CTkEntry(
            self.control_card,
            height=52,
            corner_radius=14,
            placeholder_text="Example: remind me to drink water at 6 pm",
            font=ctk.CTkFont(size=15),
            fg_color=self.input_color,
            border_width=1,
            border_color="#334155"
        )
        self.command_entry.grid(row=4, column=0, sticky="ew", padx=25, pady=(0, 15))

        self.send_button = ctk.CTkButton(
            self.control_card,
            text="Send Command",
            height=48,
            corner_radius=14,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=self.green_color,
            hover_color="#16a34a",
            command=self.handle_send_command
        )
        self.send_button.grid(row=5, column=0, sticky="ew", padx=25, pady=(0, 20))

        self.quick_label = ctk.CTkLabel(
            self.control_card,
            text="Quick Actions",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.text_color
        )
        self.quick_label.grid(row=6, column=0, sticky="w", padx=25, pady=(0, 12))

        self.quick_frame = ctk.CTkFrame(self.control_card, fg_color="transparent")
        self.quick_frame.grid(row=7, column=0, sticky="ew", padx=25, pady=(0, 25))
        self.quick_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.quick_weather = ctk.CTkButton(
            self.quick_frame,
            text="🌤 Weather",
            height=45,
            corner_radius=12,
            fg_color=self.card2_color,
            command=lambda: self.process_user_command("weather in Ahmedabad")
        )
        self.quick_weather.grid(row=0, column=0, padx=6, sticky="ew")

        self.quick_time = ctk.CTkButton(
            self.quick_frame,
            text="🕒 Time",
            height=45,
            corner_radius=12,
            fg_color=self.card2_color,
            command=lambda: self.process_user_command("time")
        )
        self.quick_time.grid(row=0, column=1, padx=6, sticky="ew")

        self.quick_reminder = ctk.CTkButton(
            self.quick_frame,
            text="⏰ Reminders",
            height=45,
            corner_radius=12,
            fg_color=self.card2_color,
            command=lambda: self.process_user_command("show reminders")
        )
        self.quick_reminder.grid(row=0, column=2, padx=6, sticky="ew")

        self.right_panel = ctk.CTkFrame(self.main_frame, corner_radius=20, fg_color="transparent")
        self.right_panel.grid(row=1, column=1, sticky="nsew", padx=(10, 0))
        self.right_panel.grid_rowconfigure(0, weight=3)
        self.right_panel.grid_rowconfigure(1, weight=2)
        self.right_panel.grid_columnconfigure(0, weight=1)

        self.response_card = ctk.CTkFrame(self.right_panel, corner_radius=20, fg_color=self.card_color)
        self.response_card.grid(row=0, column=0, sticky="nsew", pady=(0, 20))
        self.response_card.grid_rowconfigure(1, weight=1)
        self.response_card.grid_columnconfigure(0, weight=1)

        self.response_title = ctk.CTkLabel(
            self.response_card,
            text="Jarvis Response",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=self.text_color
        )
        self.response_title.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        self.response_box = ctk.CTkTextbox(
            self.response_card,
            corner_radius=15,
            fg_color=self.input_color,
            text_color=self.text_color,
            font=ctk.CTkFont(size=14),
            wrap="word"
        )
        self.response_box.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.response_box.insert("end", "Jarvis is ready...\n\n")
        self.response_box.insert("end", "Reminder scheduler will monitor timed reminders.")
        self.response_box.configure(state="disabled")

        self.bottom_cards = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.bottom_cards.grid(row=1, column=0, sticky="nsew")
        self.bottom_cards.grid_columnconfigure((0, 1), weight=1)

        self.weather_card = ctk.CTkFrame(self.bottom_cards, corner_radius=18, fg_color=self.card_color)
        self.weather_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.reminder_card = ctk.CTkFrame(self.bottom_cards, corner_radius=18, fg_color=self.card_color)
        self.reminder_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        self.build_weather_card()
        self.build_reminder_card()

    def handle_send_command(self):
        command = self.command_entry.get().strip()
        if not command:
            self.add_response("Jarvis: Please type a command first.")
            self.speak_async("Please type a command first.")
            return

        self.add_response(f"You: {command}")
        self.command_entry.delete(0, "end")
        self.process_user_command(command)

    def build_weather_card(self):
        title = ctk.CTkLabel(
            self.weather_card,
            text="Weather Preview",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.text_color
        )
        title.pack(anchor="w", padx=18, pady=(18, 10))

        self.weather_icon_label = ctk.CTkLabel(
            self.weather_card,
            text="☁️",
            font=ctk.CTkFont(size=42)
        )
        self.weather_icon_label.pack(anchor="w", padx=18, pady=(5, 5))

        self.weather_city_label = ctk.CTkLabel(
            self.weather_card,
            text="Ahmedabad",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.text_color
        )
        self.weather_city_label.pack(anchor="w", padx=18)

        self.weather_temp_label = ctk.CTkLabel(
            self.weather_card,
            text="--°C",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.text_color
        )
        self.weather_temp_label.pack(anchor="w", padx=18, pady=(5, 2))

        self.weather_info_label = ctk.CTkLabel(
            self.weather_card,
            text="Weather not loaded yet",
            font=ctk.CTkFont(size=13),
            text_color=self.subtext_color,
            justify="left",
            wraplength=250
        )
        self.weather_info_label.pack(anchor="w", padx=18, pady=(6, 18))

    def build_reminder_card(self):
        title = ctk.CTkLabel(
            self.reminder_card,
            text="Saved Reminders",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.text_color
        )
        title.pack(anchor="w", padx=18, pady=(18, 10))

        self.reminder_list_frame = ctk.CTkScrollableFrame(
            self.reminder_card,
            fg_color="transparent",
            corner_radius=12
        )
        self.reminder_list_frame.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        
      # -------------------------------
      # Sidebar Actions
      # -------------------------------
    def open_dashboard(self):
      self.add_response("Jarvis: Dashboard is already open.")
      self.set_status("Ready")

    def open_weather_from_sidebar(self):
      self.add_response("Jarvis: Fetching weather for Ahmedabad...")
      self.process_user_command("weather in Ahmedabad")

    def open_reminders_from_sidebar(self):
      self.load_reminders_into_ui()
      self.add_response("Jarvis: Reminder panel refreshed.")
      self.set_status("Ready")

    def open_history_window(self):
     history_window = ctk.CTkToplevel(self)
     history_window.title("Jarvis History")
     history_window.geometry("700x500")
     history_window.transient(self)
     history_window.grab_set()

     title = ctk.CTkLabel(
        history_window,
        text="Jarvis Conversation History",
        font=ctk.CTkFont(size=22, weight="bold")
     )
     title.pack(pady=(20, 10))

     history_box = ctk.CTkTextbox(
        history_window,
        wrap="word",
        font=ctk.CTkFont(size=14)
     )
     history_box.pack(fill="both", expand=True, padx=20, pady=(0, 20))

     if not self.chat_history:
        history_box.insert("end", "No conversation history available yet.")
     else:
        for item in self.chat_history:
            history_box.insert("end", item + "\n\n")

     history_box.configure(state="disabled")

    def open_settings_window(self):
     settings_window = ctk.CTkToplevel(self)
     settings_window.title("Jarvis Settings")
     settings_window.geometry("420x420")
     settings_window.transient(self)
     settings_window.grab_set()

     title = ctk.CTkLabel(
        settings_window,
        text="Jarvis Settings",
        font=ctk.CTkFont(size=22, weight="bold")
     )
     title.pack(pady=(20, 15))

     info = ctk.CTkLabel(
        settings_window,
        text="Change Jarvis voice speed and theme.",
        font=ctk.CTkFont(size=14),
        justify="center"
     )
     info.pack(pady=(0, 20))

     # Voice Speed
     speed_label = ctk.CTkLabel(
        settings_window,
        text="Voice Speed",
        font=ctk.CTkFont(size=16, weight="bold")
     )
     speed_label.pack(pady=(5, 8))

     speed_slider = ctk.CTkSlider(settings_window, from_=120, to=220, number_of_steps=10)
     speed_slider.set(175)
     speed_slider.pack(fill="x", padx=30, pady=(0, 10))

     # Theme
     theme_label = ctk.CTkLabel(
        settings_window,
        text="Theme Mode",
        font=ctk.CTkFont(size=16, weight="bold")
     )
     theme_label.pack(pady=(15, 5))

     theme_option = ctk.CTkOptionMenu(
        settings_window,
        values=["Dark", "Light", "System"]
     )
     theme_option.set("Dark")
     theme_option.pack(pady=5)

     def apply_voice_speed():
        try:
            new_rate = int(speed_slider.get())
            self.speech_engine.engine.setProperty("rate", new_rate)
            self.add_response(f"Jarvis: Voice speed updated to {new_rate}.")
        except Exception as e:
            self.add_response(f"Jarvis: Could not update voice speed. {str(e)}")

     def apply_theme():
        try:
            selected = theme_option.get()
            ctk.set_appearance_mode(selected)
            self.add_response(f"Jarvis: Theme changed to {selected}.")
        except Exception as e:
            self.add_response(f"Jarvis: Could not change theme. {str(e)}")

     apply_btn = ctk.CTkButton(
        settings_window,
        text="Apply Voice Speed",
        command=apply_voice_speed
     )
     apply_btn.pack(pady=10)

     theme_btn = ctk.CTkButton(
        settings_window,
        text="Apply Theme",
        command=apply_theme
     )
     theme_btn.pack(pady=10)

     close_btn = ctk.CTkButton(
        settings_window,
        text="Close",
        fg_color="#ef4444",
        hover_color="#dc2626",
        command=settings_window.destroy
     )
     close_btn.pack(pady=(10, 20))    
    def on_closing(self):
        self.reminder_scheduler.stop()
        self.destroy()


if __name__ == "__main__":
    app = VoiceAssistantApp()
    app.mainloop()
