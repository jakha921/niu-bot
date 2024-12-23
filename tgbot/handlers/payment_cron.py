from datetime import date

from aiogram import Dispatcher
from aiogram.types import Message
from loguru import logger

from tgbot.misc.marketing_api import get_payed_data, send_passport_data
from tgbot.models.models import TGUser


async def payment_sender(msg: Message):
    """User payment command handler"""
    logger.info(f'User {msg.from_user.id} requested payment')

    print('-' * 20)

    # Get all users
    users = await TGUser.get_all_users(msg.bot['db'])
    print('users len:', len(users))

    # Convert users to dict {passport: telegram_id}
    users_dict = {user.passport: user.telegram_id for user in users if user.passport}

    # users_dict = dict(list(users_dict.items())[:200])

    # add 256841597 telegram_id and AA1144022 passport
    # users_dict['AA0000332'] = 256841597
    # print('users_dict:', users_dict)
    print('users len new:', len(users_dict))


    # Get all students payments from DB
    payments = get_payed_data()

    print('-' * 20)
    print('payments len:', len(payments))

    # payments = dict(list(payments.items())[:200])
    # print('payments:', payments)
    print('payments len new:', len(payments))
    print('-' * 20)

    sent_passports = {"passport": []}
    not_sent_passports = {"passport": []}

    # Send message to all users
    for passport, telegram_id in users_dict.items():
        print('telegram_id:', telegram_id, 'passport:', passport, 'is passport in payments:', passport in payments)
        print('- ' * 30)

        if passport in payments:
            text = f'📝 <b>NIU</b> buxgalteriyasi tomonidan <b>{passport}</b> passportga qabul qilingan to\'lovlar:\n'
            for payment in payments[passport]:
                # change date format to dd.mm.yyyy
                text += '- ' * 20 + '\n'
                text += f'Summasi: <b>{payment["amount"]}</b>\n' \
                        f'Sanasi: <b>{date.strftime(date.fromisoformat(payment["payment_date"]), "%d.%m.%Y")}</b>\n'
            # print(f'{passport} text:', text)
            await msg.bot.send_message(telegram_id, text)
            logger.info(f'Payment sent to user {telegram_id}')
            sent_passports["passport"].append(passport)
            # print('-' * 20)
        else:
            # print(f'No payment for {passport}')
            not_sent_passports["passport"].append(passport)
            # print('-' * 20)

    print('sent_passports:', len(sent_passports["passport"]))
    print('not_sent_passports:', len(not_sent_passports["passport"]))

    # convert to csv
    sent_passports = '\n'.join(sent_passports["passport"])
    not_sent_passports = '\n'.join(not_sent_passports["passport"])

    # save to file
    with open(f'sent_passports_{date.today()}.csv', 'w') as file:
        file.write(sent_passports)

    with open(f'not_sent_passports_{date.today()}.csv', 'w') as file:
        file.write(not_sent_passports)

    # send csv file to admin
    await msg.answer_document(open(f'sent_passports_{date.today()}.csv', 'rb'), caption="Payment sent to users with passports:")
    await msg.answer_document(open(f'not_sent_passports_{date.today()}.csv', 'rb'), caption="No payment for users with passports:")

    print('-' * 20)
    response = send_passport_data(sent_passports)
    print('response:', response)

    # remove csv files
    if response and response.status_code == 200:
        import os
        os.remove(f'sent_passports_{date.today()}.csv')
        os.remove(f'not_sent_passports_{date.today()}.csv')


def register_payment(dp: Dispatcher):
    dp.register_message_handler(
        payment_sender,
        commands=["payment"],
        state="*",
        is_admin=True
    )
