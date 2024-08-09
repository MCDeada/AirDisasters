from typing import Any, Dict, List, Optional

from interfaces.base import Base
from table_consts import tables_fields, disasters_filters_meta
import re
from datetime import datetime
from dateutil import parser
from flask import jsonify, Response


class CheckErrors:

    @staticmethod
    def is_valid_page_number(
        table_name: str, page_number: str, filters_str: str = ''
    ) -> Response:
        """
        Метод проверки корректности номера страницы в зависимости от имени таблицы
        :param table_name: имя таблицы
        :param page_number: номер страницы
        :param filters_str: фильтр катастроф, если он необходим
        :return: (False, ошибка) если была обнаружена ошибка
                 (True, None) если ошибок не найдено
        """
        error = False
        rows_count = 0
        # Проверка, что переданный номер страницы является целым числом больше 0
        try:
            page_number = int(page_number)
            if page_number < 1:
                raise Exception
        except Exception:
            error = 'Номер страницы может быть только целым числом больше 0'
        if not error:
            # Максимальное число строк с учетом фильтров
            rows_count_dt = Base().get_rows_count(table_name, filters_str).get_json()
            # Если получение общего числа записей по фильтрам прошло с ошибкой
            if rows_count_dt['error']:
                error = f'Ошибка при получении общего числа записей в {table_name}'
            # Если номер страницы превышает максимальное по данным фильтрам
            elif rows_count_dt['result']['count'] < (int(page_number) - 1) * 10:
                error = f'Нет данных для страницы номер {page_number}'
            # Иначе ошибки нет и надо сохранить общее число строк
            else:
                rows_count = rows_count_dt['result']['count']
        return jsonify({'error': error, 'total_rows': rows_count})

    @staticmethod
    def is_is_valid_id(row_id: str) -> Response:
        """
        Метод проверяющий, что строка может быть первичным численным ключом
        :param row_id: потенциальный номер записи
        :return:
        """
        error = False
        try:
            row_id = int(row_id)
            if row_id < 1:
                raise Exception
        except Exception:
            error = 'Номер записи должен быть целым числом больше 0'

        return jsonify({'error': error})

    def check_fields(
        self,
        row_data: Dict[str, Any],
        table_name: str,
        foreign_fields_values: Dict[str, Any],
        row_data_old: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """
        Функция проверки полей строки
        :param row_data: словарь с данными записи для проверки
        :param table_name: имя таблицы
        :param foreign_fields_values: данные с возможными
            значениями для внешних полей
        :param row_data_old: старые значения
        :return: список ошибок
        """
        errors = []
        if not row_data:
            return ["Ошибка. Запрос не содержит данных"]
        # получение перечня всех полей с их ограничениями
        fields_info = tables_fields[table_name]
        for key, value in row_data.items():
            # если поле не встречается в словаре с ограничениями
            if key not in fields_info:
                continue
            # Определение конкретных ограничений одного проверяемого поля
            foreign_data = foreign_fields_values.get(key, '{}')
            field_info = fields_info[key]
            # Если поле пусто, но по базе оно не может быть пусто
            if not field_info.get('is_null', True) and value is None:
                errors.append(
                    f'Поле «{field_info["header"]}» должно быть не пусто'
                )
                continue
            # Если поле пусто и по базе оно может быть пусто
            if field_info.get('is_null', False) and value is None:
                continue
            # Если значение поля превышает максимальную длину
            if (
                field_info.get('max_length', False) and
                len(value) > field_info['max_length']
            ):
                errors.append(
                    f'Значение поля «{field_info["header"]}» '
                    f'превышает ограничение в {field_info["max_length"]} символов'
                )
            # Если значение поля не подходит под шаблон
            if (
                field_info.get('type', False) and
                field_info['type'] == 'text' and
                field_info.get('text_regx', False) and
                not re.fullmatch(field_info['text_regx'], value)
            ):
                errors.append(
                    f'Поле «{field_info["header"]}» не удовлетворяет ограничениям'
                )
            # Если значение поля не уникально для этой таблицы
            if (
                field_info.get('is_unique', False) and
                not Base().is_unique_value(table_name, key, value)
            ):
                if table_name == 'users':
                    errors.append(
                        f'Введенное значение поля «{field_info["header"]}» уже занято'
                    )
                else:
                    if row_data_old is None or row_data_old is not None and row_data_old[key] != value:
                        errors.append(
                            f'Поле «{field_info["header"]}» должно быть уникальным'
                        )
            # Если значение поля должно быть датой или датой со временем
            if (
                field_info.get('type', False) and
                field_info['type'] in ['date', 'datetime_local']
            ):
                val = None
                try:
                    val = parser.parse(value)
                except Exception:
                    errors.append(
                        f'Поле «{field_info["header"]}» недопустимый формат даты'
                    )
                if val is not None and val > datetime.now():
                    errors.append(
                        f'Дата «{field_info["header"]}» не может быть больше текущей'
                    )
            # Если поле должно принимать значения из некоторой таблицы,
            # на которую ссылается
            if (
                field_info.get('display', False) and
                field_info['display'] == 'input_select' and
                value not in foreign_data
            ):
                errors.append(
                    f'Значение поля «{field_info["header"]}» '
                    f'отсутствует в соответствующем словаре'
                )
            # Проверка целочисленного поля
            if (
                field_info.get('type', False) and
                field_info['type'] == 'number' and
                field_info.get('number', False) and
                field_info['number'] == 'int'
            ):
                if (
                    field_info.get('max_value', False) and
                    isinstance(field_info.get('min_value', False), int)
                ):
                    val = None
                    try:
                        val = int(value)
                    except Exception:
                        errors.append(
                            f'Значение поля «{field_info["header"]}» '
                            f'должно быть целым числом'
                        )
                    # Проверка максимального и минимального ограничений
                    if (
                        val is not None and
                        (val > field_info['max_value'] or
                         val < field_info['min_value'])
                    ):
                        errors.append(
                            f'Значение поля «{field_info["header"]}» '
                            f'должно быть в пределах '
                            f'[{field_info["min_value"]}; '
                            f'{field_info["max_value"]}]'
                        )
                # Если это численное поле является внешним ключом, но не
                # имеет недопустимое значение
                elif value not in foreign_data:
                    errors.append(
                        f'Значение поля «{field_info["header"]}» '
                        f'отсутствует в соответствующем словаре'
                    )
            # Проверка поля с плавающей точкой
            if (
                field_info.get('type', False) and
                field_info['type'] == 'number' and
                field_info.get('number', False) and
                field_info['number'] == 'float'
            ):
                val = None
                try:
                    val = float(value)
                except Exception:
                    errors.append(
                        f'Значение поля «{field_info["header"]}» '
                        f'должно быть целым числом'
                    )
                # Проверка ограничению минимальности и максимальности
                if (
                    val is not None and
                    (val > field_info['max_value'] or
                     val < field_info['min_value'])
                ):
                    errors.append(
                        f'Значение поля «{field_info["header"]}» '
                        f'должно быть в пределах '
                        f'[{field_info["min_value"]}; '
                        f'{field_info["max_value"]}]'
                    )

        return errors

    def is_valid_filter(
        self, data: str, field_name: str, valid_values_dt: Dict[str, Any]
    ) -> List[str]:
        """
        Функция, проверяющая значение введенное в одно из полей
        :param data: Значение
        :param field_name: Имя поля
        :param valid_values_dt: Допустимые значения для поля-внешнего ключа
        :return: Ошибка помещенная в список или пустой список, если ошибки нет
        """
        errors = []
        valid_values = []
        if disasters_filters_meta[field_name]['type'] == 'select':
            valid_values = list(valid_values_dt.values())
        elif disasters_filters_meta[field_name]['type'] == 'input_select':
            valid_values = list(valid_values_dt.keys())
        if data not in valid_values:
            errors.append(
                f"Значение '{data}' для поля '{field_name}' "
                f"нет в базе данных"
            )

        return errors

    def is_valid_filters(
        self, data: Dict[str, Any], valid_values: Dict[str, Any]
    ) -> List[str]:
        """
        Проверка значений введенных в форму фильтров.
        :param data: Словарь значений
        :param valid_values: Словарь, где имени поля
        соответствуют допустимые значения
        :return: Список ошибок или пустой список, если ошибок нет
        """
        data_result = {}
        errors = []
        float_fields_error = {
            'temperature_min': '', 'temperature_max': '',
            'pressure_min': '', 'pressure_max': ''
        }
        for field in data:
            if (
                field not in disasters_filters_meta or
                not disasters_filters_meta[field]['in_list']
            ):
                continue
            data_result[field] = data[field]
            # Если значение поля не пустое
            if data[field] != '':
                # Для выпадающих списков, нужно проверить, что значение
                # принадлежит соответствующему списку
                if (
                    field in disasters_filters_meta and
                    (disasters_filters_meta[field]['type'] == 'input_select' or
                     disasters_filters_meta[field]['type'] == 'select')
                ):
                    if (
                        field in valid_values and
                        data[field] not in valid_values[field]
                    ):
                        errors.append(
                            f"Значение '{data[field]}' для поля '{field}' "
                            f"нет в базе данных"
                        )
                # Если значение должно быть числом с плавающей точкой
                elif (
                    field in disasters_filters_meta and
                    disasters_filters_meta[field]['type'] == 'float'
                ):
                    val = None
                    try:
                        val = float(data[field])
                    except Exception:
                        errors.append(
                            f"Значение '{data[field]}' для поля '{field}' "
                            f"должно быть числом"
                        )
                    # Если оно действительно число с плавающей точкой, то
                    # нужно проверить укладывается ли оно в
                    # область допустимых значений
                    if val is not None:
                        min_val = disasters_filters_meta[field]['min']
                        max_val = disasters_filters_meta[field]['max']
                        if val < min_val or val > max_val:
                            errors.append(f"Поле '{field}' должно быть "
                                          f"в пределах [{min_val}; {max_val}]")
        # отдельно проверяется, что введенное значение максимальной температуры
        # не меньше, чем введенное минимальное
        if (
            'temperature_min' not in float_fields_error and
            'temperature_max' not in float_fields_error
        ):
            temperature_min = float(data['temperature_min'])
            temperature_max = float(data['temperature_max'])
            if temperature_min >= temperature_max:
                errors.append(
                    f"Нижняя граница температуры должна "
                    f"быть меньше верхней границы"
                )
        # Аналогично для давления
        if (
            'pressure_min' not in float_fields_error and
            'pressure_max' not in float_fields_error
        ):
            pressure_min = float(data['pressure_min'])
            pressure_max = float(data['pressure_max'])
            if pressure_min >= pressure_max:
                errors.append(
                    f"Нижняя граница давления должна "
                    f"быть меньше верхней границы"
                )
        # Проверка дат между собой
        if data['min_datetime'] != '' and data['max_datetime'] != '':
            min_date = parser.parse(data["min_datetime"]).date()
            max_date = parser.parse(data["max_datetime"]).date()
            if min_date >= max_date:
                errors.append("Дата начала дапазона должна "
                              "быть меньше даты конца диапазона")

        data = data_result
        return errors
