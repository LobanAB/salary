import os
import requests
from pprint import pprint

from dotenv import load_dotenv


def main():
    load_dotenv()
    superjob_api_key = os.getenv('SUPERJOB_API_KEY')
    url = 'https://api.superjob.ru/2.0/vacancies/'
    payload = {
        'catalogues': 48,
        'town': 4
    }
    headers = {'X-Api-App-Id': superjob_api_key}
    response = requests.get(url, headers=headers, params=payload)
    response.raise_for_status()
    #pprint(response.json()['objects'][0]['profession'])
    for vacancy in response.json()['objects']:
        print(f"{vacancy['profession']}, {vacancy['town']['title']}")


if __name__ == '__main__':
    main()

