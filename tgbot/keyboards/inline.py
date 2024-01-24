from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from tgbot.misc.utils import Map

cd_choose_lang = CallbackData("choosen_language", "lang_code")


async def choose_language(texts: Map):
    """Choose language inline keyboard"""
    # get languages from translation texts
    langs: Map = texts.user.kb.inline.languages
    keyboard = []
    for k, v in langs.items():
        keyboard.append(InlineKeyboardButton(
            v.text, callback_data=cd_choose_lang.new(lang_code=k)))
    return InlineKeyboardMarkup(
        inline_keyboard=[keyboard], row_width=len(langs.items())
    )


# convert menu_keyboard to inline_keyboard
async def menu_keyboard_inline(user_id: int):
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
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🆔Talaba ID", callback_data="student_id"),
                InlineKeyboardButton(text="📄Shartnoma", callback_data="contract")
            ],
            [
                InlineKeyboardButton(text="📚Kutubxona", switch_inline_query_current_chat="")
            ],
            [
                InlineKeyboardButton(text="💰Kontrakt to'lovilari", callback_data="contract_payment")
            ],
            [
                InlineKeyboardButton(text="🆔Telegram ID", callback_data="telegram_id"),
                # InlineKeyboardButton(text="🌐Tilni o'zgartirish", callback_data="change_language")
            ],
            [
                InlineKeyboardButton(text="📞Aloqa ma'lumotlari", callback_data="contact"),
                InlineKeyboardButton(text="❓FAQ", callback_data="faq")
            ],

        ],
        # row_width=2,
    )

    # 256841597 - Jakhongir
    # 179709417 - Guzal
    # 983432313 - Elbek
    # 1124567881 - Robiya
    # 1104388973 - Zilola
    # 6376261985 - Marjona
    # 989391636 - Shoxsanam

    print('user_id', user_id)
    if user_id in [179709417, 256841597,
                   983432313,
                   1124567881, 1104388973, 6376261985, 989391636]:
        print('admin')
        keyboard.add(InlineKeyboardButton(text="📝Pasport ma'lumotlari uzgartirish", callback_data="passport"))
        keyboard.add(InlineKeyboardButton(text="🪪Foydalanuvchi pasport ma'lumotlarini o'zgartirish",
                                          callback_data="user_passport"))

    return keyboard
