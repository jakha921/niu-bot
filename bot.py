import os

from loguru import logger

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.utils.executor import start_webhook, start_polling
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.types.bot_command_scope import BotCommandScopeDefault

from tgbot.config import load_config
from tgbot.filters import role, reply_kb
from tgbot.handlers.group import register_manage_chat
from tgbot.handlers.payment_cron import register_payment
from tgbot.handlers.student_menu import register_student
from tgbot.middlewares.throtling import ThrottlingMiddleware
from tgbot.middlewares.db import DbMiddleware
from tgbot.middlewares.translate import TranslationMiddleware
from tgbot.services.database import create_db_session
from tgbot.handlers.admin import register_admin
from tgbot.handlers.user import register_user

# load config from bot.ini file
config = load_config("bot.ini")

# create bot instance
bot = Bot(token=config.tg_bot.token, parse_mode="HTML")
# create dispatcher
dp = Dispatcher(bot)


def init_logger():
    """Logger initializer"""
    os.makedirs("logs", exist_ok=True)

    logger.add(
        sink="logs/bot.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{file}:{line} {message}",
        rotation="30 day",
        retention="90 days",
        compression="zip",
        backtrace=True,
        diagnose=True,
        enqueue=True,
        catch=True,
        level="DEBUG",
    )

    logger.success("Logger initialized")


def register_all_middlewares(dp: Dispatcher):
    """Register all middlewares"""
    dp.setup_middleware(ThrottlingMiddleware())
    dp.setup_middleware(DbMiddleware())
    dp.setup_middleware(TranslationMiddleware())


def register_all_filters(dp: Dispatcher):
    """Register all filters"""
    dp.filters_factory.bind(role.AdminFilter)
    dp.filters_factory.bind(reply_kb.CloseBtn)


def register_all_handlers(dp: Dispatcher):
    """Register all handlers"""
    register_admin(dp)
    register_manage_chat(dp)
    register_user(dp)
    register_student(dp)
    register_payment(dp)


async def set_bot_commands(bot: Bot):
    """Initialize bot commands for bot to preview them when typing slash \"/\""""
    commands = [
        BotCommand(command="start", description="Botni qayta ishga tushirish"),
        # BotCommand(command="weather", description="Ob-havo ma'lumotlari qidirish guruhda ishlaydi (NAMUNA: /weather Toshkent)"),
        # BotCommand(command="me", description="Your info in DB"),
        # BotCommand(command="phone", description="Add / Update phone number"),
        # BotCommand(command="lang", description="Choose language"),
        BotCommand(command="help", description="Yordam"),
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())


async def on_startup(dp: Dispatcher):
    """Startup function"""
    init_logger()
    logger.success("Starting the bot...")
    logger.success("Postgres database is used" if config.tg_bot.use_db else "SQLite database is used")

    if config.tg_bot.use_redis:
        # use redis storage for FSM
        storage = RedisStorage2(host=config.tg_bot.redis_host,
                                port=config.tg_bot.redis_port,
                                db=config.tg_bot.redis_db,
                                password=config.tg_bot.redis_password,
                                prefix=config.tg_bot.redis_prefix)
    else:
        # use memory storage for FSM
        storage = MemoryStorage()

    dp.storage = storage

    # adding config and db session to bot data
    bot['config'] = config
    bot['db'] = await create_db_session(config)

    register_all_middlewares(dp)
    register_all_filters(dp)
    register_all_handlers(dp)

    await set_bot_commands(bot)

    if config.tg_bot.use_webhook:
        WEBHOOK_HOST = f"{config.webhook.host}:{config.webhook.port}"
        WEBHOOK_URL = f"{WEBHOOK_HOST}/{config.webhook.path.strip('/')}"
        webhook_info = await bot.get_webhook_info()

        if webhook_info.url != WEBHOOK_URL:
            logger.info("Setting webhook...")
            await bot.set_webhook(WEBHOOK_URL)
    logger.success("Bot started!")

    # notify admins that bot has been started
    for admin in config.tg_bot.admins_id:
        try:
            await dp.bot.send_message(admin, "Bot started")
        except Exception as e:
            logger.exception(e)


async def on_shutdown(dp: Dispatcher):
    """Shutdown function"""
    logger.success("Stopping the bot...")
    if config.tg_bot.use_webhook:
        await dp.bot.delete_webhook()

    await dp.storage.close()
    await dp.storage.wait_closed()
    await dp.bot.session.close()
    logger.success("Bot stopped!")


if __name__ == "__main__":
    if config.tg_bot.use_webhook:
        logger.info("Bot is running in webhook mode")
        start_webhook(
            dispatcher=dp,
            webhook_path=config.webhook.path,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=config.tg_bot.skip_updates,
            host=config.webhook.webapp_host,
            port=config.webhook.webapp_port,
        )
    else:
        logger.info("Bot is running in polling mode")
        start_polling(
            dispatcher=dp,
            skip_updates=config.tg_bot.skip_updates,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
        )
