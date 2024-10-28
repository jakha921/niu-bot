import asyncio
import os
import re

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, InlineQuery, InlineQueryResultArticle, InputTextMessageContent, CallbackQuery
from aiogram.types.reply_keyboard import ReplyKeyboardRemove
from loguru import logger

from tgbot.keyboards.inline import menu_keyboard_inline
from tgbot.keyboards.reply import back_keyboard
from tgbot.misc.contract_api import get_contract_link, get_contract_payment_data, get_credit_data
from tgbot.misc.hemis_api import get_student_data_by_hemis_id, get_student_schedule_by_hemis_id, get_docs
from tgbot.misc.states import StudentPassport, StudentPassportChange
from tgbot.models.models import TGUser, get_list_of_books, get_student_by_passport


async def get_profile(call: CallbackQuery):
    """User start command handler"""
    logger.info(f'User send {call.data}')
    # delete inline keyboard
    # await call.message.delete()

    wait = await call.message.answer("Sizning ma'lumotlaringizni qidirilmoqda, iltimos kuting...")

    try:
        user = await TGUser.get_user(call.bot['db'], call.from_user.id)
        student = await get_student_by_passport(call.bot['db'], user.passport)

        # get image from api
        # image = get_student_data_by_hemis_id(student.hemis_id)['image']
        # print('image', type(image), image)

        text = f"<b>Sizning profil ma'lumotlaringiz:</b>\n\n" \
               f"<b>FIO:</b> {student.full_name}\n" \
               f"<b>Pasport:</b> <code>{student.passport}</code>\n" \
               f"<b>JSHSHIR:</b> <code>{student.jshshir}</code>\n" \
               f"<b>Fakultet:</b> {student.faculty}\n" \
               f"<b>Kurs:</b> {student.course.replace('-kurs', '')}\n" \
               f"<b>Guruh:</b> {student.stgroup}\n" \
               f"<b>Telegram ID:</b> <code>{user.telegram_id}</code>\n\n" \
               f"<b>Talaba ID:</b> <code>{student.hemis_id}</code>\n" \
               f"<a href='https://student.niiedu.uz/'>Hemis</a> tizimiga kirish\n\n" \
               f"Agar sizning ma'lumotlaringizda xatolik bo'lsa, " \
               f"iltimos <a href='https://t.me/nniueduuz '>admin</a> bilan bog'laning" \
 \
        # if image:
        #     await call.message.answer_photo(photo=image, caption=text)

        if student:
            # delete previous message
            await wait.delete()
            await call.message.answer(text, parse_mode='html')
            await call.message.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(call.from_user.id))
        else:
            await wait.delete()
            await call.message.answer(
                f"<b>Telegram ID:</b> <code>{user.telegram_id}</code>\n\n"
                f"Sizning pasportingiz bazada topilmadi.\n"
                f"Ma'lumotlaringizni topilmadi, iltimos <a href='https://t.me/nniueduuz'>admin</a> bilan bog'laning",
                parse_mode='html')
            await call.message.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(call.from_user.id))
    except asyncio.TimeoutError:
        await wait.delete()
        await call.message.answer("Iltimos, keyinroq urinib ko'ring yoki internet aloqasini tekshiring!")
        await call.message.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(call.from_user.id))


async def get_user_hemis_id(call: CallbackQuery):
    """User start command handler"""
    logger.info(f'User send {call.data}')
    # delete previous message
    await call.message.delete()

    wait = await call.message.answer("Iltimos kuting...")
    try:
        # Set a timeout of 5 seconds for the database queries
        user = TGUser.get_user(call.bot['db'], call.from_user.id)
        hemis_id = get_student_by_passport(call.bot['db'], user.passport)

        if hemis_id:
            # delete previous message
            await wait.delete()
            await call.message.answer(f"Sizning <b>Hemis ID</b> raqamingiz: <code>{hemis_id}</code>\n\n"
                                      f"<a href='https://student.niiedu.uz/'>Hemis</a> tizimiga kirish",
                                      parse_mode='html')
            await call.message.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(call.from_user.id))
        else:
            await wait.delete()
            await call.message.answer("Sizning pasportingiz bazada topilmadi. Iltimos tekshirib qaytadan yuboring!")
            await call.message.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(call.from_user.id))
    except asyncio.TimeoutError:
        await wait.delete()
        await call.message.answer("Iltimos, keyinroq urinib ko'ring yoki internet aloqasini tekshiring!")
        await call.message.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(call.from_user.id))


