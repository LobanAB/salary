import os
import requests

from terminaltables import AsciiTable
from dotenv import load_dotenv


def print_hh_salary(prog_lang_salary):
    for lang in prog_lang_salary:
        pages = get_from_hh(lang)['pages']
        salary = []
        for page in range(pages):
            vacancies = get_from_hh(lang, page)
            for vacancy in vacancies['items']:
                if vacancy['salary'] is not None:
                    if (predict_rub_salary(vacancy['salary']['from'], vacancy['salary']['to']) is not None)\
                            and (vacancy['salary']['currency'] == 'RUR'):
                        salary.append(predict_rub_salary(vacancy['salary']['from'], vacancy['salary']['to']))
        prog_lang_salary[lang] = {
            'vacancies_found': vacancies['found'],
            'vacancies_processed': len(salary),
            'average_salary': int(sum(salary) / len(salary))
        }
    print_table(prog_lang_salary, 'HeadHunter Moscow')


def print_sj_salary(prog_lang_salary):
    load_dotenv()
    superjob_api_key = os.getenv('SUPERJOB_API_KEY')
    for lang in prog_lang_salary:
        page = 0
        salary = []
        while True:
            vacancies = get_from_sj(superjob_api_key, page, lang)
            for vacancy in vacancies['objects']:
                if predict_rub_salary_sj(vacancy) is not None:
                    salary.append(predict_rub_salary_sj(vacancy))
            page += 1
            if not vacancies['more']:
                break
        prog_lang_salary[lang] = {
            'vacancies_found': vacancies['total'],
            'vacancies_processed': len(salary),
            'average_salary': int(sum(salary) / len(salary)) if len(salary) != 0 else None
        }
    print_table(prog_lang_salary, 'SuperJob Moscow')


def get_from_hh(prog_lang, page=1):
    url = 'https://api.hh.ru/vacancies'
    payload = {
        'text': f'name:Программист {prog_lang}',
        'period': 30,
        'area': 1,
        'page': page,
        'per_page': 20
    }
    response = requests.get(url, params=payload)
    response.raise_for_status()
    return response.json()


def get_from_sj(superjob_api_key, page, prog_lang):
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


def predict_rub_salary(salary_from, salary_to):
    if salary_from is not None:
        if salary_to is not None:
            return (salary_from + salary_to) / 2
        else:
            return salary_from * 1.2
    elif salary_to is not None:
        return salary_to * 0.8


def predict_rub_salary_sj(vacancy):
    return predict_rub_salary(vacancy['payment_from'] if vacancy['payment_from'] != 0 else None,
                             vacancy['payment_to'] if vacancy['payment_to'] != 0 else None)


def print_table(prog_lang_salary, title):
    table_data = [
        ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата'],
    ]
    for lang, data in prog_lang_salary.items():
        data_string = [lang, data['vacancies_found'], data['vacancies_processed'], data['average_salary']]
        table_data.append(data_string)

    table = AsciiTable(table_data, title)
    print(table.table)


def main() -> None:
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
    print_hh_salary(prog_lang)
    print_sj_salary(prog_lang)


if __name__ == '__main__':
    main()