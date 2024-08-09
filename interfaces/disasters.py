from interfaces.aircraft_conditions import AircraftConditions
from interfaces.aircraft_types import AircraftTypes
from interfaces.airports import Airports
from interfaces.aviation_accident_types import AviationAccidentTypes
from interfaces.base import Base
from flask import jsonify, Response
from typing import Any, Dict, Tuple

from interfaces.countries import Countries
from interfaces.engine_types import EngineTypes
from interfaces.flight_phases import FlightPhases
from interfaces.flight_types import FlightTypes
from interfaces.operators import Operators
from interfaces.weather_conditions import WeatherConditions


class Disasters(Base):
    def __init__(self, table_name: str):
        Base().__init__(table_name=table_name)
        self.table_name = table_name
        self.sql_get_row_by_id_fancy = f"""
        SELECT
            DATE_FORMAT(disaster_datetime, '%Y-%m-%dT%H:%i') as disaster_datetime,
            flight_number, ft.flight_type as flight_type,
            at.model_name as aircraft_model_type,
            et.model_name as engine_model_type,
            registration_code, op.operator_name as operator,
            aip1.airport_name as departure_place,
            DATE_FORMAT(departure_date, '%Y-%m-%dT%H:%i') as departure_date,
            aip2.airport_name as destination_place,
            DATE_FORMAT(destination_date, '%Y-%m-%dT%H:%i') as destination_date,
            crew_survived, crew_fatalities,
            passengers_survived, passengers_fatalities,
            temperature, pressure,
            wc.condition_name as weather_condition, wind_speed,
            c.country_name as country,
            d.latitude, d.longitude, d.height,
            phase_name as flight_phase, ac.condition_name as aircraft_condition,
            accident_type as disaster_accident, location_description,
            accident_description, photo_of_result
        FROM
            Disasters d
        LEFT JOIN 
            Flight_types ft ON ft.id = d.flight_type
        LEFT JOIN
            Aircraft_types at ON at.id = d.aircraft_model_type
        LEFT JOIN
            Engine_types et ON et.id = d.engine_model_type
        LEFT JOIN 
            Operators op ON op.id = d.operator
        LEFT JOIN 
            Airports aip1 ON aip1.id = d.departure_place
        LEFT JOIN 
            Airports aip2 ON aip2.id = d.destination_place
        LEFT JOIN
            Countries c ON c.id = d.country
        LEFT JOIN
            Flight_phases fp ON fp.id = d.flight_phase
        LEFT JOIN
            Aviation_accident_types act ON act.id = d.disaster_accident
        LEFT JOIN
            Aircraft_conditions ac ON ac.id = d.aircraft_condition
        LEFT JOIN
            Weather_conditions wc ON wc.id = d.weather_condition
        WHERE
            d.id = 
        """
        self.sql_get_row_by_id = f"""
        SELECT
            DATE_FORMAT(disaster_datetime, '%Y-%m-%dT%H:%i') as disaster_datetime,
            flight_number, d.flight_type,
            at.model_name as aircraft_model_type,
            et.model_name as engine_model_type,
            registration_code, op.operator_name as operator,
            aip1.airport_name as departure_place,
            DATE_FORMAT(departure_date, '%Y-%m-%dT%H:%i') as departure_date,
            aip2.airport_name as destination_place,
            DATE_FORMAT(destination_date, '%Y-%m-%dT%H:%i') as destination_date,
            crew_survived, crew_fatalities,
            passengers_survived, passengers_fatalities,
            temperature, pressure,
            d.weather_condition, wind_speed,
            c.country_name as country,
            d.latitude, d.longitude, d.height,
            d.flight_phase, d.aircraft_condition,
            d.disaster_accident, location_description,
            accident_description, photo_of_result
        FROM
            Disasters d
        LEFT JOIN
            Aircraft_types at ON at.id = d.aircraft_model_type
        LEFT JOIN
            Engine_types et ON et.id = d.engine_model_type
        LEFT JOIN 
            Operators op ON op.id = d.operator
        LEFT JOIN 
            Airports aip1 ON aip1.id = d.departure_place
        LEFT JOIN 
            Airports aip2 ON aip2.id = d.destination_place
        LEFT JOIN
            Countries c ON c.id = d.country
        WHERE
            d.id =  
        """

    def get_rows(self, page_number: str, filters_str: str = '', find_str: str = '') -> Response:
        # В зависимости от желаемой страницы данных
        # нужно задать смещение offset количество данных size
        offset = max((int(page_number) - 1) * 10, 0)
        size = 10
        sql = f"""
        SELECT
            d.id,
            DATE_FORMAT(disaster_datetime, '%d-%m-%Y %H:%i:%s') as disaster_datetime,
            crew_survived, crew_fatalities,
            passengers_survived, passengers_fatalities,
            country_name as country, phase_name as flight_phase,
            accident_type as disaster_accident
        FROM
            Disasters d
        JOIN Countries c ON c.id = d.country
        JOIN Flight_phases fp ON fp.id = d.flight_phase
        JOIN Aviation_accident_types act ON act.id = d.disaster_accident
        {filters_str}
        LIMIT {offset}, {size};
        """
        res = Base.get_rows_by_sql(sql)
        return jsonify(res)

    def get_row_by_id_all(self, row_id: str, sql: str) -> Response:
        # Формируется запрос
        sql = f'{sql} {row_id}'
        res = Base.get_rows_by_sql(sql, one_row=True)
        # После извлечения изображения из базы его нужно раскодировать, чтобы
        # можно было его отображать
        if (
            'photo_of_result' in res['result'] and
            res['result']['photo_of_result'] is not None
        ):
            res['result']['photo_of_result'] = (
                res['result']['photo_of_result'].decode()
            )
        return jsonify(res)

    def get_foreign_fields(self) -> Response:
        # Подготовка данных, на которые ссылается эта таблица
        field_values = {}
        # Типы полетов
        all_flight_types = (FlightTypes('flight_types').get_rows_all_foreign()
                            .get_json())
        if all_flight_types['error']:
            return jsonify(all_flight_types)
        field_values |= {'flight_type': all_flight_types['result']}
        # Авиаперевозчики
        all_operators = Operators('operators').get_rows_all_foreign().get_json()
        if all_operators['error']:
            return jsonify(all_operators)
        field_values |= {'operator': all_operators['result']}
        # Аэропорты
        all_airports = Airports('airports').get_rows_all_foreign().get_json()
        if all_airports['error']:
            return jsonify(all_airports)
        field_values |= {'departure_place': all_airports['result']}
        field_values |= {'destination_place': all_airports['result']}
        # Модели самолетов
        all_aircraft_types = (AircraftTypes('aircraft_types')
                              .get_rows_all_foreign().get_json())
        if all_aircraft_types['error']:
            return jsonify(all_aircraft_types)
        field_values |= {'aircraft_model_type': all_aircraft_types['result']}
        # Модели двигателей
        all_engine_types = (EngineTypes('engine_types').get_rows_all_foreign()
                            .get_json())
        if all_engine_types['error']:
            return jsonify(all_engine_types)
        field_values |= {'engine_model_type': all_engine_types['result']}
        # Страны
        all_countries = (Countries('countries')
                         .get_rows_all_foreign().get_json())
        if all_countries['error']:
            return jsonify(all_countries)
        field_values |= {'country': all_countries['result']}
        # Направления ветра
        all_wind_directions = (WeatherConditions('weather_conditions')
                               .get_rows_all_foreign().get_json())
        if all_wind_directions['error']:
            return jsonify(all_wind_directions)
        field_values |= {'weather_condition': all_wind_directions['result']}
        # Стадии полета
        all_flight_phases = (FlightPhases('flight_phases')
                             .get_rows_all_foreign().get_json())
        if all_flight_phases['error']:
            return jsonify(all_flight_phases)
        field_values |= {'flight_phase': all_flight_phases['result']}
        # Состояния самолета после аварии
        all_aircraft_conditions = (
            AircraftConditions('aircraft_conditions')
            .get_rows_all_foreign().get_json()
        )
        if all_aircraft_conditions['error']:
            return jsonify(all_aircraft_conditions)
        field_values |= {
            'aircraft_condition': all_aircraft_conditions['result']
        }
        # Виды катастроф
        all_aviation_accident_types = (
            AviationAccidentTypes('aviation_accident_types')
            .get_rows_all_foreign().get_json()
        )
        if all_aviation_accident_types['error']:
            return jsonify(all_aviation_accident_types)
        field_values |= {
            'disaster_accident': all_aviation_accident_types['result']
        }

        return jsonify(field_values)

    def update(self, data: Dict[str, Any]) -> Response:
        update_photo_sql = ''
        if data['photo_of_result'] is not None:
            update_photo_sql = 'photo_of_result = %s, '
        sql = f"""
        UPDATE Disasters
        SET
            {update_photo_sql}
            disaster_datetime = %s,
            flight_type = %s, flight_number = %s,
            aircraft_model_type = %s, engine_model_type = %s,
            operator = %s, registration_code = %s,
            departure_place = %s, departure_date = %s,
            destination_place = %s, destination_date = %s,
            crew_survived = %s, crew_fatalities = %s,
            passengers_survived = %s, passengers_fatalities = %s,
            temperature = %s, pressure = %s,
            weather_condition = %s, wind_speed = %s,
            country = %s, latitude = %s,
            longitude = %s, height = %s,
            flight_phase = %s, aircraft_condition = %s,
            location_description = %s, 
            disaster_accident = %s, accident_description = %s
        WHERE id = %s;
        """
        tupled_data = (
            data['disaster_datetime'],
            data['flight_type'], data['flight_number'],
            data['aircraft_model_type'], data['engine_model_type'],
            data['operator'], data['registration_code'],
            data['departure_place'], data['departure_date'],
            data['destination_place'], data['destination_date'],
            data['crew_survived'], data['crew_fatalities'],
            data['passengers_survived'],
            data['passengers_fatalities'],
            data['temperature'], data['pressure'],
            data['weather_condition'], data['wind_speed'],
            data['country'], data['latitude'],
            data['longitude'], data['height'],
            data['flight_phase'], data['aircraft_condition'],
            data['location_description'],
            data['disaster_accident'], data['accident_description'],
            data['row_id']
        )
        if data['photo_of_result'] is not None:
            tupled_data = (data['photo_of_result'],) + tupled_data
        res = Base.create_or_update_row_by_sql(sql, tupled_data)
        return jsonify(res)

    def get_empty(self) -> Dict[str, str]:
        return {
            'disaster_datetime': '',
            'flight_type': '', 'flight_number': '',
            'aircraft_model_type': '', 'engine_model_type': '',
            'operator': '', 'registration_code': '',
            'departure_place': '', 'departure_date': '',
            'destination_place': '', 'destination_date': '',
            'crew_survived': '', 'crew_fatalities': '',
            'passengers_survived': '', 'passengers_fatalities': '',
            'temperature': '', 'pressure': '',
            'weather_condition': '', 'wind_speed': '',
            'country': '', 'latitude': '',
            'longitude': '', 'height': '',
            'flight_phase': '', 'aircraft_condition': '',
            'disaster_accident': '', 'location_description': '',
            'accident_description': '', 'photo_of_result': ''
        }

    def create(self, data: Dict[str, Any]) -> Response:
        sql = f"""
        INSERT INTO Disasters(
            disaster_datetime,
            flight_type, flight_number,
            aircraft_model_type, engine_model_type,
            operator, registration_code,
            departure_place, departure_date,
            destination_place, destination_date,
            crew_survived, crew_fatalities,
            passengers_survived, passengers_fatalities,
            temperature, pressure,
            weather_condition, wind_speed,
            country, latitude,
            longitude, height,
            flight_phase, aircraft_condition,
            disaster_accident, location_description,
            accident_description, photo_of_result
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        );
        """
        tupled_data = (
            data['disaster_datetime'],
            data['flight_type'], data['flight_number'],
            data['aircraft_model_type'], data['engine_model_type'],
            data['operator'], data['registration_code'],
            data['departure_place'], data['departure_date'],
            data['destination_place'], data['destination_date'],
            data['crew_survived'], data['crew_fatalities'],
            data['passengers_survived'],
            data['passengers_fatalities'],
            data['temperature'], data['pressure'],
            data['weather_condition'], data['wind_speed'],
            data['country'], data['latitude'],
            data['longitude'], data['height'],
            data['flight_phase'], data['aircraft_condition'],
            data['disaster_accident'], data['location_description'],
            data['accident_description'], data['photo_of_result']
        )
        res = Base.create_or_update_row_by_sql(sql, tupled_data, is_create=True)
        return jsonify(res)

    def delete(self, row_id: str) -> Response:
        sql = f"""
            DELETE FROM Disasters WHERE id = {row_id};
        """
        res = Base.delete_by_sql(sql)
        return jsonify(res)

    def get_filters(
        self, filters: Dict[str, Any], find: Dict[str, Any]
    ) -> str:
        filters_list = []
        # обычные данные, полученные с input преобразуются в простую строку
        if filters['min_datetime'] != '':
            filters_list.append(
                f"d.disaster_datetime >= '{filters['min_datetime']}'"
            )
        if filters['max_datetime'] != '':
            filters_list.append(
                f"d.disaster_datetime <= '{filters['max_datetime']}'"
            )
        # Если данные пришли списком из множества значений по внешнему полю, то
        # нужно их циклически преобразовать к строке с подзапросом
        if filters['flight_type']:
            s = ("d.flight_type in (select id "
                 "from flight_types where flight_type in (")
            for elem in filters['flight_type']:
                s += f"'{elem}', "
            filters_list.append(s[:-2] + '))')
        if filters['operator']:
            s = ("d.operator in (select id from "
                 "operators where operator_name in (")
            for elem in filters['operator']:
                s += f"'{elem}', "
            filters_list.append(s[:-2] + '))')
        if filters['aircraft_model_type']:
            s = ("d.aircraft_model_type in (select id from "
                 "aircraft_types where model_name in (")
            for elem in filters['aircraft_model_type']:
                s += f"'{elem}', "
            filters_list.append(s[:-2] + '))')
        if filters['engine_model_type']:
            s = ("d.engine_model_type in (select id "
                 "from engine_types where model_name in (")
            for elem in filters['engine_model_type']:
                s += f"'{elem}', "
            filters_list.append(s[:-2] + '))')
        if filters['departure_place'] != '':
            filters_list.append(
                f"d.departure_place = ("
                f"select id from airports "
                f"where airport_name = '{filters['departure_place']}')"
            )
        if filters['destination_place'] != '':
            filters_list.append(
                f"d.destination_place = ("
                f"select id from airports "
                f"where airport_name = '{filters['destination_place']}')"
            )
        if filters['is_any_crew_dead'] != '':
            if filters['is_any_crew_dead'] == 'Нет':
                filters_list.append(
                    f'd.crew_fatalities = 0'
                )
            else:
                filters_list.append(
                    f'd.crew_fatalities > 0'
                )
        if filters['is_any_passengers_dead'] != '':
            if filters['is_any_passengers_dead'] == 'Нет':
                filters_list.append(
                    f'd.passengers_fatalities = 0'
                )
            else:
                filters_list.append(
                    f'd.passengers_fatalities > 0'
                )
        if filters['temperature_min'] != '':
            filters_list.append(f'd.temperature >= {filters["temperature_min"]}')
        if filters['temperature_max'] != '':
            filters_list.append(f'd.temperature <= {filters["temperature_max"]}')
        if filters['pressure_min'] != '':
            filters_list.append(f'd.pressure >= {filters["pressure_min"]}')
        if filters['pressure_max'] != '':
            filters_list.append(f'd.pressure <= {filters["pressure_max"]}')
        if filters['weather_condition']:
            s = ("d.weather_condition in (select id "
                 "from weather_conditions where condition_name in (")
            for elem in filters['weather_condition']:
                s += f"'{elem}', "
            filters_list.append(s[:-2] + '))')
        if filters['country']:
            s = ("d.country in (select id "
                 "from countries where country_name in (")
            for elem in filters['country']:
                s += f"'{elem}', "
            filters_list.append(s[:-2] + '))')
        if filters['flight_phase']:
            s = ("d.flight_phase in (select id "
                 "from flight_phases where phase_name in (")
            for elem in filters['flight_phase']:
                s += f"'{elem}', "
            filters_list.append(s[:-2] + '))')
        if filters['aircraft_condition']:
            s = ("d.aircraft_condition in (select id "
                 "from aircraft_conditions ac where ac.condition_name in (")
            for elem in filters['aircraft_condition']:
                s += f"'{elem}', "
            filters_list.append(s[:-2] + '))')
        if filters['disaster_accident']:
            s = ("d.disaster_accident in (select id "
                 "from aviation_accident_types where accident_type in (")
            for elem in filters['disaster_accident']:
                s += f"'{elem}', "
            filters_list.append(s[:-2] + '))')
        find_str = ''
        if find['table_name'] == self.table_name:
            find_str = (f"(LOCATE('{find['value']}', flight_number) or "
                        f"LOCATE('{find['value']}', registration_code) or "
                        f"LOCATE('{find['value']}', accident_description) or "
                        f"LOCATE('{find['value']}', location_description)) ")

        if filters_list and find_str:
            return 'where ' + ' and '.join(filters_list) + 'and' + find_str
        elif not filters_list and find_str:
            return 'where ' + find_str
        elif filters_list and not find_str:
            return 'where ' + ' and '.join(filters_list)
        else:
            return ''

    @staticmethod
    def get_report_all(
        filters_str: str, field_name: str, sub_select_sql: str
    ) -> Response:
        """
        Функция извлечения данных по полям и фильтрам переданным в неё
        :param filters_str: Фильтры на языке sql
        :param field_name: Поле, по которому необходимо сгруппировать данные
        :param sub_select_sql: Отдельное имя поля на языке sql в select
        :return: Статус операции и извлеченные данные
        """
        sql = f"""
        SELECT
            {sub_select_sql} 
            count(*) as 'Общее число катастроф',
            max(crew_fatalities) 
            as 'Максимальное число погибших среди экипажа',
            max(crew_survived) 
            as 'Максимальное число выживших среди экипажа',
            max(passengers_fatalities) 
            as 'Максимальное число погибших среди пассажиров',
            max(passengers_survived) 
            as 'Максимальное число погибших среди пассажиров',
            round(avg(
                crew_survived / (crew_survived + crew_fatalities)
                ), 2) * 100
            as 'Средний процент выживаемости среди экипажа',
            ROUND(avg(passengers_survived /
                (passengers_survived + passengers_fatalities)
            ), 2) * 100 as 'Средний процент выживаемости среди пассажиров'
        FROM
            Disasters d
        {filters_str}
        GROUP BY 
            {field_name};
        """
        res = Base.get_rows_by_sql(sql)
        return jsonify(res)

    @staticmethod
    def get_report_worst(filters_str: str) -> Response:
        """
        Функция получающая данные о наихудших катастрофах
        :param filters_str: Фильтры отсекающие ненужные нам в статистике строки
        :return: Статус операции и извлеченные данные
        """
        sql = f"""
        SELECT
            id as id,
            flight_number as 'Номер полета(ссылка)', 
            DATE_FORMAT(disaster_datetime, '%d-%m-%Y %H:%i:%s') 
            as 'Дата катастрофы',
            crew_fatalities as 'Количество жертв среди экипажа', 
            crew_survived as 'Количество выживших среди экипажа',
            passengers_fatalities as 'Количество жертв среди пассажиров', 
            passengers_survived as 'Количество выживших среди пассажиров'
        FROM
            Disasters d
        {filters_str}
        ORDER BY crew_fatalities desc, passengers_fatalities desc
        LIMIT 25;
        """
        res = Base.get_rows_by_sql(sql)
        return jsonify(res)
