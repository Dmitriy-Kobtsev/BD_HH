from utils import get_hh_data, create_database, save_data_to_database, DBManager
from config import config


def main():

    employer_ids = [
        '3529',  # Сбер
        '39305',  # Газпром
        '2324020',  # Точка
        '114223',  # Буше
        '64174',  # 2ГИС
        '139',  # IBS
        '1455',  # HH
        '84585',  # avito
        '588914',  # aviasales.ru
        '80',  # alfa_bank

    ]
    data = get_hh_data(employer_ids)
    params = config()
    BD_name = 'headhunter'
    create_database(BD_name, params)
    save_data_to_database(data, BD_name, params)


if __name__ == '__main__':
    main()
    database = DBManager('headhunter', config())
    database.get_companies_and_vacancies_count()
    database.get_vacancies_with_keyword('Python')