from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from tgbot.misc.utils import Map


async def phone_number(texts: Map):
    """Phone number inline keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=texts.user.kb.reply.phone,
                            request_contact=True)],
            [KeyboardButton(text=texts.user.kb.reply.close)],
        ],
        resize_keyboard=True,
    )
    return keyboard


async def menu_keyboard():
    """
    User menu keyboards

    Talaba ID,
    Talaba shartnomasi,
    Aloqa ma'lumotlari,
    Tilni o'zgartirish,
    Pasport ma'lumotlari uzgartirish,
    Kutubxona,
    FAQ
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🆔Talaba ID"),
                KeyboardButton(text="📄Shartnoma")
            ],
            [
                KeyboardButton(text="📝Pasport ma'lumotlari uzgartirish")
            ],
            [
                # KeyboardButton(text="🌐Tilni o'zgartirish"),
                KeyboardButton(text="📚Kutubxona")
            ],
            [
                KeyboardButton(text="📞Aloqa ma'lumotlari"),
                KeyboardButton(text="❓FAQ")
            ],

        ],
        resize_keyboard=True,
    )
    return keyboard


# back keyboard
async def back_keyboard():
    """Back keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⬅️Ortga")],
        ],
        resize_keyboard=True,
    )
    return keyboard
