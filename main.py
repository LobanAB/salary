import os

import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable


def get_hh_salaries(prog_langs):
    prog_lang_salaries = {}
    for lang in prog_langs:
        salaries, vacancies_found = get_hh_lang_salaries(lang)
        prog_lang_salaries[lang] = {
            'vacancies_found': vacancies_found,
            'vacancies_processed': len(salaries),
            'average_salary': int(sum(salaries) / len(salaries)) if len(salaries) else None
        }
    return prog_lang_salaries


def get_hh_lang_salaries(lang):
    salaries = []
    page = 0
    while True:
        vacancies = get_vacancies_from_hh(lang, page)
        for vacancy in vacancies['items']:
            if not vacancy['salary'] or vacancy['salary']['currency'] != 'RUR':
                continue
            rub_salary = predict_rub_salary(vacancy['salary']['from'], vacancy['salary']['to'])
            if rub_salary:
                salaries.append(rub_salary)
        page += 1
        if page == vacancies['pages']:
            return salaries, vacancies['found']


def get_sj_salaries(prog_langs, superjob_api_key):
    prog_lang_salaries = {}
    for lang in prog_langs:
        salaries, vacancies_found = get_sj_lang_salaries(lang, superjob_api_key)
        prog_lang_salaries[lang] = {
            'vacancies_found': vacancies_found,
            'vacancies_processed': len(salaries),
            'average_salary': int(sum(salaries) / len(salaries)) if len(salaries) else None
        }
    return prog_lang_salaries


def get_sj_lang_salaries(lang, superjob_api_key):
    salaries = []
    page = 0
    while True:
        vacancies = get_vacancies_from_sj(superjob_api_key, page, lang)
        for vacancy in vacancies['objects']:
            vacancy_salary = predict_rub_salary(vacancy['payment_from'], vacancy['payment_to'])
            if vacancy_salary:
                salaries.append(vacancy_salary)
        page += 1
        if not vacancies['more']:
            return salaries, vacancies['total']


def get_vacancies_from_hh(prog_lang, page=1):
    url = 'https://api.hh.ru/vacancies'
    vacancies_published_days = 30
    vacancies_city = 1
    vacancies_per_page = 20
    payload = {
        'text': f'name:?????????????????????? {prog_lang}',
        'period': vacancies_published_days,
        'area': vacancies_city,
        'page': page,
        'per_page': vacancies_per_page
    }
    response = requests.get(url, params=payload)
    response.raise_for_status()
    return response.json()


def get_vacancies_from_sj(superjob_api_key, page, prog_lang):
    url = 'https://api.superjob.ru/2.0/vacancies/'
    industries_section = 48
    vacancies_city = 4
    vacancies_per_page = 100
    payload = {
        'catalogues': industries_section,
        'town': vacancies_city,
        'page': page,
        'count': vacancies_per_page,
        'keyword': prog_lang
    }
    headers = {'X-Api-App-Id': superjob_api_key}
    response = requests.get(url, headers=headers, params=payload)
    response.raise_for_status()
    return response.json()


def predict_rub_salary(salary_from, salary_to):
    if salary_from:
        if salary_to:
            return (salary_from + salary_to) / 2
        else:
            return salary_from * 1.2
    elif salary_to:
        return salary_to * 0.8


def get_table(prog_lang_salaries, title):
    table = [
        ['???????? ????????????????????????????????',
         '???????????????? ??????????????',
         '???????????????? ????????????????????',
         '?????????????? ????????????????'],
    ]
    for lang, salaries in prog_lang_salaries.items():
        prog_lang = [lang,
                     salaries['vacancies_found'],
                     salaries['vacancies_processed'],
                     salaries['average_salary']
                     ]
        table.append(prog_lang)
    table = AsciiTable(table, title)
    return table


def main() -> None:
    load_dotenv()
    superjob_api_key = os.getenv('SUPERJOB_API_KEY')
    prog_langs = [
        'JavaScript',
        'Java',
        'Python',
        'Ruby',
        'PHP',
        'C++',
        'C#',
        'Go',
        'Scala'
    ]
    hh_prog_lang_salaries = get_hh_salaries(prog_langs)
    sj_prog_lang_salaries = get_sj_salaries(prog_langs, superjob_api_key)
    hh_table = get_table(hh_prog_lang_salaries, 'HeadHunter Moscow')
    sj_table = get_table(sj_prog_lang_salaries, 'SuperJob Moscow')
    print(hh_table.table)
    print(sj_table.table)


if __name__ == '__main__':
    main()
