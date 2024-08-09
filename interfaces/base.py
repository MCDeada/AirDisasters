import mysql.connector
from interfaces.connection_config import connection_params, database_name
from typing import Dict, Tuple, Any
from flask import Response, jsonify

from table_consts import tables_fields


class Base:
    def __init__(self, table_name: str = 'Base'):
        self.table_name = table_name
        # Запрос извлекающий данные по всем полям, заменяющий все внешние ключи
        # на значения из таблиц, на которые они ссылаются
        self.sql_get_row_by_id_fancy = ''
        # Запрос извлекающий данные по всем полям, заменяющий только часть
        # внешних ключей на значения из таблиц, на которые они ссылаются,
        # В частности нужен при изменении и удалении
        self.sql_get_row_by_id = ''

    @staticmethod
    def get_rows_by_sql(
        sql: str, one_row: bool = False
    ) -> Dict[str, Any]:
        """
        Единый для всех таблиц метод для получения данных из базы
        :param sql: Запрос на языке sql
        :param one_row: Флаг определяющий нужно извлечь одну запись или 10
        :return: Статус операции и извлеченные данные
        """
        error = False
        res = None
        with mysql.connector.connect(**connection_params) as conn:
            cur = conn.cursor(dictionary=True)
            try:
                cur.execute(f'use {database_name}')
                cur.execute(sql)
                res = cur.fetchone() if one_row else cur.fetchall()
            except Exception as e:
                error = e.args
            finally:
                cur.close()
        return {"result": res, "error": error}

    @staticmethod
    def create_or_update_row_by_sql(
        sql: str, data: Tuple[Any, ...],
        is_create: bool = False
    ) -> Dict[str, Any]:
        """
        Единый метод для создания и изменения данных в базе
        :param sql: Запрос на языке sql
        :param data: Данные в виде кортежа
        :param is_create: Флаг, в случае True метод
            вернет id созданной записи в бд
        :return: Статус операции и id созданной записи или None
        """
        error = False
        row_id = None
        try:
            with mysql.connector.connect(**connection_params) as conn:
                cur = conn.cursor(dictionary=True)
                cur.execute(f'use {database_name}')
                cur.execute(sql, data)
                conn.commit()
                if is_create:
                    cur.execute("SELECT LAST_INSERT_ID() as row_id")
                    row_id = cur.fetchone()['row_id']
                cur.close()
        except Exception as e:
            error = e.args

        return {"error": error, 'row_id': row_id}

    @staticmethod
    def delete_by_sql(sql: str) -> Dict[str, Any]:
        """
        Единый метод удаления данных из базы данных
        :param sql: Запрос на языке sql
        :return: Словарь со статусом операции
        """
        error = False
        with mysql.connector.connect(**connection_params) as conn:
            cur = conn.cursor(dictionary=True)
            try:
                cur.execute(f'use {database_name}')
                cur.execute(sql)
                conn.commit()
            except Exception as e:
                error = e.args
            finally:
                cur.close()
        return {"error": error}

    def get_rows(
        self, page_number: str, filters_str: str = ''
    ) -> Response:
        """ Извлекает данные для маршрута get_all """
        ...

    def get_row_by_id_all(
        self, row_id: str, sql: str
    ) -> Response:
        """
        Извлекает все поля одной записи
        с подмененными данными во внешних полях
        :param row_id: Номер записи
        :param sql: Используемый запрос
        :return: Статус операции и извлеченные данные
        """
        ...

    def get_empty(self) -> Dict[str, str]:
        """
        Словарь с полями и пустыми для них значениями в зависимости от таблицы
        :return: словарь, где по имени поля хранится пустая строка
        """
        res = {}
        for field, values in tables_fields[self.table_name].items():
            if values.get('type', False):
                res |= {field: ''}
        return res

    def get_rows_all_foreign(self) -> Response:
        """
        Извлекает и готовит данные для использования в виде выпадающих списков
        :return: Статус ошибочности операции и данные по таблице
        """
        ...

    def get_foreign_fields(self) -> Response:
        """
        Формирует словарь, в котором по имени внешнего ключа таблицы,
        хранится список значений
        :return: Статус ошибочности операции и данные по таблице
        """
        field_values = {}
        return jsonify(field_values)

    def update(
        self, data: Dict[str, Any]
    ) -> Response:
        """
        Формирует запросы для обновления записей в базе данных
        :param data: Словарь с данными полей
        :return: Ответ со статусом операции
        """
        ...

    def create(
        self, data: Dict[str, Any]
    ) -> Response:
        """
        Формирует запросы для обновления записей в базе данных
        :param data: Словарь с данными полей
        :return: Ответ со статусом операции
        """
        ...

    def delete(self, row_id: str) -> Response:
        """
        Формирует запросы для удаления записей в базе данных
        :param row_id: номер записи
        :return: Ответ со статусом операции
        """
        ...

    def get_filters(
        self, filters: Dict[str, Any], find: Dict[str, Any]
    ) -> str:
        """
        Получает список необходимых фильтров для класса катастроф,
        у остальных классов метод - пустой
        :param filters: словарь со значениями для фильтров
        :param find: словарь со значениями для поиска среди текстовых полей
        :return: строка с фильтрами
        """
        return ''

    @staticmethod
    def get_rows_count(
        table_name: str, filters_str: str = ''
    ) -> Response:
        """
        Метод определяющий количество записей в таблице бд.
        Используется при проверке корректности номера страницы
        :param table_name: имя таблицы
        :param filters_str: фильтр катастроф, если он необходим
        :return: (False, имя ошибки) если произошла ошибка
                 (True, количество записей) если ошибки нет
        """
        sql = f""" 
            SELECT COUNT(*) as count FROM {table_name} d {filters_str};
        """
        res = Base.get_rows_by_sql(sql, one_row=True)
        return jsonify(res)

    def is_unique_value(
        self, table_name: str, field_name: str,
        value: str
    ) -> bool:
        """
        Проверяет не встречается ли значение value среди значений
        столбца field_name таблицы table_name
        :param table_name: Имя таблицы, в которой проверяется уникальность.
        :param field_name: Имя столбца, в котором проверяется уникальность.
        :param value: Значение.
        :return: False если произошла ошибка или значение не уникально
                 True если значение уникально
        """
        try:
            with mysql.connector.connect(**connection_params) as conn:
                cur = conn.cursor()
                sql = f""" 
                    SELECT COUNT(*) FROM {database_name}.{table_name}
                    WHERE {field_name} = '{value}';
                """
                cur.execute(sql)
                res = cur.fetchone()[0]
                cur.close()
            return not bool(res)
        except Exception:
            return False
