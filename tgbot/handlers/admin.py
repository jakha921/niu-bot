import os
from datetime import datetime

from aiogram import Dispatcher
from aiogram.types import Message
from loguru import logger

from tgbot.misc.broadcast import broadcast
from tgbot.misc.utils import Map
from tgbot.models.models import TGUser, get_student_which_has_not_passport
from tgbot.services.database import AsyncSession


async def admin_start(msg: Message, texts: Map):
    """Admin start command handler"""
    logger.info(f'Admin {msg.from_user.id} opened admin panel')
    await msg.reply(texts.admin.hi)


async def admin_stats(m: Message, db_session: AsyncSession, texts: Map):
    """Admin stats command handler"""
    logger.info(f'Admin {m.from_user.id} requested stats')
    count = await TGUser.users_count(db_session)
    await m.reply(texts.admin.total_users.format(count=count))


async def admin_broadcast(m: Message, db_session: AsyncSession, texts: Map):
    """Admin broadcast command handler"""
    logger.info(f'Admin {m.from_user.id} requested broadcast')
    broadcast_text = m.text.replace("/broadcast", "")
    if not broadcast_text:
        # there must be some text after command for broadcasting
        await m.reply(texts.admin.no_broadcast_text)
        return
    users = await TGUser.get_all_users(db_session)
    try:
        await m.reply(texts.admin.broadcast_started)
        logger.success(f'Broadcast started.')
        await broadcast(broadcast_text, users)
        logger.success(f'Broadcast finished.')
        await m.reply(texts.admin.broadcast_ended)
    except Exception as e:
        await m.reply(texts.admin.broadcast_error.format(err=e))
        logger.error("Error while broadcasting!")
        logger.exception(e)


async def admin_send_message(msg: Message, db_session: AsyncSession):
    """
    Admin send message command handler
    get reply message and send it to all users
    """
    logger.info(f'Admin {msg.from_user.id} requested send message')
    users = await TGUser.get_all_users(db_session)
    try:
        post = msg.reply_to_message
        if not post:
            await msg.reply("Reply to message for sending to users")
            return
        await msg.reply("Sending message...")
        for user in users:
            try:
                if user.telegram_id == msg.from_user.id:
                    continue
                await post.copy_to(user.telegram_id)
            except Exception as e:
                logger.exception(e)
                logger.error(f"Error while sending message to user {user.telegram_id}")
        await msg.reply("Message sent!")
    except Exception as e:
        await msg.reply(f"Error while sending message: {e}")
        logger.error("Error while sending message!")
        logger.exception(e)


async def remove_weather_forecast_img(msg: Message, texts: Map):
    """Admin remove weather forecast image command handler"""
    logger.info(f'Admin {msg.from_user.id} requested remove weather forecast image')
    try:
        to_remove = []
        folder = 'tgbot/misc/weather_forecast_img'

        if not os.listdir(folder):
            await msg.reply("No images to remove")
            return

        today_date = datetime.today().strftime("%Y-%m-%d")
        for file in os.listdir(folder):
            if file.endswith('.png') and file.split('_')[-1].replace('.png', '') < today_date:
                to_remove.append(file)

        if not to_remove:
            await msg.reply("All images are up to date")
            return

        # remove images
        for file in to_remove:
            os.remove(os.path.join(folder, file))
            logger.info(f"Removed {file}")
        await msg.reply(f"Removed {len(to_remove)} images")


    except Exception as e:
        await msg.reply(f"Error while removing weather forecast image: {e}")
        logger.error("Error while removing weather forecast image!")
        logger.exception(e)


async def send_custom_message(msg: Message, db_session: AsyncSession):
    """
    Admin send message command handler
    get reply message and send it to all users
    """
    logger.info(f'Admin {msg.from_user.id} requested send message')
    users = await get_student_which_has_not_passport(db_session)
    try:
        post = msg.reply_to_message
        if not post:
            await msg.reply("Reply to message for sending to users")
            return
        await msg.reply("Sending message...")
        for user in users:
            try:
                if user.telegram_id == msg.from_user.id:
                    continue
                await post.copy_to(user.telegram_id)
            except Exception as e:
                logger.exception(e)
                logger.error(f"Error while sending message to user {user.telegram_id}")
        await msg.reply("Message sent!")
    except Exception as e:
        await msg.reply(f"Error while sending message: {e}")
        logger.error("Error while sending message!")
        logger.exception(e)


def register_admin(dp: Dispatcher):
    dp.register_message_handler(
        admin_start,
        commands=["admin"],
        state="*",
        is_admin=True
    )
    dp.register_message_handler(
        admin_stats,
        commands=["stats"],
        state="*",
        is_admin=True
    )
    dp.register_message_handler(
        admin_broadcast,
        commands=["broadcast"],
        state="*",
        is_admin=True
    ),
    dp.register_message_handler(
        admin_send_message,
        commands=["send_post"],
        state="*",
        is_admin=True
    )
    dp.register_message_handler(
        remove_weather_forecast_img,
        commands=["remove"],
        state="*",
        is_admin=True
    )
    dp.register_message_handler(
        send_custom_message,
        commands=["send_not_passport"],
        state="*",
        is_admin=True
    )
