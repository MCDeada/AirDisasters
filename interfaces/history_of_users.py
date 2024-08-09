from interfaces.base import Base
from flask import jsonify, Response


class HistoryOfUsers(Base):
    def __init__(self, table_name: str):
        Base().__init__(table_name=table_name)
        self.table_name = table_name
        self.sql_get_row_by_id_fancy = f"""
        SELECT
            u.login as user_id,
            uac.action_name as user_action,
            related_table, row_before_action,
            row_after_action, 
            DATE_FORMAT(action_datetime, '%Y-%m-%d %H:%i') as action_datetime
        FROM
            History_of_users hou
        LEFT JOIN 
            Users u ON u.id = hou.user_id
        LEFT JOIN 
            Users_actions uac ON uac.id = hou.user_action
        WHERE
            hou.id = 
        """
        self.sql_get_row_by_id = self.sql_get_row_by_id_fancy

    def get_rows(self, page_number: str, filters_str: str = '') -> Response:
        # В зависимости от желаемой страницы данных
        # нужно задать смещение offset количество данных size
        offset = max((int(page_number) - 1) * 10, 0)
        size = 10
        sql = f"""
        SELECT
            hou.id, u.login as user_id,
            uac.action_name as user_action,
            related_table, '...' as row_before_action,
            '...' as row_after_action,
            DATE_FORMAT(action_datetime, '%Y-%m-%d %H:%i') as action_datetime
        FROM
            History_of_users hou
        LEFT JOIN 
            Users u ON u.id = hou.user_id
        LEFT JOIN 
            Users_actions uac ON uac.id = hou.user_action
        ORDER BY action_datetime DESC
        LIMIT {offset}, {size};
        """
        res = Base.get_rows_by_sql(sql)
        return jsonify(res)

    def get_row_by_id_all(self, row_id: str, sql: str) -> Response:
        # Формируется запрос
        sql = f'{sql} {row_id}'
        res = Base.get_rows_by_sql(sql, one_row=True)
        return jsonify(res)
