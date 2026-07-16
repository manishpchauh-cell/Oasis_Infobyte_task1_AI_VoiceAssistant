import speech_recognition as sr
import pyttsx3


class SpeechEngine:
    def __init__(self):
        self.recognizer = sr.Recognizer()

        # Faster listening settings
        self.recognizer.pause_threshold = 0.6
        self.recognizer.non_speaking_duration = 0.3
        self.recognizer.dynamic_energy_threshold = True

        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 175)

    def speak(self, text):
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print("Speech error:", e)

    def listen(self):
        """
        This matches main.py:
        success, result = self.speech_engine.listen()
        """
        try:
            with sr.Microphone() as source:
                print("Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)

                audio = self.recognizer.listen(
                    source,
                    timeout=3,
                    phrase_time_limit=5
                )

            command = self.recognizer.recognize_google(audio)
            return True, command

        except sr.WaitTimeoutError:
            return False, "Listening timed out."
        except sr.UnknownValueError:
            return False, "Sorry, I could not understand your voice."
        except sr.RequestError as e:
            return False, f"Speech recognition error: {str(e)}"
        except Exception as e:
            return False, f"Microphone error: {str(e)}"
