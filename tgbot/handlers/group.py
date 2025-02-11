import json
import os
from datetime import datetime

from aiogram import Dispatcher
from aiogram.dispatcher.filters import Command
from aiogram.types import Message
from loguru import logger

from tgbot.filters.group import GroupChatFilter
from tgbot.misc.weather_integration.convert_data_to_img import generate_weather_report


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
            if len(bdays) == 1:
                bday = bdays[0]
                text_admin = (
                    f"🎊 Hurmatli <i>{bday['first_name']} {bday['middle_name']} {bday['last_name']}</i>! 🎂\n\n"
                    "Bugungi tug‘ilgan kuningiz munosabati bilan sizni chin dildan muborakbod etamiz! 🎉\n"
                    "Yangi yoshingiz yanada ko‘proq imkoniyatlar, muvaffaqiyat va baraka olib kelsin. ✨\n"
                    "Jamoamizdagi faolligingiz va fidoyiligingiz biz uchun katta ahamiyatga ega. 🤝\n\n"
                    "Hurmat bilan, NIU jamoasi. 🎈"
                )
            else:
                text_admin = "🎊 Bugun bizning jamoadoshlarimiz tavallud ayyomini nishonlamoqda! 🎂🎈\n\n"

                for bday in bdays:
                    text_admin += f"🎉 <i>{bday['first_name']} {bday['middle_name']} {bday['last_name']}</i>\n"

                text_admin += (
                    "\nBugungi tug‘ilgan kun munosabati bilan sizlarni chin dildan qutlaymiz! 🌟\n"
                    "Sizlarga mustahkam sog‘liq, yangi yutuqlar va barqaror muvaffaqiyatlar tilaymiz. ✨\n"
                    "Sizning mehnatingiz va fidoyiligingiz jamoamiz uchun juda muhim! 🤝\n\n"
                    "Hurmat bilan, NIU jamoasi. 🎈"
                )

            await msg.answer(text_admin)
        else:
            await msg.answer("Bugun tug‘ilgan kun nishonlaydigan hamkasblar yo‘q. 😊")


async def start(msg: Message):
    """Bot start handler"""
    await msg.answer(f"Asalomu aleykum, {msg.from_user.first_name}, xush kelibsiz!")


async def get_weather_report(message: Message):
    """
    Handles the /weather command. Generates a weather report for the given city.
    Usage: /weather <city>
    """
    logger.info(f"User {message.from_user.id} requested weather report")

    # if not from group, return error
    if message.chat.type not in ['group', 'supergroup']:
        await message.reply("Bu buyruq faqat guruhda ishlaydi.")
        return

    args = message.get_args()

    city = args.strip() if args else "Navoiy"
    wait = await message.reply(f"Ob-havo ma'lumotlari {city} uchun qidirilmoqda...")

    try:
        # Construct the image filename
        weather_img_name = f'weather_report_{city.capitalize()}_{datetime.today().strftime("%Y-%m-%d")}.png'
        # base_dir = os.path.abspath(os.path.join('tgbot', 'misc', 'weather_integration'))
        base_dir = "./tgbot/misc/weather_integration"
        # image_path = os.path.join('tgbot', 'misc', 'weather_integration', 'weather_forecast_img', weather_img_name)
        image_path = f"{base_dir}/weather_forecast_img/{weather_img_name}"

        # Check if the image already exists
        if os.path.exists(image_path):
            logger.info(f"Sending existing weather report image to user: {message.from_user.id}")
            with open(image_path, 'rb') as photo:
                await wait.delete()
                await message.reply_photo(photo, caption=f"Ob-havo ma'lumotlari {city} uchun, kuningiz xayrli bo'lsin!")
            return
        logger.info(f"Weather report image not found: {image_path}")

        # Run the generate_weather_report function asynchronously
        is_created_img = await generate_weather_report(
            location=city.capitalize(),
            output_image_name=weather_img_name
        )
        logger.info(f"Generated weather report for {city}")
        if not os.path.exists(f"{base_dir}/weather_forecast_img/{weather_img_name}") and is_created_img!=True:
            logger.error(f"File was not created: {image_path}")
            await wait.edit_text(f"Ob-havo ma'lumotlari {city} uchun topilmadi.")
            return

        logger.info(f"Sending weather report image to user: {message.from_user.id}")
        # Send the generated image back to the user
        with open(f"{base_dir}/weather_forecast_img/{weather_img_name}", 'rb') as photo:
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
        # GroupChatFilter(),
        commands=["weather"],
    )
    dp.register_message_handler(
        send_congratulation_to_group,
        GroupChatFilter(),
        Command("bday", prefixes="!/"),
        is_admin=True
    )