async def get_user_contract(call: CallbackQuery):
    """User start command handler"""
    logger.info(f'User send {call.data}')
    # delete inline keyboard
    await call.message.delete()

    wait = await call.message.answer("Sizning shartnomangiz qidirilmoqda, iltimos kuting...")

    try:
        user_task = TGUser.get_user(call.bot['db'], call.from_user.id)
        user = await asyncio.wait_for(user_task, timeout=5)

        contract_links = get_contract_link(user.passport)

        if contract_links:
            # delete previous message
            await wait.delete()
            await call.message.answer(f"<b>Sizning shartnomangiz:</b> \n\n"
                                      "Ko'chirib olish uchun quyidagi linklardan birini tanlang👇\n\n"
                                      f"<a href='{contract_links[2]}'>2-tomonli shartnoma</a> - talaba va universitet o'rtasidagi shartnoma\n\n"
                                      f"<a href='{contract_links[3]}'>3-tomonli shartnoma</a> - talaba, universitet va yuridik shaxs(bank) o'rtasidagi shartnoma\n\n",
                                      parse_mode='html')
            await call.message.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(call.from_user.id))

        else:
            await wait.delete()
            await call.message.answer(
                f"Sizning {user.passport} pasportingiz buyicha shartnoma topilmadi. Iltimos tekshirib qaytadan yuboring!")
            await call.message.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(call.from_user.id))
    except asyncio.TimeoutError:
        await wait.delete()
        await call.message.answer(
            "Bazaga so'rov uzun muddat ichida javob qaytarmadi. Iltimos, keyinroq urinib ko'ring.")
        await call.message.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(call.from_user.id))


async def back_to_menu(msg: Message):
    """User start command handler"""
    logger.info(f'User send {msg.text}')

    # remove reply keyboard
    await msg.answer("Bekor qilindi", reply_markup=ReplyKeyboardRemove())
    await msg.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(msg.from_user.id))


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

    text = f"<b>Telefon raqam:</b> <code>+998 55 500 00 43</code>\n" \
           f"<b>Sayt:</b> <a href='https://niuedu.uz'>niuedu.uz</a>\n" \
           f"<b>E-mail:</b> info@niuedu.uz\n" \
           f"<b>Manzil:</b> Navoiy viloyati Karmana tumani Toshkent ko'chasi 39-uy\n" \
           f"<b>Telegram:</b> @niuedu_uz\n" \
           f"<b>Instagram:</b> <a href='https://instagram.com/niuedu.uz'>niuedu.uz</a>\n\n" \
           f"<b>Hemis:</b> <a href='https://student.niiedu.uz/'>student.niiedu.uz</a>\n"
    # send location
    await call.message.answer_location(40.14868330039444, 65.35709196263187)
    await call.message.answer(text, parse_mode='html')
    await call.message.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(call.from_user.id))


async def get_faq(call: CallbackQuery):
    """User start command handler"""
    logger.info(f'User send {call.data}')
    # delete previous message
    await call.message.delete()

    # https://telegra.ph/Tez-Tez-Soraluvchi-Savollar-11-13 - FAQ send as article
    await call.message.answer(
        "<a href='https://telegra.ph/Tez-Tez-Soraluvchi-Savollar-12-18'>Tez-Tez Soraluvchi Savollar</a>",
        parse_mode='html')
    await call.message.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(call.from_user.id))


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
                      f"Xavola: {book[9] if book[9] else 'Elektron versiya topilmadi, kitobni olish uchun kutibxonaga murojaat qiling'}\n"

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


