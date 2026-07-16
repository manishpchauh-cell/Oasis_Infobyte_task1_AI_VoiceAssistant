import os
import subprocess
from datetime import datetime
from pathlib import Path


class SystemService:
    def __init__(self):
        self.screenshot_folder = Path("screenshots")
        self.screenshot_folder.mkdir(exist_ok=True)

    # -------------------------------
    # OPEN APPS
    # -------------------------------
    def open_notepad(self):
        try:
            subprocess.Popen("notepad.exe")
            return {"success": True, "response_text": "Opening Notepad."}
        except Exception as e:
            return {"success": False, "response_text": f"Could not open Notepad. {str(e)}"}

    def open_calculator(self):
        try:
            subprocess.Popen("calc.exe")
            return {"success": True, "response_text": "Opening Calculator."}
        except Exception as e:
            return {"success": False, "response_text": f"Could not open Calculator. {str(e)}"}

    def open_chrome(self):
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ]

        for path in possible_paths:
            if os.path.exists(path):
                try:
                    subprocess.Popen(path)
                    return {"success": True, "response_text": "Opening Chrome."}
                except Exception as e:
                    return {"success": False, "response_text": f"Could not open Chrome. {str(e)}"}

        return {"success": False, "response_text": "Chrome not found on this system."}

    def open_vscode(self):
        possible_paths = [
            r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe",
            r"C:\Program Files\Microsoft VS Code\Code.exe"
        ]

        # expand %USERNAME% if present
        expanded_paths = [os.path.expandvars(path) for path in possible_paths]

        for path in expanded_paths:
            if os.path.exists(path):
                try:
                    subprocess.Popen(path)
                    return {"success": True, "response_text": "Opening Visual Studio Code."}
                except Exception as e:
                    return {"success": False, "response_text": f"Could not open VS Code. {str(e)}"}

        return {"success": False, "response_text": "VS Code not found on this system."}

    def open_file_explorer(self):
        try:
            subprocess.Popen("explorer")
            return {"success": True, "response_text": "Opening File Explorer."}
        except Exception as e:
            return {"success": False, "response_text": f"Could not open File Explorer. {str(e)}"}

    # -------------------------------
    # SYSTEM CONTROL
    # -------------------------------
    def shutdown_pc(self):
        try:
            os.system("shutdown /s /t 5")
            return {"success": True, "response_text": "Shutting down your computer in 5 seconds."}
        except Exception as e:
            return {"success": False, "response_text": f"Could not shut down PC. {str(e)}"}

    def restart_pc(self):
        try:
            os.system("shutdown /r /t 5")
            return {"success": True, "response_text": "Restarting your computer in 5 seconds."}
        except Exception as e:
            return {"success": False, "response_text": f"Could not restart PC. {str(e)}"}

    def lock_pc(self):
        try:
            os.system("rundll32.exe user32.dll,LockWorkStation")
            return {"success": True, "response_text": "Locking your computer."}
        except Exception as e:
            return {"success": False, "response_text": f"Could not lock PC. {str(e)}"}

    # -------------------------------
    # SCREENSHOT
    # -------------------------------
    def take_screenshot(self):
        try:
            from PIL import ImageGrab

            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            file_path = self.screenshot_folder / f"screenshot_{timestamp}.png"

            image = ImageGrab.grab()
            image.save(file_path)

            return {
                "success": True,
                "response_text": f"Screenshot saved successfully as {file_path.name}."
            }
        except Exception as e:
            return {
                "success": False,
                "response_text": f"Could not take screenshot. {str(e)}"
            }
