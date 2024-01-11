# Employees and vacancies
Проект получения данных о компаниях и вакансиях с сайта hh.ru с записью информации в БД.
## System requirements:
python 3.9
## Setup instruction:
```bash
$ pip install -r requirements.txt
```
## Стек:
1. Python 3.9
2. Json
3. requests
4. psycopg2
5. re
6. config

## How to run:
В main.py
Реализован сценарий взаимодействия с пользователем.
По отобранным работодателям c использованием API hh.ru получаем информацию о них и их вакансиях.
Необходимая информация сохраняется в БД PostgreSQL.
Для работы с данными в БД реализован класс DBManager.

В utils.py реализованы следующие функции:

- get_hh_data - получение данных о работодателе и вакансиях на hh.ru с помощью API hh.ru
- create_database - создание Базы данных и таблиц для сохранения данных о работодателях и вакансиях
- save_data_to_database - сохранение данных о работодателях и вакансиях в базу данных

## Project Goals
Код написан в образовательных целях