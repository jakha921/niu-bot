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


if __name__ == '__main__':
    print(get_contract_link('AA7652863'))
