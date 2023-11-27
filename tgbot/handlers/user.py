from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.types.reply_keyboard import ReplyKeyboardRemove
from aiogram.dispatcher.handler import ctx_data

from loguru import logger

from tgbot.keyboards.inline import choose_language, cd_choose_lang
from tgbot.keyboards.reply import phone_number
from tgbot.middlewares.translate import TranslationMiddleware
from tgbot.models.models import TGUser, get_student_hemis_id
from tgbot.misc.utils import Map, find_button_text
from tgbot.services.database import AsyncSession


async def user_start(m: Message, texts: Map):
    """User start command handler"""
    logger.info(f'User {m.from_user.id} started the bot')
    text = f"Assalomu alaykum, {m.from_user.full_name}!\n\n"
    text += "Botga xush kelibsiz!\n\n" \
            "Bu bot orqalt siz o'zingizni Hemis dagi ID raqamingizni olishingiz mumkin.\n" \
            "Buning uchun siz o'zingizni passportingizni seriyasini va raqamini yuboring.\n\n" \
            "Masalan:\n" \
            "<b>AA1234567</b>\n\n"

    await m.reply(text)


async def get_user_hemis_id(msg: Message):
    """User start command handler"""
    logger.info(f'User send {msg.text} passport')
    wait = await msg.reply("Sizning passportingiz qabul qilindi. Iltimos kuting!")
    hemis_id = await get_student_hemis_id(msg.bot['db'], msg.text)
    print('hemis_id', hemis_id)
    if hemis_id:
        # delete previous message
        await wait.delete()
        await msg.reply(f"Sizning Hemis ID raqamingiz: <code>{hemis_id}</code>")
    else:
        await wait.delete()
        await msg.reply("Sizning passportingiz bazada topilmadi. Iltimos tekshirib qaytadan yuboring!")


async def user_me(m: Message, db_user: TGUser, texts: Map):
    """User me command handler"""
    logger.info(f'User {m.from_user.id} requested his info')
    await m.reply(texts.user.me.format(
        telegram_id=db_user.telegram_id,
        firstname=db_user.firstname,
        lastname=db_user.lastname,
        username=db_user.username,
        phone=db_user.phone,
        lang_code=db_user.lang_code))


async def user_close_reply_keyboard(m: Message, texts: Map):
    """User close reply keyboard button handler"""
    logger.info(f'User {m.from_user.id} closed reply keyboard')
    await m.reply(texts.user.close_reply_keyboard, reply_markup=ReplyKeyboardRemove())


async def user_phone(m: Message, texts: Map):
    """User phone command handler"""
    logger.info(f'User {m.from_user.id} requested phone number')
    await m.reply(texts.user.phone, reply_markup=await phone_number(texts))


async def user_phone_sent(m: Message, texts: Map, db_user: TGUser, db_session: AsyncSession):
    """User contact phone receiver handler"""
    logger.info(f'User {m.from_user.id} sent phone number')

    number = m.contact.phone_number

    # if number not start with +, add +
    if not number.startswith('+'):
        number = '+' + number

    # updating user's phone number
    await TGUser.update_user(db_session,
                             telegram_id=db_user.telegram_id,
                             updated_fields={'phone': number})
    await m.reply(texts.user.phone_saved, reply_markup=ReplyKeyboardRemove())


async def user_lang(m: Message, texts: Map):
    """User lang command handler"""
    logger.info(f'User {m.from_user.id} requested language')
    await m.reply(texts.user.lang, reply_markup=await choose_language(texts))


async def user_lang_choosen(cb: CallbackQuery, callback_data: dict,
                            texts: Map, db_user: TGUser, db_session: AsyncSession):
    """User lang choosen handler"""
    logger.info(f'User {cb.from_user.id} choosed language')
    code = callback_data.get('lang_code')
    await TGUser.update_user(db_session,
                             telegram_id=db_user.telegram_id,
                             updated_fields={'lang_code': code})

    # manually load translation for user with new lang_code
    texts = await TranslationMiddleware().reload_translations(cb, ctx_data.get(), code)
    btn_text = await find_button_text(cb.message.reply_markup.inline_keyboard, cb.data)
    await cb.message.edit_text(texts.user.lang_choosen.format(lang=btn_text), reply_markup='')


def register_user(dp: Dispatcher):
    dp.register_message_handler(
        user_start,
        commands=["start"],
        state="*"
    )
    dp.register_message_handler(
        get_user_hemis_id,
        regexp=r"^[A-Z]{2}\d{7}$",
        content_types=["text"],
        state="*"
    )
    dp.register_message_handler(
        user_me,
        commands=["me"],
        state="*"
    )
    dp.register_message_handler(
        user_phone,
        commands=["phone"],
        state="*"
    )
    dp.register_message_handler(
        user_lang,
        commands=["lang"],
        state="*"
    )
    dp.register_message_handler(
        user_close_reply_keyboard,
        is_close_btn=True,
        state="*"
    )
    dp.register_message_handler(
        user_phone_sent,
        content_types=["contact"],
        state="*"
    )
    dp.register_callback_query_handler(
        user_lang_choosen,
        cd_choose_lang.filter(),
        state="*",
    )
