from aiogram import Dispatcher
from aiogram.types import Message, InlineQuery, InlineQueryResultArticle, InputTextMessageContent, CallbackQuery
from aiogram.types.reply_keyboard import ReplyKeyboardRemove
from aiogram.dispatcher.handler import ctx_data

from loguru import logger

from tgbot.keyboards.inline import choose_language, cd_choose_lang, menu_keyboard_inline
from tgbot.keyboards.reply import phone_number, menu_keyboard, back_keyboard
from tgbot.middlewares.translate import TranslationMiddleware
from tgbot.misc.contract_api import get_contract_link
from tgbot.misc.states import StudentPassport
from tgbot.models.models import TGUser, get_student_hemis_id, get_list_of_books
from tgbot.misc.utils import Map, find_button_text
from tgbot.services.database import AsyncSession


async def get_user_hemis_id(call: CallbackQuery):
    """User start command handler"""
    logger.info(f'User send {call.data}')
    # delete previous message
    await call.message.delete()

    wait = await call.message.answer("Iltimos kuting...")
    user = await TGUser.get_user(call.bot['db'], call.from_user.id)
    hemis_id = await get_student_hemis_id(call.bot['db'], user.passport)
    print('hemis_id', hemis_id)
    if hemis_id:
        # delete previous message
        await wait.delete()
        await call.message.answer(f"Sizning <b>Hemis ID</b> raqamingiz: <code>{hemis_id}</code>\n\n"
                                  f"<a href='https://student.niiedu.uz/'>Hemis</a> tizimiga kirish",
                                  parse_mode='html')
        await call.message.answer("Bosh menyu", reply_markup=await menu_keyboard_inline())
    else:
        await wait.delete()
        await call.message.answer("Sizning passportingiz bazada topilmadi. Iltimos tekshirib qaytadan yuboring!")
        await call.message.answer("Bosh menyu", reply_markup=await menu_keyboard_inline())


async def get_user_contract(call: CallbackQuery):
    """User start command handler"""
    logger.info(f'User send {call.data}')
    # delete inline keyboard
    await call.message.delete()

    wait = await call.message.answer("Iltimos kuting...")
    user = await TGUser.get_user(call.bot['db'], call.from_user.id)

    contract_links = get_contract_link(user.passport)

    if contract_links:
        # delete previous message
        await wait.delete()
        await call.message.answer(f"<b>Sizning shartnomangiz:</b> \n\n"
                                  "Ko'chirib olish uchun quyidagi linklardan birini tanlang👇\n\n"
                                  f"<a href='{contract_links[2]}'>2-tomonli shartnoma</a> - talaba va universitet o'rtasidagi shartnoma\n\n"
                                  f"<a href='{contract_links[3]}'>3-tomonli shartnoma</a> - talaba, universitet va yuridik shaxs(bank) o'rtasidagi shartnoma\n\n",
                                  parse_mode='html')
        await call.message.answer("Bosh menyu", reply_markup=await menu_keyboard_inline())

    else:
        await wait.delete()
        await call.message.answer(
            f"Sizning {user.passport} passportingiz buyicha shartnoma topilmadi. Iltimos tekshirib qaytadan yuboring!")
        await call.message.answer("Bosh menyu", reply_markup=await menu_keyboard_inline())


async def back_to_menu(msg: Message):
    """User start command handler"""
    logger.info(f'User send {msg.text}')

    # remove reply keyboard
    await msg.answer("Bekor qilindi", reply_markup=ReplyKeyboardRemove())
    await msg.answer("Bosh menyu", reply_markup=await menu_keyboard_inline())


async def user_change_passport(call: CallbackQuery):
    """User start command handler"""
    logger.info(f'User send {call.data}')

    # delete previous message
    await call.message.delete()

    await StudentPassport.passport.set()
    await call.message.answer("Pasport ma'lumotlarini yuboring", reply_markup=await back_keyboard())


