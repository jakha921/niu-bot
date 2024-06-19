import os
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
            'documents': [
                {
                    'name': i['name'],
                    'file': i['file'],
                    'type': i['type'],
                    'data': i['attributes'],
                    'link': i['link']
                }
                for i in data['documents'] if i['type'] not in ['reference', 'decree']
            ]
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

    # print('unix time ', from_now, to_now)

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


def get_docs(student_info: str, type: str = 'call-sheet'):
    name = [i['name'] for i in student_info['documents'] if i['type'] == type][0] if [i['name'] for i in student_info['documents'] if i['type'] == type] else None
    url = [i['link'] for i in student_info['documents'] if i['type'] == type][0] if [i['link'] for i in student_info['documents'] if i['type'] == type] else None
    print('url', url)

    if name and url:
        file_name = f'{name}.pdf' if type == 'reference' else f'{name}-{student_info["hemis_id"]}.pdf'
        print('file_name', file_name)

        headers = {
            'accept': 'application/json',
            'Authorization': 'Bearer r9E1eEhFPM41R9-2dGq1ZWAsgfKzH2OE'
        }
        response = requests.get(url, headers=headers)
        # print('response', response)

        if response.status_code == 200:
            # response return pdf file
            # with open(file_name, 'wb') as file:
            with open(os.path.join('tgbot/misc/files/', file_name), 'wb') as file:
                file.write(response.content)

            return os.path.join('tgbot/misc/files/', file_name)
    return None


if __name__ == '__main__':
    # foo = (get_student_data_by_hemis_id('462231100931'))
    foo = (get_student_data_by_hemis_id('462221100016'))
    pprint(foo)
    print('---')
    # bar = get_student_schedule_by_hemis_id('462221100016')
    # pprint(bar)

    # academic_data = 'https://student.niiedu.uz/rest/v1/data/student-info-download?student_id_number=462231100103&id=32236&type=academic_data'
    # academic_sheet = 'https://student.niiedu.uz/rest/v1/data/student-info-download?student_id_number=462231100103&id=32236&type=academic_sheet'
    # call_sheet = 'https://student.niiedu.uz/rest/v1/data/student-info-download?student_id_number=462231100103&id=1815&type=call-sheet'
    # call_sheet = 'https://student.niiedu.uz/rest/v1/student/document-download?id=9694&type=call-sheet'

    # call_sheet = [i['file'] for i in foo['documents'] if i['type'] == 'call-sheet'][0]
    # print('call_sheet', call_sheet)

    bar = get_docs(foo, 'academic_data')
    print(bar)
