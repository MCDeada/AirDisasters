from interfaces.base import Base
from flask import jsonify, Response
from typing import Any, Dict


class EngineTypes(Base):
    def __init__(self, table_name: str):
        Base().__init__(table_name=table_name)
        self.table_name = table_name
        self.sql_get_row_by_id_fancy = f"""
        SELECT
            model_name, static_thrust,
            mass, length, diameter,
            CONVERT(DATE(developed_in), char) as developed_in
        FROM
            Engine_types
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
            id, model_name, static_thrust,
            mass, length, diameter,
            CONVERT(DATE(developed_in), char) as developed_in
        FROM
            Engine_types
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
            id, model_name
        FROM
            Engine_types
        """
        res = Base.get_rows_by_sql(sql)
        if res['error']:
            return jsonify(res)
        # Формирует словарь, где номеру записи в базе данных
        # соответствует имя поля
        res_dict = {row['model_name']: row['id'] for row in res['result']}
        return jsonify({'error': False, 'result': res_dict})

    def update(self, data: Dict[str, Any]) -> Response:
        sql = f"""
        UPDATE Engine_types
        SET model_name = %s,
            static_thrust = %s,
            mass = %s,
            length = %s,
            diameter = %s,
            developed_in = %s
        WHERE id = %s;
        """
        tupled_data = (
            data['model_name'], data['static_thrust'],
            data['mass'], data['length'],
            data['diameter'], data['developed_in'],
            data['row_id'],
        )
        res = Base.create_or_update_row_by_sql(sql, tupled_data)
        return jsonify(res)

    def create(self, data: Dict[str, Any]) -> Response:
        sql = f"""
        INSERT INTO Engine_types(
            model_name, static_thrust, mass,
            length, diameter, developed_in
        ) VALUES (%s, %s, %s, %s, %s, %s);
        """
        tupled_data = (
            data['model_name'], data['static_thrust'],
            data['mass'], data['length'],
            data['diameter'], data['developed_in']
        )
        res = Base.create_or_update_row_by_sql(sql, tupled_data, is_create=True)
        return jsonify(res)

    def delete(self, row_id: int) -> Response:
        sql = f"""
            DELETE FROM Engine_types WHERE id = {row_id};
        """
        res = Base.delete_by_sql(sql)
        return jsonify(res)