async def contact_us(call: CallbackQuery):
    """User start command handler"""
    logger.info(f'User send {call.data}')

    # delete previous message
    await call.message.delete()

    text = f"<b>Telefon raqam:</b> +998 55 500-00-43\n" \
           f"<b>E-mail:</b> info@niuedu.uz\n" \
           f"<b>Manzil:</b> Navoiy viloyati Karmana tumani Toshkent ko'chasi 39-uy\n" \
           f"<b>Telegram:</b> @niueduuz\n" \
           f"<b>Instagram:</b> @niu_uz\n" \
        # send location
    await call.message.answer_location(40.14868330039444, 65.35709196263187)
    await call.message.answer(text, parse_mode='html')
    await call.message.answer("Bosh menyu", reply_markup=await menu_keyboard_inline())


async def get_faq(call: CallbackQuery):
    """User start command handler"""
    logger.info(f'User send {call.data}')
    # delete previous message
    await call.message.delete()

    # https://telegra.ph/Tez-Tez-Soraluvchi-Savollar-11-13 - FAQ send as article
    await call.message.answer(
        "<a href='https://telegra.ph/Tez-Tez-Soraluvchi-Savollar-11-13'>Tez-Tez Soraluvchi Savollar</a>",
        parse_mode='html')
    await call.message.answer("Bosh menyu", reply_markup=await menu_keyboard_inline())


async def inline_query_handler(query: InlineQuery):
    logger.info(f'Received inline query: {query.query}')

    results = []
    list_of_books = await get_list_of_books(query.bot['db'])
    search_query = query.query.lower() if query.query else None

    for book in list_of_books:
        text = f"{book[1]} - {book[2]}, Nashriyot: {book[3]}\n"
        detail_text = f"Muallif: {book[1]}\n" \
                      f"Kitob nomi: {book[2]}\n" \
                      f"Nashriyot: {book[3]}\n" \
                      f"Yili: {book[4]}\n" \
                      f"Xavola: {book[9] if book[9] else 'Topilmadi'}\n"

        if search_query and (search_query in book[1].lower() or search_query in book[2].lower()):
            results.append(InlineQueryResultArticle(
                id=str(book[0]),
                title=text,
                input_message_content=InputTextMessageContent(
                    message_text=detail_text
                ),
                url=book[9]
            ))

        if search_query is None:
            results.append(InlineQueryResultArticle(
                id=str(book[0]),
                title=text,
                input_message_content=InputTextMessageContent(
                    message_text=detail_text
                ),
                url=book[9]
            ))

        if len(results) == 50:
            break

    await query.answer(results, cache_time=1)


# async def inline_handler(query: InlineQuery, msg: Message):
#     results = []
#     list_of_books = await get_list_of_books(msg.bot['db'])
#     if not list_of_books:
#         await query.answer("Kutubxona bo'sh")
#         return
#
#     for book in list_of_books:
#         if query.query.lower() in book[1].lower() or query.query.lower() in book[2].lower():
#             results.append(InlineQueryResultArticle(
#                 id=str(book[0]),
#                 title=f"{book[1]}: {book[2]}",
#                 input_message_content=InputTextMessageContent(
#                     message_text=f"{book[1]} - {book[2]}\nСсылка: {book[9]}"
#                 ),
#                 url=book[9]
#             ))
#     await query.answer(results)


def register_student(dp: Dispatcher):
    dp.register_callback_query_handler(
        get_user_hemis_id,
        text="student_id",
        state="*"
    )
    dp.register_callback_query_handler(
        get_user_contract,
        text="contract",
        state="*"
    )
    dp.register_message_handler(
        back_to_menu,
        text="⬅️Ortga",
        state="*"
    )
    dp.register_callback_query_handler(
        user_change_passport,
        text="passport",
        state="*"
    )
    dp.register_callback_query_handler(
        contact_us,
        text="contact",
        state="*"
    )
    dp.register_callback_query_handler(
        get_faq,
        text="faq",
        state="*"
    )
    dp.register_inline_handler(inline_query_handler)
