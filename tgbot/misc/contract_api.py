from pprint import pprint

import requests


def get_contract_link(passport_data: str):
    """{
    "data": [
        {
            "name": "2 tomonlama",
            "types": [
                {
                    "name": "Stipendiyasiz",
                    "url": "http://marketing.niuedu.uz/student/download-agreement?code=MzAyOSYxJjI="
                }
            ]
        },
        {
            "name": "3 tomonlama",
            "types": [
                {
                    "name": "Stipendiyasiz",
                    "url": "http://marketing.niuedu.uz/student/download-agreement?code=MzAyOSYyJjI="
                }
            ]
        }
    ]}"""
    url = f'http://marketing.niuedu.uz/student/get-side-types?passport={passport_data}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        dict_of_links = {
            2: data['data'][0]['types'][0]['url'],
            3: data['data'][1]['types'][0]['url']
        }
        return dict_of_links

    return None


def get_contract_payment_data(passport_data: str):
    """

    {
      "data": {
        "payment_history": [
          {
            "id": 15370,
            "amount": "19500000",
            "id_code": "RU-0328563/K-1/1",
            "description": "contract",
            "need_payment": null,
            "student_id": 86,
            "payment_date": "1970-01-01",
            "created_at": "2023-12-15 17:38:35",
            "updated_at": null,
            "created_by": 33,
            "updated_by": null
          }
        ],
        "payments": [
          {
            "id": 16,
            "type_id": 1,
            "agreement_type_id": 2,
            "price": "15000000",
            "created_at": "2023-06-12 20:05:56",
            "updated_at": "2023-06-12 20:05:56",
            "price_part1": null,
            "price_part2": null,
            "price_part1_word": null,
            "price_part2_word": null,
            "agreement_type": {
              "id": 2,
              "name": "Stipendiyasiz",
              "created_at": "2021-08-27 16:11:34",
              "updated_at": "2021-08-27 16:11:37"
            },
            "type": {
              "id": 1,
              "name": "Filologiya tillarini o'qitish (Rus tili)",
              "comment": "RU",
              "part1": "2023 yil 29-dekabrga qadar",
              "part2": "2024 yil 15-may"
            }
          }
        ]
      },
      "student": {
        "id": 86,
        "id_code": "RU-0328563/K-1/1",
        "last_name": "MIRZAYEV",
        "first_name": "ULUG‘BEK",
        "middle_name": "XURSHID O‘G‘LI",
        "type_student": null,
        "passport_seria": "AC",
        "passport_number": "0328563",
        "passport_jshir": "53110025360013",
        "birthday": "2002-10-31",
        "status_new": 1,
        "course": 2,
        "ball": null,
        "dir": null,
        "comment": null,
        "lang": null,
        "phone": "+998919266768",
        "edu_type_id": null,
        "region": "5",
        "address": null,
        "gender": null,
        "dtm_id": null,
        "chechked": 0,
        "status_check": 0,
        "area": "5",
        "passport_given_date": "2018-11-28",
        "passport_issued_date": null,
        "passport_given_by": null,
        "status": 1,
        "super_id": null,
        "summa": null,
        "updated_at": "2023-08-14 10:56:27",
        "created_at": "2023-07-14 10:16:59",
        "status_original": null,
        "getting_date": null,
        "sms_sended": 0,
        "faculty_id": null,
        "description": null,
        "backlog": null
      },
      "status": 1,
      "message": "success"
    }

    """
    url = f'http://marketing.niuedu.uz/student/get-payments?passport={passport_data}'

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()

        if data['status'] != 1:
            return data['message']

        text = f'📝 Kontrakt to\'lovlari:\n\n'
        text += f'<b>{data["student"]["last_name"]} {data["student"]["first_name"]} {data["student"]["middle_name"]}</b>\n'
        text += f'Passport: <b>{data["student"]["passport_seria"]} {data["student"]["passport_number"]}</b>\n\n'

        if not data['data']['payment_history']:
            text += 'Kontrakt to\'lovlari yo\'q'
        else:
            for payment in data['data']['payment_history']:
                text += '- ' * 20 + '\n'
                text += f'Summasi: <b>{payment["amount"]}</b>\n' \
                        f'Sanasi: <b>{payment["payment_date"]}</b>\n' \
                        f"To'lov maqsadi <b>{payment['description']}</b>\n"
                    # f'Bazaga qo\'yilgan sanasi: <b>{payment["created_at"]}</b>\n'
        return text

    return None


def get_credit_data(passport_data: str):
    url = f'http://marketing.niuedu.uz/student/get-credits?passport={passport_data}'

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()

        pprint('data', data)
        if data['status'] != 1:
            return data['message']

        total_credit_price = 0
        for credit in data['data']['credit_history']:
            total_credit_price += int(credit['credits'])

        text = f'📝 Kredit to\'lovlari:\n\n'
        text += f'<b>{data["student"]["last_name"]} {data["student"]["first_name"]} {data["student"]["middle_name"]}</b>\n'
        text += f'Passport: <b>{data["student"]["passport_seria"]} {data["student"]["passport_number"]}</b>\n\n'
        text += f'📝 Kredit narxilari:\n'

        for credit in data['data']['credit_price']:
            text += f'Talim shakli: <b>{credit["name"]}</b> uchun 1 kredit narxi = <b>{credit["price"]}</b>\n'

        if total_credit_price:
            text += f'\nJami qarz kredit soni: <b>{total_credit_price}</b>'
        else:
            text += '\nSizda kredit yo\'q'

        return data

    return None


if __name__ == '__main__':
    # print(get_contract_link('AA7652863'))
    foo = get_contract_payment_data('AB8056883')
    # foo = get_credit_data('AD0414879')
    pprint(foo)
