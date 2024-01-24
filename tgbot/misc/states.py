from aiogram.dispatcher.filters.state import State, StatesGroup


# Coming soon...
class StudentPassport(StatesGroup):
    passport = State()


class StudentPassportChange(StatesGroup):
    telegram_id = State()
    passport = State()
