import json
from datetime import datetime

from aiogram import Dispatcher
from aiogram.dispatcher.filters import Command
from aiogram.types import Message
from loguru import logger

from tgbot.filters.group import GroupChatFilter


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

            text_admin += f"\n\nJamoadoshimizni chin qalbdan jamoa nomidan qutlaymiz ! Sizga ishlaringgizga rivoj tilaymiz ! 🎉🎉🎉"

            await msg.answer(text_admin)
        else:
            await msg.answer("Bugun tug'ilganlar yo'q!")


async def start(msg: Message):
    """Bot start handler"""
    await msg.answer(f"Hello, {msg.from_user.full_name}, Welcome to the group!")


def register_manage_chat(dp: Dispatcher):
    dp.register_message_handler(
        start,
        GroupChatFilter(),
        commands=["start"],
    )
    dp.register_message_handler(
        send_congratulation_to_group,
        GroupChatFilter(),
        Command("bday", prefixes="!/"),
        is_admin=True
    )
