import os
import requests
from dotenv import load_dotenv

load_dotenv()
OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')

def fetch(location):
    try:
        url = (
            f"http://api.openweathermap.org/data/2.5/weather?q={location}"
            f"&appid={OPENWEATHERMAP_API_KEY}"
        )
        response = requests.get(url)
        data = response.json()

        if data.get('cod') != 200:
            return "General loamy soil suitable for various crops."

        weather_desc = data['weather'][0]['description']
        temp_k = data['main']['temp']
        temp_c = round(temp_k - 273.15, 2)

        soil_info = (
            f"Location: {location}\n"
            f"Weather: {weather_desc}\n"
            f"Temperature: {temp_c}°C\n"
            f"Based on this, the soil is likely loamy with average moisture."
        )
        return soil_info

    except Exception as e:
        return "Failed to fetch location data."
