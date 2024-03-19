import re

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.handler import ctx_data
from aiogram.types import Message, CallbackQuery
from aiogram.types.reply_keyboard import ReplyKeyboardRemove
from loguru import logger

from tgbot.keyboards.inline import choose_language, cd_choose_lang, menu_keyboard_inline
from tgbot.keyboards.reply import phone_number
from tgbot.middlewares.translate import TranslationMiddleware
from tgbot.misc.states import StudentPassport
from tgbot.misc.utils import Map, find_button_text
from tgbot.models.models import TGUser
from tgbot.services.database import AsyncSession


async def user_start(m: Message, texts: Map):
    """User start command handler"""
    logger.info(f'User {m.from_user.id} started the bot')
    text = f"🚀 Assalomu Aleykum , {m.from_user.full_name}!\n\n"

    text += "Botning Asosiy xususiyati:\n\n" \
            "📝 Talaba pasport ma'lumotlarini bazaga saqlaydi\n\n" \
            "va sizga quyidagi imkoniyatlarni beradi:\n\n" \
            "https://www.youtube.com/watch?v=XY0q-JJruk0"
            # "<b>🆔 Talaba ID</b> - Talabani <b>Hemis</b> tizimiga kirish uchun kerak bo'ladigan <b>ID</b> raqami ni beradi\n\n" \
            # "<b>📄 Shartnoma</b> - Kontrakt shartnomangizni olishingiz mumkin\n\n" \
            # "<b>📚 Kutubxona</b> - NIU kutubxonasidagi bor kitoblarni izlash uchun kerak bo'ladigan bo'lim\n\n" \
            # "<b>📞 Aloqa ma'lumotlari</b> - Biz bilan bog'lanish va kontakt ma'lumotlari olish mumkin\n\n" \
            # "<b>❓ FAQ</b> - Tez-tez so'raladigan savollar va ularning javoblari\n\n" \
            # "<b>💰Kontrakt to'lovilari</b> - Kontrakt to'lovlarini tekshirish uchun kerak bo'ladigan bo'lim\n\n" \
            # "<b>🆔 Telegram ID</b> - Sizning telegram ID raqamingizni ko'rsatadi\n\n" \

        # "<b>📝 Pasport ma'lumotlari uzgartirish</b> - Agar pasportingizda o'zgarish bo'lsa uni yangilash uchun kerak bo'ladigan bo'lim\n\n" \

    # Check if user already exists passport in DB
    print('user id', m.from_user.id)
    user = await TGUser.get_user(m.bot['db'], m.from_user.id)
    print('user', user.passport)
    if user.passport is None:
        await m.answer(text)
        text = f"Uzingizni pasportingizni yuboring " \
               f"masalan: <b><i>(AA1234567)</i></b> va bot sizga hismat ko'rsatadi!"
        await m.answer(text)
        await StudentPassport.passport.set()
    else:
        msg = f"📝 Sizning pasportingiz bazada saqlangan!\n\n" \
                f"bot sizga quyidagi imkoniyatlarni beradi:\n\n" \
                "https://www.youtube.com/watch?v=XY0q-JJruk0"
        await m.answer(msg)
        await m.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(m.from_user.id))
        return


async def get_passport_from_user(msg: Message, state: FSMContext):
    """Bot help handler"""
    logger.info(f'User {msg.from_user.id} send {msg.text} passport data')

    # Check to cancel
    if msg.text == '⬅️Ortga':
        # delete previous message
        await msg.delete()
        await msg.answer("Pasport kiritish bekor qilindi!", reply_markup=ReplyKeyboardRemove())
        await msg.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(msg.from_user.id))
        await state.finish()
        return

    # Check passport
    if not re.match(r'[A-Z]{2}\d{7}', msg.text):
        await msg.answer("Pasport malumotlari noto'g'ri kiritildi. Iltimos tekshirib qaytadan yuboring!")
        return

    # Update user passport in DB
    await TGUser.update_user(msg.bot['db'], msg.from_user.id, {'passport': msg.text})

    # Finish conversation
    await state.finish()
    await msg.answer("Pasport muvaffaqiyatli saqlandi!")
    await msg.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(msg.from_user.id))


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


async def set_passport(msg: Message, state: FSMContext):
    """Bot help handler"""
    logger.info(f'User {msg.from_user.id} send {msg.text} passport data')

    # Check to cancel
    if msg.text == '⬅️Ortga':
        # delete previous message
        await msg.delete()
        await msg.answer("Talaba telegram ID raqamini yuboring!")
        await msg.answer("Telegram ID raqamini olish uchun quyidagi tugmani bosing",
                         reply_markup=await menu_keyboard_inline(msg.from_user.id))
        await msg.answer("Pasport kiritish bekor qilindi!", reply_markup=ReplyKeyboardRemove())
        await msg.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(msg.from_user.id))
        await state.finish()
        return

    # Check passport
    if not re.match(r'[A-Z]{2}\d{7}', msg.text):
        await msg.answer("Pasport malumotlari noto'g'ri kiritildi. Iltimos tekshirib qaytadan yuboring!")
        return

    # Update user passport in DB
    await TGUser.update_user(msg.bot['db'], msg.from_user.id, {'passport': msg.text})

    # Finish conversation
    await state.finish()
    await msg.answer("Pasport muvaffaqiyatli saqlandi!")
    await msg.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(msg.from_user.id))


def register_user(dp: Dispatcher):
    dp.register_message_handler(
        user_start,
        commands=["start"],
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
    dp.register_message_handler(
        get_passport_from_user,
        state=StudentPassport.passport,
    )
