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
        # pprint(data)
        # print('---', '\n')

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
                } if i['type'] != 'reference' else {
                    'name': i['name'],
                    'file': i['file'],
                    'type': i['type'],
                    'data': i['attributes']
                    # 'link': i['link']
                }
                for i in data['documents'] if i['type'] not in ['decree']
            ]
        }

        # add reference

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
    document = next((doc for doc in reversed(student_info['documents']) if doc['type'] == type), None)
    if not document:
        return None

    name = document['name']
    url = document['link'] if type != 'reference' else document['file']
    if not name or not url:
        return None

    # print('url', url)
    file_name = f'{name}.pdf' if type == 'reference' else f'{name}-{student_info["hemis_id"]}.pdf'
    print('file_name', file_name)
    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer r9E1eEhFPM41R9-2dGq1ZWAsgfKzH2OE' if type != 'reference' else
        'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJ2MVwvYXV0aFwvbG9naW4iLCJhdWQiOiJ2MVwvYXV0aFwvbG9naW4iLCJleHAiOjE3MjIwNjIwNzYsImp0aSI6IjQ2MjIyMTEwMTE0NyIsInN1YiI6IjExNTEifQ.Ywlv9boM-kAmwPWq8W8MCCVVQD5pQZ1nn_rzp3bRJ54'
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        file_path = os.path.join('tgbot/misc/files/', file_name)
        with open(file_path, 'wb') as file:
            file.write(response.content)
        return file_path

    return None


def get_reference(link: str):
    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJ2MVwvYXV0aFwvbG9naW4iLCJhdWQiOiJ2MVwvYXV0aFwvbG9naW4iLCJleHAiOjE3MjIwNjIwNzYsImp0aSI6IjQ2MjIyMTEwMTE0NyIsInN1YiI6IjExNTEifQ.Ywlv9boM-kAmwPWq8W8MCCVVQD5pQZ1nn_rzp3bRJ54'
    }

    response = requests.get(link, headers=headers)
    print('response', response)

    if response.status_code == 200:
        # response return pdf file
        # with open(file_name, 'wb') as file:
        with open('files/reference.pdf', 'wb') as file:
            file.write(response.content)

        return 'tgbot/misc/files/reference.pdf'


# get student data by hemis id, fullname, image
def get_student_data():
    """
    Fetch student data from paginated API and return a list of students.
    """
    url = 'https://student.niiedu.uz/rest/v1/data/student-list'
    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer r9E1eEhFPM41R9-2dGq1ZWAsgfKzH2OE'
    }

    # Initialize parameters for pagination
    params = {
        # 'page': 1,  # Start with the first page
        'page': 401,  # Start with the first page
        'limit': 20  # Number of items per page (adjustable)
    }

    student_list = []

    while True:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            items = data['data']['items']

            # Extract full_name, student_id_number, and image from each item
            for item in items:
                student_info = {
                    "full_name": item["full_name"],
                    "student_id_number": item["student_id_number"],
                    "image": item["image"]
                }
                student_list.append(student_info)

            # Get totalCount and pageCount from the response
            total_count = data.get('totalCount', 0)
            page_count = data.get('pageCount', 0)
            # print('pageCount', page_count)
            current_page = params['page']

            # If we are on the last page, break the loop
            # if in 3 page break

            print('current_page', current_page)
            # if current_page >= 3:
            #     print('break on 3 page')
            #     break

            if current_page >= 479:
                print('break on 479 page')
                with open(f'student_list_{current_page}.csv', 'w') as f:
                    f.write('full_name,student_id_number,image\n')
                    for student in student_list:
                        f.write(f"{student['full_name']},{student['student_id_number']},{student['image']}\
                         \n")
                break

            # Increment the page number for the next request
            # print(f"Fetching page {params['page'] + 1}")
            params['page'] += 1

            # every 100 Write the list of students to a file.csv
            if current_page % 100 == 0:
                print('Write to file', current_page)
                with open(f'student_list_{current_page}.csv', 'w') as f:
                    f.write('full_name,student_id_number,image\n')
                    for student in student_list:
                        f.write(f"{student['full_name']},{student['student_id_number']},{student['image']}\
                        \n")

                # empty the list
                student_list = []

        else:
            print(f"Error fetching data: {response.status_code}")
            break

    # Display the list of students
    pprint(student_list)

    return student_list


# Call the function to get student data

if __name__ == '__main__':
    # foo = (get_student_data_by_hemis_id('462231100931'))
    # foo = (get_student_data_by_hemis_id('462221100016'))
    foo = (get_student_data_by_hemis_id('462221101147'))
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

    # bar = get_docs(foo, 'academic_data')
    # bar = get_docs(foo, 'reference')
    bar = get_docs(foo)

    # reference
    # bar = get_reference(foo['documents'][-1]['file'])
    print(bar)

    print('---')
    # get_student_data()
