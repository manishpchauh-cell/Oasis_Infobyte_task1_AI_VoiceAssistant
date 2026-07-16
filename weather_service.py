
import requests


class WeatherService:
    def __init__(self):
        # Paste your OpenWeatherMap API key here
        self.api_key = "f47cab102b0e051a9766669d961bad6b"
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"

    def get_weather(self, city):
        """
        Returns:
        {
            "success": True/False,
            "city": "...",
            "temperature": "...",
            "description": "...",
            "humidity": "...",
            "wind_speed": "...",
            "response_text": "..."
        }
        """
        if not city:
            return {
                "success": False,
                "response_text": "Please provide a city name for weather."
            }

        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric"
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            data = response.json()

            if response.status_code != 200:
                return {
                    "success": False,
                    "response_text": f"Sorry, I could not find weather for {city}."
                }

            city_name = data["name"]
            temperature = data["main"]["temp"]
            description = data["weather"][0]["description"].title()
            humidity = data["main"]["humidity"]
            wind_speed = data["wind"]["speed"]

            response_text = (
                f"The weather in {city_name} is {description} with a temperature of "
                f"{temperature} degree Celsius. Humidity is {humidity} percent and "
                f"wind speed is {wind_speed} meters per second."
            )

            return {
                "success": True,
                "city": city_name,
                "temperature": temperature,
                "description": description,
                "humidity": humidity,
                "wind_speed": wind_speed,
                "response_text": response_text
            }

        except requests.RequestException:
            return {
                "success": False,
                "response_text": "Weather service is currently unavailable."
            }

        except Exception:
            return {
                "success": False,
                "response_text": "Something went wrong while fetching weather."
            }
