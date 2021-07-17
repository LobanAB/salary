import os
import requests
from pprint import pprint

from dotenv import load_dotenv


def predict_salary(salary_from, salary_to):
    if salary_from is not None:
        if salary_to is not None:
            return (salary_from + salary_to) / 2
        else:
            return salary_from * 1.2
    elif salary_to is not None:
        return salary_to * 0.8


def predict_rub_salary_sj(vacancy):
    return predict_salary(vacancy['payment_from'] if vacancy['payment_from'] != 0 else None,
                          vacancy['payment_to'] if vacancy['payment_to'] != 0 else None)


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
        salary = predict_rub_salary_sj(vacancy)
        print(f"{vacancy['profession']}, {vacancy['town']['title']}")
        print(salary)


if __name__ == '__main__':
    main()

