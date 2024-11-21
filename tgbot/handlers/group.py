import json
import os
from datetime import datetime

from aiogram import Dispatcher
from aiogram.dispatcher.filters import Command
from aiogram.types import Message
from loguru import logger

from tgbot.filters.group import GroupChatFilter
from tgbot.misc.weather_integration.convert_data_to_img import generate_weather_report

# Define the base directory relative to this script's location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, 'tgbot', 'misc', 'weather_forecast_img')



async def send_congratulation_to_group(msg: Message):
    """Client week day chosen handler"""
    logger.info(f'User {msg.from_user.id} send congratulation to group')

    # get from json data
    with open("./grouped_data.json", "r") as file:
        data = json.load(file)
        now = datetime.now()

        month_now = f'{now.month}' if now.month > 9 else f'0{now.month}'
        day_now = f'{now.day}' if now.day > 9 else f'0{now.day}'

        # month_now = '05'
        # day_now = '10'

        # print(f'day now: {day_now} {type(day_now)}, month now: {month_now} {type(month_now)}')

        bdays = data[day_now][month_now] if data.get(day_now) and data[day_now].get(month_now) else None

        if bdays:
            text_admin = f"Bugungi kun tavallud ayyomi bilan:\n\n"
            for bday in bdays:
                text_admin += f"<i>{bday['first_name']} {bday['last_name']} {bday['middle_name']}</i> 🎂\n"

            text_admin += f"\n\nJamoadosh(lar)imizni chin qalbdan jamoa nomidan qutlaymiz ! Ishlaringgizga rivoj tilaymiz ! 🎉🎉🎉 Hurmat bilan NIU jamoasi."

            await msg.answer(text_admin)
        else:
            await msg.answer("Bugun tug'ilganlar yo'q!")


async def start(msg: Message):
    """Bot start handler"""
    await msg.answer(f"Asalomu aleykum, {msg.from_user.first_name}, xush kelibsiz!")


async def get_weather_report(message: Message):
    """
    Handles the /weather command. Generates a weather report for the given city.
    Usage: /weather <city>
    """
    logger.info(f"User {message.from_user.id} requested weather report")
    args = message.get_args()

    city = args.strip() if args else "Navoiy"
    wait = await message.reply(f"Ob-havo ma'lumotlari {city} uchun qidirilmoqda...")

    try:
        # Ensure the image directory exists
        os.makedirs(IMAGE_DIR, exist_ok=True)

        # Construct the image filename
        weather_img_name = f'weather_report_{city.capitalize()}_{datetime.today().strftime("%Y-%m-%d")}.png'
        image_path = os.path.join(IMAGE_DIR, weather_img_name)

        # Check if the image already exists
        if os.path.exists(image_path):
            with open(image_path, 'rb') as photo:
                await wait.delete()
                await message.reply_photo(photo, caption=f"Ob-havo ma'lumotlari {city} uchun, kuningiz xayrli bo'lsin!")
            return

        # Run the generate_weather_report function asynchronously
        output_image = await generate_weather_report(
            location=city.capitalize(),
            output_image=image_path
        )
        if not output_image:
            await wait.edit_text(f"Ob-havo ma'lumotlari {city} uchun topilmadi.")
            return

        # Send the generated image back to the user
        with open(f"tgbot/misc/weather_integration/weather_forecast_img/{weather_img_name}", "rb") as photo:
            await wait.delete()
            await message.reply_photo(photo, caption=f"Ob-havo ma'lumotlari {city} uchun, kuningiz xayrli bo'lsin!")

    except Exception as e:
        logger.exception(f"An error occurred while generating the weather report. {e}")
        await message.reply("Kutilmagan xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.")


def register_manage_chat(dp: Dispatcher):
    dp.register_message_handler(
        start,
        GroupChatFilter(),
        commands=["start"],
    )
    dp.register_message_handler(
        get_weather_report,
        GroupChatFilter(),
        commands=["weather"],
    )
    dp.register_message_handler(
        send_congratulation_to_group,
        GroupChatFilter(),
        Command("bday", prefixes="!/"),
        is_admin=True
    )
