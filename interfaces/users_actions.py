from interfaces.base import Base
from typing import Any, Dict
from flask import jsonify, Response


class UsersActions(Base):
    def __init__(self, table_name: str):
        Base().__init__(table_name=table_name)
        self.table_name = table_name
        self.sql_get_row_by_id_fancy = f"""
        SELECT
            action_name
        FROM
            Users_actions
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
            id, action_name
        FROM
            Users_actions
        LIMIT {offset}, {size};
        """
        res = Base.get_rows_by_sql(sql)
        return jsonify(res)

    def get_row_by_id_all(self, row_id: str, sql: str) -> Response:
        # Формируется запрос
        sql = f'{sql} {row_id}'
        res = Base.get_rows_by_sql(sql, one_row=True)
        return jsonify(res)

    def get_rows_all(self) -> Response:
        sql = f"""
           SELECT
               id, action_name
           FROM
               Users_actions
           """
        res = Base.get_rows_by_sql(sql)
        if res['error']:
            return jsonify(res)
        res_dict = {row['id']: row['action_name'] for row in res['result']}
        return jsonify({'error': False, 'result': res_dict})

    def update(self, data: Dict[str, Any]) -> Response:
        sql = f"""
        UPDATE Users_actions
        SET action_name = %s
        WHERE id = %s;
        """
        tupled_data = (data['action_name'], data['row_id'],)
        res = Base.create_or_update_row_by_sql(sql, tupled_data)
        return jsonify(res)

    def create(self, data: Dict[str, Any]) -> Response:
        sql = f"""
        INSERT INTO Users_actions(
            action_name
        ) VALUES (%s);
        """
        tupled_data = (data['action_name'],)
        res = Base.create_or_update_row_by_sql(sql, tupled_data, is_create=True)
        return jsonify(res)

    def delete(self, row_id: int) -> Response:
        sql = f"""
            DELETE FROM Users_actions WHERE id = {row_id};
        """
        res = Base.delete_by_sql(sql)
        return jsonify(res)
