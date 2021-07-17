import requests


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
    # print(response.json()['found'])
    return response.json()


def predict_rub_salary(vacancy):
    if vacancy['currency'] == 'RUR':
        if vacancy['from'] is not None:
            if vacancy['to'] is not None:
                return (vacancy['from'] + vacancy['to']) / 2
            else:
                return vacancy['from'] * 1.2
        else:
            return vacancy['to'] * 0.8


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
    for lang in prog_lang:
        pages = get_from_hh(lang)['pages']
        salary = []
        if pages > 2:
            pages = 2
        for page in range(pages):
            vacancies = get_from_hh(lang, page)
            for vacancy in vacancies['items']:
                if vacancy['salary'] is not None:
                    if predict_rub_salary(vacancy['salary']) is not None:
                        salary.append(predict_rub_salary(vacancy['salary']))
                    # print(predict_rub_salary(vacancy['salary']))
        prog_lang[lang] = {
            'vacancies_found': vacancies['found'],
            'vacancies_processed': len(salary),
            'average_salary': int(sum(salary) / len(salary))
        }
    print(prog_lang)

    #    prog_lang[lang] = get_from_hh(lang)
    # print(prog_lang)

    # print(vacancy['salary'])


if __name__ == '__main__':
    main()
