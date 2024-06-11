from datetime import datetime, timedelta
from pprint import pprint

import requests


def get_student_data_by_hemis_id(hemis_id: str):
    """
      'https://student.niiedu.uz/rest/v1/data/student-list?search=462221100016' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer r9E1eEhFPM41R9-2dGq1ZWAsgfKzH2OE'
    """
    # url = f'https://student.niiedu.uz/rest/v1/data/student-list?search={hemis_id}'
    url = f'https://student.niiedu.uz/rest/v1/data/student-info?student_id_number={hemis_id}'
    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer r9E1eEhFPM41R9-2dGq1ZWAsgfKzH2OE'
    }
    response = requests.get(url, headers=headers)
    # print('response', response)
    if response.status_code == 200:
        data = response.json()['data']

        dict_of_links = {
            'hemis_id': data['student_id_number'],
            'full_name': data['full_name'],
            'image': data['image'],
            'avg_gpa': data['avg_gpa'],
            'course': data['level']['name'],
            'semester': {
                'name': data['semester']['name'],
                'code': data['semester']['code']
            },
            'group': {
                'name': data['group']['name'],
                'code': data['group']['id']
            },
            'department': {
                'name': data['department']['name'],
                'code': data['department']['code']
            },
            'district': {
                'name': data['district']['name'],
                'code': data['district']['code']
            },
            # O'quv varaqa
            'academic_sheet': {
                'file': data['documents'][0]['file'],
                'link': data['documents'][0]['link'],
                'name': data['documents'][0]['name'],
            },
            # Reyting daftarchasi
            'academic_data': {
                'file': data['documents'][1]['file'],
                'link': data['documents'][1]['link'],
                'name': data['documents'][1]['name'],
            },
            # Chaqiruv qog'ozi
            'call-sheet': {
                'file': data['documents'][2]['file'],
                'link': data['documents'][2]['link'],
                'name': data['documents'][2]['name'],
            },
            # Ma'lumotnomalar
            'reference': {
                'file': data['documents'][3]['file'],
                'name': data['documents'][3]['name'],
            },
        }

        # pprint(data)

        return dict_of_links

    return None


def get_student_schedule_by_hemis_id(hemis_id: str):
    """
    'https://student.niiedu.uz/rest/v1/data/schedule-list?_group=410&lesson_date_from=1717959600&lesson_date_to=1718045999' \
    -H 'accept: application/json' \
    -H 'Authorization: Bearer r9E1eEhFPM41R9-2dGq1ZWAsgfKzH2OE'
    """

    student = get_student_data_by_hemis_id(hemis_id)
    group_id = student['group']['code']

    # GMT time zone +5 hours
    from_now = datetime.utcnow().combine(datetime.utcnow(), datetime.min.time()) + timedelta(hours=5)
    to_now = datetime.utcnow().combine(datetime.utcnow(), datetime.max.time()) + timedelta(hours=5)

    # unix time
    from_now = int(from_now.timestamp())
    to_now = int(to_now.timestamp())

    print('unix time ', from_now, to_now)

    url = f'https://student.niiedu.uz/rest/v1/data/schedule-list?_group={group_id}&lesson_date_from={from_now}&lesson_date_to={to_now}'
    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer r9E1eEhFPM41R9-2dGq1ZWAsgfKzH2OE'
    }

    response = requests.get(url, headers=headers)
    # print('response', response)
    if response.status_code == 200:
        data = response.json()['data']['items']

        # lessons_list = [
        #     {
        #         'pair': i['lessonPair']['name'],
        #         'subject': i['subject']['name'],
        #         'auditory': i['auditorium']['name'],
        #         'lesson_type': i['trainingType']['name'],
        #         'teacher': i['employee']['name'],
        #         'start_time': i['lessonPair']['start_time'],
        #         'end_time': i['lessonPair']['end_time']
        #     }
        #     for i in data
        # ]

        # pprint(data)

        if data:
            text = f"📅 <b>{student['group']['name']}</b> guruh dars jadvali <b>{datetime.now().date().strftime('%d.%m.%Y')}</b> sanaga:\n\n"

            for i in data:
                text += '-' * 30 + '\n'
                text += f"🏢 Xona <b>{i['auditorium']['name']}</b>\n"
                text += f"📚 <b>{i['lessonPair']['name']}. {i['subject']['name']}</b> | {i['trainingType']['name']}\n"
                text += f"🕒 {i['lessonPair']['start_time']} - {i['lessonPair']['end_time']}\n"
                text += f"👨‍🏫 Ustoz <b>{i['employee']['name']}</b>\n\n"

            # add lesson date
            # lessons_list.insert(0, datetime.now().date().strftime('%d.%m.%Y'))

            return text
        else:
            return f"📅 {student['group']['name']} guruh dars jadvali {datetime.now().date().strftime('%d.%m.%Y')} sanasida mavjud emas!"

    return None


def get_docs(url: str):
    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer r9E1eEhFPM41R9-2dGq1ZWAsgfKzH2OE'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print('response', response)

        # response return pdf file
        with open('academic_data.pdf', 'wb') as file:
            file.write(response.content)

        return 'files/academic_data.pdf'
    return None


if __name__ == '__main__':
    foo = (get_student_data_by_hemis_id('462231100103'))
    # foo = (get_student_data_by_hemis_id('462221100016'))
    pprint(foo)
    print('---')
    bar = get_student_schedule_by_hemis_id('462221100016')
    pprint(bar)

    academic_data = 'https://student.niiedu.uz/rest/v1/data/student-info-download?student_id_number=462231100103&id=32236&type=academic_data'
    academic_sheet = 'https://student.niiedu.uz/rest/v1/data/student-info-download?student_id_number=462231100103&id=32236&type=academic_sheet'
    call_sheet = 'https://student.niiedu.uz/rest/v1/data/student-info-download?student_id_number=462231100103&id=1815&type=call-sheet'

    # bar = get_docs(call_sheet)
    # print(bar)
