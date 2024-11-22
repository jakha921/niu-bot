from datetime import datetime

import aiohttp
import pytz
from loguru import logger

API_KEY = "056aea965aa6404ea93125839242011"


async def fetch_weather(session, city_name):
    """
    Asynchronously fetch current weather and hourly forecast from WeatherAPI.com.

    :param session: aiohttp ClientSession object.
    :param city_name: Name of the city.
    :return: JSON data with weather information or None in case of an error.
    """
    logger.info(f"Fetching weather data for {city_name}")
    url = "http://api.weatherapi.com/v1/forecast.json"
    params = {
        "key": API_KEY,
        "q": city_name,
        "days": 1,
        "aqi": "no",
        "alerts": "no",
        "lang": "ru"
    }
    try:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Error fetching weather data: {response.status}, {await response.text()}")
                return None
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None


async def get_weather_json(city_name: str):
    """
    Asynchronously get formatted weather data for a given city.

    :param city_name: Name of the city.
    :return: Formatted weather data dictionary or None.
    """
    logger.info(f"Getting weather data for {city_name}")
    async with aiohttp.ClientSession() as session:
        weather_data = await fetch_weather(session, city_name)
        if weather_data:
            return format_weather_data(weather_data)
        else:
            return None


def format_weather_data(data):
    """
    Format weather data for JSON output.

    :param data: JSON data from WeatherAPI.com.
    :return: Dictionary with formatted data.
    """
    logger.info("Formatting weather data")
    # pprint(data)
    # print('---------------------------------')
    location = data['location']
    current = data['current']
    forecast = data['forecast']['forecastday'][0]
    timezone = pytz.timezone(location['tz_id'])
    day = forecast['day']

    formatted_data = {
        "location": {
            "name": location['name'],
            "country": location['country'],
            "local_time": datetime.now(timezone).strftime('%d.%m.%Y'),
        },
        "day": {
            "max_temp": round(day['maxtemp_c']),
            "min_temp": round(day['mintemp_c']),
            "condition": day['condition']['text'],
            "icon_url": f"http:{day['condition']['icon']}",
            "wind_kph": day['maxwind_kph'],

        },
        "current_weather": {
            "temperature_c": current['temp_c'],
            "feels_like_c": current['feelslike_c'],
            "condition": current['condition']['text'],
            "wind_kph": current['wind_kph'],
            "humidity": current['humidity'],
            "pressure_mb": current['pressure_mb'],
            "sunrise": datetime.strptime(forecast['astro']['sunrise'], '%I:%M %p').strftime('%H:%M'),
            "sunset": datetime.strptime(forecast['astro']['sunset'], '%I:%M %p').strftime('%H:%M'),
            "icon_url": f"http:{current['condition']['icon']}"
        },
        "hourly_forecast": []
    }

    # Hours for which to get the forecast
    target_hours = {7, 10, 13, 16, 19, 22}

    for hour_data in forecast['hour']:
        # Extract hour from time
        hour = datetime.strptime(hour_data['time'], '%Y-%m-%d %H:%M').hour
        if hour in target_hours:
            time = datetime.strptime(hour_data['time'], '%Y-%m-%d %H:%M').strftime('%H:%M')
            hourly_data = {
                "time": time,
                "temperature": round(hour_data['temp_c']),
                "condition": hour_data['condition']['text'],
                "icon_url": f"http:{hour_data['condition']['icon']}"
            }
            formatted_data["hourly_forecast"].append(hourly_data)

    return formatted_data


if __name__ == '__main__':
    import asyncio

    loop = asyncio.get_event_loop()
    data = loop.run_until_complete(get_weather_json("Navoiy"))
    print(data)
