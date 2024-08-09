from interfaces.base import Base
from flask import jsonify, Response
from typing import Dict, Any
from interfaces.countries import Countries


class Operators(Base):
    def __init__(self, table_name: str):
        Base().__init__(table_name=table_name)
        self.table_name = table_name
        self.sql_get_row_by_id_fancy = f"""
        SELECT
            operator_name, country_name as country, ICAO_code
        FROM
            Operators op
        LEFT JOIN Countries c ON c.id = op.country
        WHERE
            op.id = 
        """
        self.sql_get_row_by_id = self.sql_get_row_by_id_fancy

    def get_rows(self, page_number: str, filters_str: str = '') -> Response:
        # В зависимости от желаемой страницы данных
        # нужно задать смещение offset количество данных size
        offset = max((int(page_number) - 1) * 10, 0)
        size = 10
        sql = f"""
        SELECT
            op.id, operator_name, country_name as country, ICAO_code
        FROM
            Operators op
        LEFT JOIN
            Countries c ON c.id = op.country
        LIMIT {offset}, {size};
        """
        res = Base.get_rows_by_sql(sql)
        return jsonify(res)

    def get_row_by_id_all(self, row_id: str, sql: str) -> Response:
        # Формируется запрос
        sql = f'{sql} {row_id}'
        res = Base.get_rows_by_sql(sql, one_row=True)
        return jsonify(res)

    def get_foreign_fields(self) -> Response:
        # данные из таблицы, на которую ссылается country
        all_countries = (
            Countries('countries').get_rows_all_foreign().get_json()
        )
        if all_countries['error']:
            return jsonify(all_countries)
        field_values = {'country': all_countries['result']}
        return jsonify(field_values)

    def get_rows_all_foreign(self) -> Response:
        sql = f"""
        SELECT
            id, operator_name
        FROM
            Operators
        """
        res = Base.get_rows_by_sql(sql)
        if res['error']:
            return jsonify(res)
        # Формирует словарь, где номеру записи в базе данных
        # соответствует имя поля
        res_dict = {row['operator_name']: row['id'] for row in res['result']}
        return jsonify({'error': False, 'result': res_dict})

    def update(self, data: Dict[str, Any]) -> Response:
        sql = f"""
        UPDATE Operators
        SET operator_name = %s,
            country = %s,
            ICAO_code = %s
        WHERE id = %s;
        """
        tupled_data = (
            data['operator_name'], data['country'],
            data['ICAO_code'], data['row_id']
        )
        res = Base.create_or_update_row_by_sql(sql, tupled_data)
        return jsonify(res)

    def create(self, data: Dict[str, Any]) -> Response:
        sql = f"""
        INSERT INTO Operators(
            operator_name, country, ICAO_code
        ) VALUES (%s, %s, %s);
        """
        tupled_data = (
            data['operator_name'], data['country'], data['ICAO_code']
        )
        res = Base.create_or_update_row_by_sql(sql, tupled_data, is_create=True)
        return jsonify(res)

    def delete(self, row_id: int) -> Response:
        sql = f"""
            DELETE FROM Operators WHERE id = {row_id};
        """
        res = Base.delete_by_sql(sql)
        return jsonify(res)