async def get_contract_payment(call: CallbackQuery):
    """User start command handler"""
    logger.info(f'User send {call.data}')
    # delete inline keyboard
    await call.message.delete()

    wait = await call.message.answer("Sizning to'lovlar ma'lumotlaringiz qidirilmoqda, iltimos kuting...")

    try:
        user_task = TGUser.get_user(call.bot['db'], call.from_user.id)
        user = await asyncio.wait_for(user_task, timeout=5)

        contract_payment = get_contract_payment_data(user.passport)

        contract_payment += f"\n\n<b>Malumot olish uchun:</b> +998 79 222 02 00 (107) raqamiga murojaat qiling"

        if contract_payment:
            # delete previous message
            await wait.delete()
            await call.message.answer(contract_payment, parse_mode='html')
            await call.message.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(call.from_user.id))
        else:
            await wait.delete()
            await call.message.answer(
                f"Sizning {user.passport} pasportingiz buyicha shartnoma topilmadi. Iltimos tekshirib qaytadan yuboring!")
            await call.message.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(call.from_user.id))
    except asyncio.TimeoutError:
        await wait.delete()
        await call.message.answer(
            "Bazaga so'rov uzun muddat ichida javob qaytarmadi. Iltimos, keyinroq urinib ko'ring.")
        await call.message.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(call.from_user.id))


async def get_telegram_id(call: CallbackQuery):
    """User start command handler"""
    logger.info(f'User send {call.data}')
    # delete inline keyboard
    await call.message.delete()

    await call.message.answer(f"<b>Sizning Telegram ID:</b> <code>{call.from_user.id}</code>", parse_mode='html')
    await call.message.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(call.from_user.id))


async def set_user_passport(call: CallbackQuery):
    """User start command handler"""
    logger.info(f'User send {call.data}')
    # delete inline keyboard
    await call.message.delete()

    await StudentPassportChange.telegram_id.set()
    await call.message.answer("Foydalanuvchi telegram ID raqamini yuboring", reply_markup=await back_keyboard())


async def set_telegram_id(msg: Message, state: FSMContext):
    """Bot help handler"""
    logger.info(f'User {msg.from_user.id} send {msg.text} telegram id')

    # Check to cancel
    if msg.text == '⬅️Ortga':
        # delete previous message
        await msg.delete()
        await msg.answer("Bekor qilindi", reply_markup=ReplyKeyboardRemove())
        await msg.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(msg.from_user.id))
        await state.finish()
        return

    # Check telegram id
    if not msg.text.isdigit():
        await msg.answer("Telegram ID raqamini noto'g'ri kiritildi. Iltimos tekshirib qaytadan yuboring!")
        return

    if not await TGUser.get_user(msg.bot['db'], msg.from_user.id):
        await msg.answer("Foydalanuvchi bazada topilmadi!")
        return

    # Save telegram id
    await state.update_data(telegram_id=msg.text)

    await StudentPassportChange.passport.set()
    await msg.answer("Pasport ma'lumotlarini yuboring")


async def set_passport(msg: Message, state: FSMContext):
    """Bot help handler"""
    logger.info(f'User {msg.from_user.id} send {msg.text} passport data')

    # Check to cancel
    if msg.text == '⬅️Ortga':
        # delete previous message
        await msg.delete()
        await msg.answer("Bekor qilindi", reply_markup=ReplyKeyboardRemove())
        await msg.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(msg.from_user.id))
        await state.finish()
        return

    # Check passport
    if not re.match(r'[A-Z]{2}\d{7}', msg.text):
        await msg.answer("Pasport malumotlari noto'g'ri kiritildi. Iltimos tekshirib qaytadan yuboring!")
        return

    # Update user passport in DB
    get_data = await state.get_data()
    telegram_id = get_data.get('telegram_id')

    # Update user passport in DB
    await TGUser.update_user(msg.bot['db'], int(telegram_id), {'passport': msg.text})

    # Finish conversation
    await state.finish()
    await msg.answer("Foydalanuvchi pasport ma'lumotlari muvaffaqiyatli saqlandi!")
    await msg.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(msg.from_user.id))


