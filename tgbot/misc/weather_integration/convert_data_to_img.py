import asyncio
import os

import jinja2.exceptions
from html2image import Html2Image
from jinja2 import Environment, FileSystemLoader

from tgbot.misc.weather_integration.weather_api import get_weather_json

translation_text = {
    "Солнечно": "Quyoshli",
    "Переменная облачность": "Qisman bulutli",
    "Облачно": "Bulutli",
    "Пасмурно": "Bulutli",
    "Дымка": "Tuman",
    "Местами дождь": "Ba'zi joylarda yomg'ir",
    "Местами снег": "Ba'zi joylarda qor",
    "Местами дождь со снегом": "Ba'zi joylarda yomg'ir va qor",
    "Местами замерзающая морось": "Ba'zi joylarda muzlayotgan yomg'ir",
    "Местами грозы": "Ba'zi joylarda momaqaldiroq",
    "Поземок": "Qor bo'roni",
    "Метель": "Bo'ron",
    "Туман": "Tuman",
    "Переохлажденный туман": "Muzli tuman",
    "Местами слабая морось": "Ba'zi joylarda yengil yomg'ir",
    "Слабая морось": "Yengil yomg'ir",
    "Замерзающая морось": "Muzlayotgan yomg'ir",
    "Сильная замерзающая морось": "Kuchli muzlayotgan yomg'ir",
    "Местами небольшой дождь": "Ba'zi joylarda yengil yomg'ir",
    "Небольшой дождь": "Yengil yomg'ir",
    "Временами умеренный дождь": "Vaqti-vaqti bilan o'rtacha yomg'ir",
    "Умеренный дождь": "O'rtacha yomg'ir",
    "Временами сильный дождь": "Vaqti-vaqti bilan kuchli yomg'ir",
    "Сильный дождь": "Kuchli yomg'ir",
    "Слабый переохлажденный дождь": "Yengil muzlayotgan yomg'ir",
    "Умеренный или сильный переохлажденный дождь": "O'rtacha yoki kuchli muzlayotgan yomg'ir",
    "Небольшой дождь со снегом": "Yengil yomg'ir va qor",
    "Умеренный или сильный дождь со снегом": "O'rtacha yoki kuchli yomg'ir va qor",
    "Местами небольшой снег": "Ba'zi joylarda yengil qor",
    "Небольшой снег": "Yengil qor",
    "Местами умеренный снег": "Ba'zi joylarda o'rtacha qor",
    "Умеренный снег": "O'rtacha qor",
    "Местами сильный снег": "Ba'zi joylarda kuchli qor",
    "Сильный снег": "Kuchli qor",
    "Ледяной дождь": "Muzli yomg'ir",
    "Небольшой ливневый дождь": "Yengil jala",
    "Умеренный или сильный ливневый дождь": "O'rtacha yoki kuchli jala",
    "Сильные ливни": "Kuchli jala",
    "Небольшой ливневый дождь со снегом": "Yengil jala va qor",
    "Умеренные или сильные ливневые дожди со снегом": "O'rtacha yoki kuchli jala va qor",
    "Умеренный или сильный снег": "O'rtacha yoki kuchli qor",
    "Небольшой ледяной дождь": "Yengil muzli yomg'ir",
    "Умеренный или сильный ледяной дождь": "O'rtacha yoki kuchli muzli yomg'ir",
    "В отдельных районах местами небольшой дождь с грозой": "Ayrim joylarda yengil yomg'ir va momaqaldiroq",
    "В отдельных районах умеренный или сильный дождь с грозой": "Ayrim joylarda o'rtacha yoki kuchli yomg'ir va momaqaldiroq",
    "В отдельных районах местами небольшой снег с грозой": "Ayrim joylarda yengil qor va momaqaldiroq",
    "В отдельных районах умеренный или сильный снег с грозой": "Ayrim joylarda o'rtacha yoki kuchli qor va momaqaldiroq"
}


async def generate_weather_report(
        location: str,
        template_path: str = 'template.html',
        output_image: str = 'weather_report.png',
        scale_factor: int = 5,
        window_size: tuple = (520, 420)):
    """
    Asynchronously generates a weather report image for a specified location.

    :param location: Name of the location for the weather report.
    :param template_path: Path to the HTML template file.
    :param output_image: Filename for the output image.
    :param scale_factor: Device scale factor for the screenshot.
    :param window_size: Window size for the screenshot.
    :return: Path to the generated image or None if an error occurred.
    """
    # Fetch weather data
    weather_data = await get_weather_json(location)
    if not weather_data:
        print(f"Failed to get weather data for {location}")
        return None

    # Define base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Define paths
    template_dir = os.path.join(base_dir, 'tgbot', 'misc', 'weather_integration')
    output_dir = os.path.join(base_dir, 'tgbot', 'misc', 'weather_forecast_img')
    html_file_path = os.path.join(output_dir, 'weather_report.html')
    output_image_path = os.path.join(output_dir, output_image)

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Load the HTML template
    try:
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template(template_path)
    except jinja2.exceptions.TemplateNotFound:
        print(f"Template '{template_path}' not found in '{template_dir}'")
        return None

    # Render the HTML with weather data
    html_content = template.render(
        location_name=weather_data['location']['name'],
        country=weather_data['location']['country'],
        local_time=weather_data['location']['local_time'],
        sunrise=weather_data['current_weather']['sunrise'],
        sunset=weather_data['current_weather']['sunset'],
        max_temp=weather_data['day']['max_temp'],
        min_temp=weather_data['day']['min_temp'],
        icon_url=weather_data['day']['icon_url'],
        day_condition=translation_text.get(weather_data['day']['condition'], weather_data['day']['condition']),
        current_temp=weather_data['current_weather']['temperature_c'],
        feels_like=weather_data['current_weather']['feels_like_c'],
        condition=weather_data['current_weather']['condition'],
        wind_speed=weather_data['current_weather']['wind_kph'],
        humidity=weather_data['current_weather']['humidity'],
        pressure=weather_data['current_weather']['pressure_mb'],
        current_icon_url=weather_data['current_weather']['icon_url'],
        hourly_forecast=weather_data['hourly_forecast']
    )

    # Save the rendered HTML to a file
    with open(html_file_path, 'w', encoding='utf-8') as file:
        file.write(html_content)

    # Initialize Html2Image with custom flags
    hti = Html2Image(
        custom_flags=[
            f'--force-device-scale-factor={scale_factor}',
            f'--window-size={window_size[0]},{window_size[1]}'
        ],
        output_path=output_dir
    )

    # Generate the screenshot
    hti.screenshot(
        html_file=html_file_path,
        save_as=output_image
    )

    print(f"Weather report saved as {output_image_path}")

    # Clean up the HTML file
    os.remove(html_file_path)

    return output_image_path


if __name__ == '__main__':
    asyncio.run(generate_weather_report('Navoi'))
