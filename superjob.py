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


def get_vacancy_sj(superjob_api_key, page, prog_lang):
    url = 'https://api.superjob.ru/2.0/vacancies/'
    payload = {
        'catalogues': 48,
        'town': 4,
        'page': page,
        'count': 100,
        'keyword': prog_lang
    }
    headers = {'X-Api-App-Id': superjob_api_key}
    response = requests.get(url, headers=headers, params=payload)
    response.raise_for_status()
    return response.json()


def main():
    load_dotenv()
    superjob_api_key = os.getenv('SUPERJOB_API_KEY')
    page = 1
    salary = []
    prog_lang = {
        'JavaScript': {},
        'Java': {},
        'Python': {},
        'Ruby': {},
        'PHP': {},
        'C++': {},
        'C#': {},
        'Go': {},
        'Scala': {}
    }
    for lang in prog_lang:
        page = 0
        salary = []
        while True:
            vacancies = get_vacancy_sj(superjob_api_key, page, lang)
            for vacancy in vacancies['objects']:
                if predict_rub_salary_sj(vacancy) is not None:
                    salary.append(predict_rub_salary_sj(vacancy))
            page += 1
            if not vacancies['more']:
                break
        print(salary)
        prog_lang[lang] = {
            'vacancies_found': vacancies['total'],
            'vacancies_processed': len(salary),
            'average_salary': int(sum(salary) / len(salary)) if len(salary) != 0 else None
        }
    pprint(prog_lang)


if __name__ == '__main__':
    main()