async def get_credit(call: CallbackQuery):
    """
    User get credit data
    """
    logger.info(f'User send {call.data}')
    # delete inline keyboard
    await call.message.delete()

    wait = await call.message.answer("Sizning kredit ma'lumotlaringiz qidirilmoqda, iltimos kuting...")

    try:
        user_task = TGUser.get_user(call.bot['db'], call.from_user.id)
        user = await asyncio.wait_for(user_task, timeout=5)

        credit_data = get_credit_data(user.passport)

        if credit_data:
            # delete previous message
            await wait.delete()
            await call.message.answer(credit_data, parse_mode='html')
            await call.message.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(call.from_user.id))
        else:
            await wait.delete()
            await call.message.answer(
                f"Sizning {user.passport} pasportingiz buyicha kredit ma'lumotlari topilmadi. Iltimos tekshirib qaytadan yuboring!")
            await call.message.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(call.from_user.id))
    except asyncio.TimeoutError:
        await wait.delete()
        await call.message.answer(
            "Bazaga so'rov uzun muddat ichida javob qaytarmadi. Iltimos, keyinroq urinib ko'ring.")
        await call.message.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(call.from_user.id))


async def get_schedule(call: CallbackQuery):
    """
    User get schedule data
    """
    logger.info(f'User send {call.data}')
    # delete inline keyboard
    await call.message.delete()

    wait = await call.message.answer("Sizning dars jadvalingiz qidirilmoqda, iltimos kuting...")

    try:
        user_task = TGUser.get_user(call.bot['db'], call.from_user.id)
        user = await asyncio.wait_for(user_task, timeout=5)

        student = await get_student_by_passport(call.bot['db'], user.passport)

        schedule = get_student_schedule_by_hemis_id(student.hemis_id)
        # print('schedule', schedule)

        if schedule:
            # delete previous message
            await wait.delete()
            await call.message.answer(schedule, parse_mode='html')
            await call.message.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(call.from_user.id))
        else:
            await wait.delete()
            await call.message.answer(
                f"Sizning {user.passport} pasportingiz buyicha dars jadvali topilmadi. Iltimos tekshirib qaytadan yuboring!")
            await call.message.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(call.from_user.id))
    except asyncio.TimeoutError:
        await wait.delete()
        await call.message.answer(
            "Bazaga so'rov uzun muddat ichida javob qaytarmadi. Iltimos, keyinroq urinib ko'ring.")
        await call.message.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(call.from_user.id))


async def get_call_sheet(call: CallbackQuery):
    """
    User get call sheet data
    """
    logger.info(f'User send {call.data}')
    # delete inline keyboard
    await call.message.delete()

    wait = await call.message.answer("Sizning chaqiruv varaqangiz qidirilmoqda, iltimos kuting...")

    try:
        user_task = TGUser.get_user(call.bot['db'], call.from_user.id)
        user = await asyncio.wait_for(user_task, timeout=5)

        student = await get_student_by_passport(call.bot['db'], user.passport)

        hemis_data = get_student_data_by_hemis_id(student.hemis_id)
        link_to_call_sheet = get_docs(hemis_data, type='call-sheet')
        # link_to_call_sheet = get_docs(hemis_data, type='academic_data')
        print('link_to_call_sheet', link_to_call_sheet)

        if link_to_call_sheet:
            # delete previous message
            await wait.delete()

            # send call sheet file
            with open(link_to_call_sheet, 'rb') as file:
                await call.message.answer_document(file, caption=f"{student.full_name} chaqiruv varaqasi")

            # delete file
            os.remove(link_to_call_sheet)

            await call.message.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(call.from_user.id))
        else:
            await wait.delete()
            await call.message.answer(
                f"Sizni chaqiruv varaqasi topilmadi. Iltimos tekshirib qaytadan yuboring!")
            await call.message.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(call.from_user.id))
    except asyncio.TimeoutError:
        await wait.delete()
        await call.message.answer(
            "Bazaga so'rov uzun muddat ichida javob qaytarmadi. Iltimos, keyinroq urinib ko'ring.")
        await call.message.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(call.from_user.id))


