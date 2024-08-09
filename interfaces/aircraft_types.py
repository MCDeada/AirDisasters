from interfaces.base import Base
from flask import jsonify, Response
from typing import Dict, Any


class AircraftTypes(Base):
    def __init__(self, table_name: str):
        Base().__init__(table_name=table_name)
        self.table_name = table_name
        self.sql_get_row_by_id_fancy = f"""
        SELECT
            model_name,
            DATE_FORMAT(first_flight, '%Y-%m-%d') as first_flight,
            DATE_FORMAT(last_flight, '%Y-%m-%d') as last_flight,
            max_mass, max_crew, max_passengers,
            length, height, wingspan, wing_area, fuselage_width,
            interior_width, cruising_speed, runaway_range,
            max_flight_altitude
        FROM
            Aircraft_types at
        WHERE
            at.id = 
        """
        self.sql_get_row_by_id = self.sql_get_row_by_id_fancy

    def get_rows(self, page_number: str, filters_str: str = '') -> Response:
        # В зависимости от желаемой страницы данных
        # нужно задать смещение offset количество данных size
        offset = max((int(page_number) - 1) * 10, 0)
        size = 10
        sql = f"""
        SELECT
            at.id, model_name,
            DATE_FORMAT(first_flight, '%Y-%m-%d') as first_flight,
            DATE_FORMAT(last_flight, '%Y-%m-%d') as last_flight,
            max_crew, max_passengers
        FROM
            Aircraft_types at
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
            Aircraft_types
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
        UPDATE Aircraft_types
        SET model_name = %s,
            first_flight = %s,
            last_flight = %s,
            max_passengers = %s,
            max_crew = %s,
            length = %s,
            height = %s,
            wingspan = %s,
            wing_area = %s,
            fuselage_width = %s,
            interior_width = %s,
            cruising_speed = %s,
            runaway_range = %s,
            max_flight_altitude = %s
        WHERE id = %s;
        """
        tupled_data = (
            data['model_name'], data['first_flight'],
            data['last_flight'], data['max_passengers'],
            data['max_crew'], data['length'],
            data['height'], data['wingspan'],
            data['wing_area'], data['fuselage_width'],
            data['interior_width'], data['cruising_speed'],
            data['runaway_range'], data['max_flight_altitude'],
            data['row_id'],)
        res = Base.create_or_update_row_by_sql(sql, tupled_data)
        return jsonify(res)

    def create(self, data: Dict[str, Any]) -> Response:
        sql = f"""
        INSERT INTO Aircraft_types(
            model_name, first_flight, last_flight,
            max_mass, max_crew, max_passengers,
            length, height, wingspan,
            wing_area, fuselage_width,
            interior_width, cruising_speed, runaway_range,
            max_flight_altitude
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        );
        """
        tupled_data = (
            data['model_name'], data['first_flight'], data['last_flight'],
            data['max_mass'], data['max_crew'], data['max_passengers'],
            data['length'], data['height'], data['wingspan'],
            data['wing_area'], data['fuselage_width'],
            data['interior_width'], data['cruising_speed'],
            data['runaway_range'], data['max_flight_altitude']
        )
        res = Base.create_or_update_row_by_sql(sql, tupled_data, is_create=True)
        return jsonify(res)

    def delete(self, row_id: int) -> Response:
        sql = f"""
            DELETE FROM Aircraft_types WHERE id = {row_id};
        """
        res = Base.delete_by_sql(sql)
        return jsonify(res)
