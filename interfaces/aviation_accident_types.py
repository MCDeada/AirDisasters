from interfaces.base import Base
from typing import Any, Dict
from flask import jsonify, Response


class AviationAccidentTypes(Base):
    def __init__(self, table_name: str):
        Base().__init__(table_name=table_name)
        self.table_name = table_name
        self.sql_get_row_by_id_fancy = f"""
        SELECT
            accident_type
        FROM
            Aviation_accident_types
        WHERE
            id = 
        """
        self.sql_get_row_by_id = self.sql_get_row_by_id_fancy

    def get_rows(self, page_number: str, filters_str: str = '') -> Response:
        # В зависимости от желаемой страницы данных
        # нужно задать смещение offset количество данных size
        offset = max((int(page_number) - 1) * 10, 0)
        size = 10
        sql = f"""
        SELECT
            id, accident_type
        FROM
            Aviation_accident_types
        LIMIT {offset}, {size};
        """
        res = Base.get_rows_by_sql(sql)
        return jsonify(res)

    def get_row_by_id_all(self, row_id: str, sql: str) -> Response:
        # Формируется запрос
        sql = f'{sql} {row_id}'
        res = Base.get_rows_by_sql(sql, one_row=True)
        return jsonify(res)

    def get_rows_all_foreign(self) -> Response:
        sql = f"""
        SELECT
            id, accident_type
        FROM
            Aviation_accident_types
        """
        res = Base.get_rows_by_sql(sql)
        if res['error']:
            return jsonify(res)
        # Формирует словарь, где номеру записи в базе данных
        # соответствует имя поля
        res_dict = {row['id']: row['accident_type'] for row in res['result']}
        return jsonify({'error': False, 'result': res_dict})

    def update(self, data: Dict[str, Any]) -> Response:
        sql = f"""
        UPDATE Aviation_accident_types
        SET accident_type = %s
        WHERE id = %s;
        """
        tupled_data = (data['accident_type'], data['row_id'],)
        res = Base.create_or_update_row_by_sql(sql, tupled_data)
        return jsonify(res)

    def create(self, data: Dict[str, Any]) -> Response:
        sql = f"""
        INSERT INTO Aviation_accident_types(
            accident_type
        ) VALUES (%s);
        """
        tupled_data = (data['accident_type'],)
        res = Base.create_or_update_row_by_sql(sql, tupled_data, is_create=True)
        return jsonify(res)

    def delete(self, row_id: int) -> Response:
        sql = f"""
            DELETE FROM Aviation_accident_types WHERE id = {row_id};
        """
        res = Base.delete_by_sql(sql)
        return jsonify(res)
