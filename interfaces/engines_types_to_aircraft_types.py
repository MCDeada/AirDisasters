from interfaces.base import Base
from typing import Any, Dict
from flask import jsonify, Response
from interfaces.aircraft_types import AircraftTypes
from interfaces.engine_types import EngineTypes


class EnginesTypesToAircraftTypes(Base):
    def __init__(self, table_name: str):
        Base().__init__(table_name=table_name)
        self.table_name = table_name
        self.sql_get_row_by_id_fancy = f"""
        SELECT
            at.model_name as id_aircraft_type,
            et.model_name as id_engine_type
        FROM
            Engines_types_to_aircraft_types etat
        LEFT JOIN
            Aircraft_types at ON at.id = etat.id_aircraft_type
        LEFT JOIN
            Engine_types et ON et.id = etat.id_engine_type
        WHERE
            etat.id = 
        """
        self.sql_get_row_by_id = self.sql_get_row_by_id_fancy

    def get_rows(self, page_number: str, filters_str: str = '') -> Response:
        # В зависимости от желаемой страницы данных
        # нужно задать смещение offset количество данных size
        offset = max((int(page_number) - 1) * 10, 0)
        size = 10
        sql = f"""
        SELECT
            etat.id, at.model_name as id_aircraft_type,
            et.model_name as id_engine_type
        FROM
            Engines_types_to_aircraft_types etat
        LEFT JOIN
            Aircraft_types at ON at.id = etat.id_aircraft_type
        LEFT JOIN
            Engine_types et ON et.id = etat.id_engine_type
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
        # данные из таблицы, на которую ссылается id_aircraft_type
        all_aircraft_types = (
            AircraftTypes('aircraft_types').get_rows_all_foreign().get_json()
        )
        if all_aircraft_types['error']:
            return jsonify(all_aircraft_types)
        # данные из таблицы, на которую ссылается id_engine_type
        all_engine_types = (
            EngineTypes('engine_types').get_rows_all_foreign().get_json()
        )
        if all_engine_types['error']:
            return jsonify(all_engine_types)
        field_values = {
            'id_aircraft_type': all_aircraft_types['result'],
            'id_engine_type': all_engine_types['result']
        }
        return jsonify(field_values)

    def update(self, data: Dict[str, Any]) -> Response:
        sql = f"""
        UPDATE Engines_types_to_aircraft_types
        SET id_engine_type = %s,
            id_aircraft_type = %s
        WHERE id = %s;
        """
        tupled_data = (
            data['id_engine_type'], data['id_aircraft_type'],
            data['row_id'],
        )
        res = Base.create_or_update_row_by_sql(sql, tupled_data)
        return jsonify(res)

    def create(self, data: Dict[str, Any]) -> Response:
        sql = f"""
        INSERT INTO Engines_types_to_aircraft_types(
            id_engine_type, id_aircraft_type
        ) VALUES (%s, %s);
        """
        tupled_data = (
            data['id_engine_type'], data['id_aircraft_type'],
        )
        res = Base.create_or_update_row_by_sql(sql, tupled_data, is_create=True)
        return jsonify(res)

    def delete(self, row_id: int) -> Response:
        sql = f"""
            DELETE FROM Engines_types_to_aircraft_types WHERE id = {row_id};
        """
        res = Base.delete_by_sql(sql)
        return jsonify(res)