async def get_academic_data(call: CallbackQuery):
    """
    User get academic data data
    """
    logger.info(f'User send {call.data}')
    # delete inline keyboard
    await call.message.delete()

    wait = await call.message.answer("Sizning reyting daftarchangiz qidirilmoqda, iltimos kuting...")

    try:
        user_task = TGUser.get_user(call.bot['db'], call.from_user.id)
        user = await asyncio.wait_for(user_task, timeout=5)

        student = await get_student_by_passport(call.bot['db'], user.passport)

        hemis_data = get_student_data_by_hemis_id(student.hemis_id)
        link_to_call_sheet = get_docs(hemis_data, type='academic_data')
        # link_to_call_sheet = get_docs(hemis_data, type='academic_data')
        print('link_to_call_sheet', link_to_call_sheet)

        if link_to_call_sheet:
            # delete previous message
            await wait.delete()

            # send call sheet file
            with open(link_to_call_sheet, 'rb') as file:
                await call.message.answer_document(file, caption=f"{student.full_name} reyting daftarchasi")

            # delete file
            os.remove(link_to_call_sheet)

            await call.message.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(call.from_user.id))
        else:
            await wait.delete()
            await call.message.answer(
                f"Sizni reyting daftarchasi topilmadi. Iltimos tekshirib qaytadan yuboring!")
            await call.message.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(call.from_user.id))
    except asyncio.TimeoutError:
        await wait.delete()
        await call.message.answer(
            "Bazaga so'rov uzun muddat ichida javob qaytarmadi. Iltimos, keyinroq urinib ko'ring.")
        await call.message.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(call.from_user.id))


async def get_academic_sheet(call: CallbackQuery):
    """
    User get academic sheet data
    """
    logger.info(f'User send {call.data}')
    # delete inline keyboard
    await call.message.delete()

    wait = await call.message.answer("Sizning o'quv varaqangiz qidirilmoqda, iltimos kuting...")

    try:
        user_task = TGUser.get_user(call.bot['db'], call.from_user.id)
        user = await asyncio.wait_for(user_task, timeout=5)

        student = await get_student_by_passport(call.bot['db'], user.passport)

        hemis_data = get_student_data_by_hemis_id(student.hemis_id)
        link_to_call_sheet = get_docs(hemis_data, type='academic_sheet')
        # link_to_call_sheet = get_docs(hemis_data, type='academic_data')
        print('link_to_call_sheet', link_to_call_sheet)

        if link_to_call_sheet:
            # delete previous message
            await wait.delete()

            # send call sheet file
            with open(link_to_call_sheet, 'rb') as file:
                await call.message.answer_document(file, caption=f"{student.full_name} o'quv varaqasi")

            # delete file
            os.remove(link_to_call_sheet)

            await call.message.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(call.from_user.id))
        else:
            await wait.delete()
            await call.message.answer(
                f"Sizni o'quv varaqasi topilmadi. Iltimos tekshirib qaytadan yuboring!")
            await call.message.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(call.from_user.id))
    except asyncio.TimeoutError:
        await wait.delete()
        await call.message.answer(
            "Bazaga so'rov uzun muddat ichida javob qaytarmadi. Iltimos, keyinroq urinib ko'ring.")
        await call.message.answer("Bosh menyu", reply_markup=await menu_keyboard_inline(call.from_user.id))


def register_student(dp: Dispatcher):
    dp.register_callback_query_handler(
        get_profile,
        text="profile",
        state="*"
    )
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
    dp.register_callback_query_handler(
        get_contract_payment,
        text="contract_payment",
        state="*"
    )
    dp.register_callback_query_handler(
        get_telegram_id,
        text="telegram_id",
        state="*"
    )
    dp.register_callback_query_handler(
        set_user_passport,
        text="user_passport",
        state="*"
    )
    dp.register_callback_query_handler(
        get_credit,
        text="credit",
        state="*"
    )
    dp.register_callback_query_handler(
        get_schedule,
        text="schedule",
        state="*"
    )
    dp.register_callback_query_handler(
        get_call_sheet,
        text="call-sheet",
        state="*"
    )
    dp.register_callback_query_handler(
        get_academic_data,
        text="academic_data",
        state="*"
    )
    dp.register_callback_query_handler(
        get_academic_sheet,
        text="academic_sheet",
        state="*"
    )
    dp.register_message_handler(
        set_telegram_id,
        state=StudentPassportChange.telegram_id
    )
    dp.register_message_handler(
        set_passport,
        state=StudentPassportChange.passport
    )
    dp.register_inline_handler(inline_query_handler)
