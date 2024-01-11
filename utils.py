import requests
import re
import psycopg2


class DBManager:
    """Класс для работы с базой данных"""

    def __init__(self, database_name, params):
        self.database_name = database_name
        self.params = params

    def get_companies_and_vacancies_count(self):
        """получает список всех компаний и количество вакансий у каждой компании"""

        conn = psycopg2.connect(dbname=self.database_name, **self.params)

        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT employees.title, COUNT(*)
                FROM vacancies
                INNER JOIN employees USING(employer_id)
                GROUP BY employees.title
                """
            )
            rows = cur.fetchall()
            print(rows)

        conn.close()

    def get_all_vacancies(self):
        """получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию
        """

        conn = psycopg2.connect(dbname=self.database_name, **self.params)

        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT employees.title, vacancies.title, salary, vacancy_url
                FROM vacancies
                INNER JOIN employees USING(employer_id)
                """
            )
            rows = cur.fetchall()
            print(rows)

        conn.close()

    def get_avg_salary(self):
        """получает среднюю зарплату по вакансиям"""

        conn = psycopg2.connect(dbname=self.database_name, **self.params)

        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT AVG(salary)
                FROM vacancies
                """
            )
            rows = cur.fetchall()
            print(rows)

        conn.close()

    def get_vacancies_with_higher_salary(self):
        """получает список всех вакансий, у которых зарплата выше средней по всем вакансиям"""

        conn = psycopg2.connect(dbname=self.database_name, **self.params)

        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT *
                FROM vacancies
                WHERE salary > (SELECT AVG(salary) FROM vacancies)
                """
            )
            rows = cur.fetchall()
            print(rows)

        conn.close()

    def get_vacancies_with_keyword(self, key_word):
        """получает список всех вакансий, в названии которых содержатся переданные в метод слова, например python"""

        conn = psycopg2.connect(dbname=self.database_name, **self.params)

        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT *
                FROM vacancies
                WHERE title LIKE '%{key_word}%'
                """
            )
            rows = cur.fetchall()
            print(rows)

        conn.close()


def get_hh_data(employer_ids):
    """Получение данных о работодателе и вакансиях на hh.ru с помощью API hh.ru"""

    hh_data = []
    for employer_id in employer_ids:
        employer_data = {}
        vacancies = []
        url_employer = 'https://api.hh.ru/employers/'+str(employer_id)

        url = 'https://api.hh.ru/vacancies'
        params = {
            "employer_id": employer_id,
        }
        headers = {
            "User-Agent": 'kibtsev94@gmail.com',
        }

        response = requests.get(url_employer, headers=headers)
        if response.status_code == 200:
            data = response.json()
            text = re.sub(r'<.*?>', '', data.get('description'))
            text = re.sub(r'\xa0', '', text)
            employer_data = {
                "employer_name": data.get('name'),
                "employer_about": text
            }
        else:
            print(f"Request failed with status code: {response.status_code}")

        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            data = response.json()
            vacancies = data.get("items", [])
        else:
            print(f"Request failed with status code: {response.status_code}")

        hh_data.append({
            'employer': employer_data,
            'vacancies': vacancies
        })

    return hh_data


def create_database(database_name, params):
    """Создание Базы данных и таблиц для сохранения данных о работодателях и вакансиях"""

    conn = psycopg2.connect(dbname='postgres', **params)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(f"DROP DATABASE {database_name}")
    cur.execute(f"CREATE DATABASE {database_name}")

    conn.close()

    conn = psycopg2.connect(dbname=database_name, **params)

    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE employees (
                employer_id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                employer_about TEXT
            )
        """)

    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE vacancies(
                vacancy_id SERIAL PRIMARY KEY,
                employer_id INT REFERENCES employees(employer_id),
                title VARCHAR(255),
                published_at DATE,
                salary INTEGER,
                vacancy_url TEXT,
                requirement TEXT,
                responsibility TEXT,
                area VARCHAR(100),
                experience TEXT,
                employment VARCHAR(100)
            )
        """)
    conn.commit()
    conn.close()


def save_data_to_database(data, database_name, params):
    """Сохранение данных о работодателях и вакансиях в базу данных"""

    conn = psycopg2.connect(dbname=database_name, **params)

    with conn.cursor() as cur:
        for employer in data:
            cur.execute(
                """
                INSERT INTO employees (title, employer_about)
                VALUES (%s, %s)
                RETURNING employer_id
                """,
                (employer['employer']['employer_name'], employer['employer']['employer_about'])
            )
            employer_id = cur.fetchone()[0]
            vacancy_data = employer['vacancies']
            # Проверим заполнение графы ЗП. Ставим ноль если оба поля None
            for vacancy in vacancy_data:
                if vacancy.get('salary') is None:
                    salary = 0
                elif vacancy.get('salary')['from'] is None:
                    if vacancy.get('salary')['to'] is not None:
                        salary = int(vacancy['salary']['to'])
                    else:
                        salary = 0
                else:
                    salary = vacancy.get('salary')['from']
                cur.execute(
                    """
                    INSERT INTO vacancies (employer_id, title, published_at, salary, vacancy_url, requirement, responsibility, area, experience, employment)
                    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        employer_id,
                        vacancy['name'],
                        vacancy['published_at'],
                        salary,
                        vacancy['alternate_url'],
                        vacancy['snippet']['requirement'],
                        vacancy['snippet']['responsibility'],
                        vacancy['area']['name'],
                        vacancy['experience']['name'],
                        vacancy['employment']['name']
                    )
                )

    conn.commit()
    conn.close()