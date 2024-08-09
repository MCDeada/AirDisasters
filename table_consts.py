# словарь с тем как соотносятся имена маршрутов с таблицами
table_names = [
    'weather_conditions', 'flight_phases', 'aircraft_conditions', 'countries',
    'aviation_accident_types', 'airports', 'flight_types',
    'aircraft_types', 'engine_types', 'engines_types_to_aircraft_types',
    'operators', 'disasters', 'filters',
    'users_actions', 'history_of_users', 'users', 'roles'
]

# Общее обозначение в браузере пустых данных
no_data = 'Нет данных'

# Словарь соответствия имен таблиц в бд и их имен в браузере
table_names_dt = {
    'weather_conditions': 'Виды погодных условий',
    'flight_phases': 'Фазы полета',
    'aircraft_conditions': 'Состояния самолета после аварии',
    'countries': 'Страны',
    'aviation_accident_types': 'Типы катастроф',
    'airports': 'Аэропорты',
    'flight_types': 'Типы полетов',
    'aircraft_types': 'Модели самолетов',
    'engine_types': 'Модели двигателей',
    'engines_types_to_aircraft_types': 'Соотношение двигателей с самолетами',
    'operators': 'Авиаперевозчики',
    'disasters': 'Катастрофы',
    'filters': 'Фильтры',
    'users_actions': 'Возможные действия пользователей',
    'history_of_users': 'История действий пользователей',
    'users': 'Данные о пользователях',
    'roles': 'Роли пользователей',
}


# Словарь с заголовками для отображения у шаблонов
path_titles = {
    # справочники
    'weather_conditions': {
        'title_get': 'Данные о погодных условиях',
        'title_update': 'Изменение записи о погодных условиях',
        'title_create': 'Создание записи о погодных условиях',
        'active': False
    },
    'flight_phases': {
        'title_get': 'Данные о стадиях полета',
        'title_update': 'Изменение записи о стадии полета',
        'title_create': 'Создание записи о стадии полета',
        'active': False
    },
    'aircraft_conditions': {
        'title_get': 'Данные о возможных состояниях самолетов',
        'title_update': 'Изменение записи о состоянии самолета',
        'title_create': 'Создание записи о состоянии самолета',
        'active': False
    },
    'aviation_accident_types': {
        'title_get': 'Данные о типах инцидентов',
        'title_update': 'Изменение записи о типе инцидента',
        'title_create': 'Создание записи о типе инцидента',
        'active': False
    },
    'countries': {
        'title_get': 'Данные о странах',
        'title_update': 'Изменение записи страны',
        'title_create': 'Создание записи страны',
        'active': False
    },
    'flight_types': {
        'title_get': 'Данные о видах полетов',
        'title_update': 'Изменение записи вида полета',
        'title_create': 'Создание записи вида полета',
        'active': False
    },
    'airports': {
        'title_get': 'Данные об аэропортах',
        'title_update': 'Изменение записи аэропорта',
        'title_create': 'Создание записи аэропорта',
        'active': False
    },
    # описание самолетов
    'aircraft_types': {
        'title_get': 'Данные о моделях самолетов',
        'title_update': 'Изменение записи о модели самолета',
        'title_create': 'Создание записи о модели самолета',
        'active': True
    },
    'engine_types': {
        'title_get': 'Данные о моделях двигателей',
        'title_update': 'Изменение записи о модели двигателя',
        'title_create': 'Создание записи о модели двигателя',
        'active': False
    },
    'engines_types_to_aircraft_types': {
        'title_get': 'Данные о соотношении двигателей и самолетов',
        'title_update': 'Изменение записи о соотношении двигателей и самолетов',
        'title_create': 'Создание записи о соотношении двигателей и самолетов',
        'active': False
    },
    'operators': {
        'title_get': 'Данные об операторах',
        'title_update': 'Изменение записи о операторе',
        'title_create': 'Создание записи о операторе',
        'active': False
    },
    'disasters': {
        'title_get': 'Данные о катастрофах',
        'title_update': 'Изменение записи о катастрофе',
        'title_create': 'Создание записи о катастрофе',
        'active': True
    },
    # Пользователи
    'users_actions': {
        'title_get': 'Данные о возможных действиях пользователей',
        'title_update': 'Изменение записи о возможном действии пользователя',
        'title_create': 'Создание записи о возможном действии пользователя',
        'active': False
    },
    'history_of_users': {
        'title_get': 'Данные о фактических действиях пользователей',
        'title_update': 'Изменение записи о фактическом действии пользователя',
        'title_create': 'Создание записи о фактическом действии пользователя',
        'active': True
    },
    'users': {
        'title_get': 'Данные о пользователях',
        'title_update': 'Изменение записи о пользователе',
        'title_create': 'Создание записи о пользователе',
        'active': False
    },
    'roles': {
        'title_get': 'Данные о ролях пользователей',
        'title_update': 'Изменение записи о роли пользователя',
        'title_create': 'Создание записи о роли пользователя',
        'active': False
    },
}

# Словарь, в котором имени таблицы соответствует перечень полей.
# У каждого поля указано:
#   header - имя поля в шаблоне,
#   title - подсказка, при наведении на поле. Содержит описание ограничений
#   display - формат отображения элементов input в шаблоне,
#   type - какого типа должен быть элемент <input>,
#   max_length - максимальная длина для тестовых полей,
#   text_regx - регулярное выражение для тестовых полей,
#   is_unique - Нужна ли проверка поля на уникальность при проверке полей
#   max_value, min_value - ограничение для численных полей и дат
#   in_list - True, если отображается на форме.
tables_fields = {
    'weather_conditions': {
        'condition_name': {
            'header': 'Вид погодных условий',
            'title': 'Обязательное поле. Не более 30 символов. '
                     'Только кириллица, латиница, пробелы и знак тире',
            'display': 'input',
            'is_null': False,
            'type': 'text',
            'max_length': 30,
            'text_regx': r'^[а-яА-Я]+[а-яА-Я\s\-]*$',
            'is_unique': True,
            'max_value': '',
            'min_value': '',
            'in_list': True,
        }
    },
    'flight_phases': {
        'phase_name': {
            'header': 'Стадия полета',
            'title': 'Обязательное поле. Не более 40 символов. '
                     'Только кириллица, латиница, пробелы и знак тире',
            'display': 'input',
            'is_null': False,
            'type': 'text',
            'max_length': 40,
            'text_regx': r'^[а-яА-Я]+[а-яА-Я\s\-]*$',
            'is_unique': True,
            'max_value': '',
            'min_value': '',
            'in_list': True,
        }
    },
    'aircraft_conditions': {
        'condition_name': {
            'header': 'Состояния самолета',
            'title': 'Обязательное поле. Не более 40 символов. '
                     'Только кириллица, латиница, пробелы и знак тире',
            'display': 'input',
            'is_null': False,
            'type': 'text',
            'max_length': 40,
            'text_regx': r'^[а-яА-Яa-zA-Z]+[а-яА-Яa-zA-Z\s\-]*$',
            'is_unique': True,
            'max_value': '',
            'min_value': '',
            'in_list': True,
        },
    },
    'aviation_accident_types': {
        'accident_type': {
            'header': 'Вид катастрофы',
            'title': 'Обязательное поле. Не более 80 символов. '
                     'Только кириллица, латиница, пробелы и знак тире',
            'display': 'input',
            'is_null': False,
            'type': 'text',
            'max_length': 80,
            'text_regx': r'^[а-яА-Яa-zA-Z]+[а-яА-Яa-zA-Z\s\-]*$',
            'is_unique': True,
            'max_value': '',
            'min_value': '',
            'in_list': True,
        }
    },
    'countries': {
        'country_name': {
            'header': 'Наименование страны',
            'title': 'Обязательное поле. Не более 80 символов. '
                     'Только кириллица, латиница, пробелы и знак тире',
            'display': 'input',
            'is_null': False,
            'type': 'text',
            'max_length': 80,
            'text_regx': r'^[а-яА-Яa-zA-Z]+[а-яА-Яa-zA-Z\s\-]*$',
            'is_unique': True,
            'max_value': '',
            'min_value': '',
            'in_list': True,
        }
    },
    'flight_types': {
        'flight_type': {
            'header': 'Тип полета',
            'title': 'Обязательное поле. Не более 70 символов. '
                     'Только кириллица, латиница, пробелы и знак тире',
            'display': 'input',
            'is_null': False,
            'type': 'text',
            'max_length': 70,
            'text_regx': r'^[а-яА-Яa-zA-Z]+[а-яА-Яa-zA-Z\s\-]*$',
            'is_unique': True,
            'max_value': '',
            'min_value': '',
            'in_list': True,
        }
    },
    'airports': {
        'airport_name': {
            'header': 'Наименование аэропорта',
            'title': 'Обязательное поле. Не более 80 символов. '
                     'Только кириллица, латиница, пробелы и знак тире',
            'display': 'input',
            'is_null': False,
            'type': 'text',
            'max_length': 80,
            'text_regx': r'^[а-яА-Яa-zA-Z]+[а-яА-Яa-zA-Z\s\-]*$',
            'is_unique': False,
            'max_value': '',
            'min_value': '',
            'in_list': True,
        },
        'ICAO_code': {
            'header': 'Код аэропорта',
            'title': 'Обязательное поле. От 2 до 4 символов. '
                     'Только заглавные буквы латинского алфавита',
            'display': 'input',
            'is_null': False,
            'type': 'text',
            'max_length': 10,
            'text_regx': r'^[A-Z]{2,4}$',
            'is_unique': True,
            'max_value': '',
            'min_value': '',
            'in_list': True,
        },
        'country': {
            'header': 'Страна базирования',
            'title': 'Обязательное поле. Не более 80 символов. '
                     'Должно быть из предлагаемых на выбор',
            'display': 'input_select',
            'is_null': False,
            'type': 'text',
            'max_length': 80,
            'in_list': True,
        },
        'latitude': {
            'header': 'Широта',
            'title': 'Необязательное поле. Число из диапазона [-90;90]',
            'display': 'input',
            'is_null': True,
            'type': 'number',
            'number': 'float',
            'max_value': 90,
            'min_value': -90,
            'in_list': True,
        },
        'longitude': {
            'header': 'Долгота',
            'title': 'Необязательное поле. Число из диапазона [-180;180]',
            'display': 'input',
            'is_null': True,
            'type': 'number',
            'number': 'float',
            'max_value': 180,
            'min_value': -180,
            'in_list': True,
        },
        'height': {
            'header': 'Высота',
            'title': 'Необязательное поле. Число из диапазона [-433;15000]',
            'display': 'input',
            'is_null': True,
            'type': 'number',
            'number': 'float',
            'max_value': 15000,
            'min_value': -433,
            'in_list': True,
        }
    },
    # техника
    'aircraft_types': {
        'model_name': {
            'header': 'Наименование модели',
            'title': 'Обязательное поле. Не более 80 символов. Только '
                     'кириллица, латиница, цифры 0-9, пробелы и знак тире',
            'display': 'input',
            'is_null': False,
            'type': 'text',
            'max_length': 80,
            'text_regx': r'^[а-яА-Яa-zA-Z]+[а-яА-Яa-zA-Z0-9\s\-]*$',
            'is_unique': True,
            'max_value': '',
            'min_value': '',
            'in_list': True,
        },
        'first_flight': {
            'header': 'Дата первого полета',
            'title': 'Необязательное поле. '
                     'Дата из диапазона [1900-01-01; 2500-01-01]',
            'display': 'input',
            'is_null': True,
            'type': 'date',
            'max_value': '2500-01-01',
            'min_value': '1900-01-01',
            'in_list': True,
        },
        'last_flight': {
            'header': 'Дата последнего полета',
            'title': 'Необязательное поле. '
                     'Дата из диапазона [1900-01-01; 2500-01-01]',
            'display': 'input',
            'is_null': True,
            'type': 'date',
            'max_value': '2500-01-01',
            'min_value': '1900-01-01',
            'in_list': True,
        },
        'max_mass': {
            'header': 'Максимальная масса (т)',
            'title': 'Необязательное поле. Число из диапазона [1; 650]',
            'display': 'input',
            'is_null': True,
            'type': 'number',
            'number': 'float',
            'max_value': 650.0,
            'min_value': 1.0,
            'in_list': False,
        },
        'max_crew': {
            'header': 'Максимальное число экипажа',
            'title': 'Обязательное поле. Число из диапазона [1; 10]',
            'is_null': False,
            'display': 'input',
            'type': 'number',
            'number': 'int',
            'max_value': 10,
            'min_value': 1,
            'in_list': True,
        },
        'max_passengers': {
            'header': 'Максимальное число пассажиров',
            'title': 'Обязательное поле. Число из диапазона [0; 1000]',
            'is_null': False,
            'display': 'input',
            'type': 'number',
            'max_value': 1000,
            'min_value': 0,
            'in_list': True,
        },
        'length': {
            'header': 'Длина модели (м)',
            'title': 'Необязательное поле. Число из диапазона [3.5; 85]',
            'display': 'input',
            'is_null': True,
            'type': 'number',
            'number': 'float',
            'max_value': 85.0,
            'min_value': 3.5,
            'in_list': False,
        },
        'height': {
            'header': 'Высота модели (м)',
            'title': 'Необязательное поле. Число из диапазона [1; 30]',
            'display': 'input',
            'is_null': True,
            'type': 'number',
            'number': 'float',
            'max_value': 30,
            'min_value': 1,
            'in_list': False,
        },
        'wingspan': {
            'header': 'Размах крыла (м)',
            'title': 'Необязательное поле. Число из диапазона [4; 120]',
            'display': 'input',
            'is_null': True,
            'type': 'number',
            'number': 'float',
            'max_value': 120,
            'min_value': 4,
            'in_list': False,
        },
        'wing_area': {
            'header': 'Площадь крыла (кв. м)',
            'title': 'Необязательное поле. Число из диапазона [4; 550]',
            'display': 'input',
            'is_null': True,
            'type': 'number',
            'number': 'float',
            'max_value': 550,
            'min_value': 4,
            'in_list': False,
        },
        'fuselage_width': {
            'header': 'Ширина фюзеляжа (м)',
            'title': 'Необязательное поле. Число из диапазона [0.5; 10]',
            'display': 'input',
            'is_null': True,
            'type': 'number',
            'number': 'float',
            'max_value': 10,
            'min_value': 0.5,
            'in_list': False,
        },
        'interior_width': {
            'header': 'Ширина салона (м)',
            'title': 'Необязательное поле. Число из диапазона [0.5; 10]',
            'display': 'input',
            'is_null': True,
            'type': 'number',
            'number': 'float',
            'max_value': 10,
            'min_value': 0.5,
            'in_list': False,
        },
        'cruising_speed': {
            'header': 'Крейсерская скорость (км/ч)',
            'title': 'Необязательное поле. Число из диапазона [160; 3000]',
            'display': 'input',
            'is_null': True,
            'type': 'number',
            'number': 'float',
            'max_value': 3000,
            'min_value': 160,
            'in_list': False,
        },
        'runaway_range': {
            'header': 'Длина разбега (м)',
            'title': 'Необязательное поле. Число из диапазона [350; 12000]',
            'display': 'input',
            'is_null': True,
            'type': 'number',
            'number': 'float',
            'max_value': 1200,
            'min_value': 350,
            'in_list': False,
        },
        'max_flight_altitude': {
            'header': 'Максимальная высота полета (м)',
            'title': 'Необязательное поле. Число из диапазона [1000; 20000]',
            'display': 'input',
            'is_null': True,
            'type': 'number',
            'number': 'float',
            'max_value': 20000,
            'min_value': 1000,
            'in_list': False,
        }
    },
    'engine_types': {
        'model_name': {
            'header': 'Наименование модели',
            'title': 'Обязательное поле. Не более 50 символов. Только '
                     'кириллица, латиница, цифры 0-9, пробелы и знак тире',
            'display': 'input',
            'is_null': False,
            'type': 'text',
            'max_length': 50,
            'text_regx': r'^[а-яА-Яa-zA-Z]+[а-яА-Яa-zA-Z0-9\s\-]*$',
            'is_unique': True,
            'max_value': '',
            'min_value': '',
            'in_list': True,
        },
        'static_thrust': {
            'header': 'Мощность двигателя (кН)',
            'title': 'Необязательное поле. Число из диапазона [0.1; 570]',
            'display': 'input',
            'is_null': True,
            'type': 'number',
            'number': 'float',
            'max_value': 570,
            'min_value': 0.1,
            'in_list': True,
        },
        'mass': {
            'header': 'Масса двигателя (кг)',
            'title': 'Необязательное поле. Число из диапазона [0.1; 10000]',
            'display': 'input',
            'is_null': True,
            'type': 'number',
            'number': 'float',
            'max_value': 10000,
            'min_value': 0.1,
            'in_list': True,
        },
        'length': {
            'header': 'Длина движка (мм)',
            'title': 'Необязательное поле. Число из диапазона [250; 15000]',
            'display': 'input',
            'is_null': True,
            'type': 'number',
            'number': 'float',
            'max_value': 15000,
            'min_value': 250,
            'in_list': True,
        },
        'diameter': {
            'header': 'Диаметр движка (мм)',
            'title': 'Необязательное поле. Число из диапазона [100; 4500]',
            'display': 'input',
            'is_null': True,
            'type': 'number',
            'number': 'float',
            'max_value': 4500,
            'min_value': 100,
            'in_list': True,
        },
        'developed_in': {
            'header': 'Год окончания разработки',
            'title': 'Необязательное поле. '
                     'Дата из диапазона [1900-01-01; 2500-01-01]',
            'display': 'input',
            'is_null': True,
            'type': 'date',
            'max_value': '2500-01-01',
            'min_value': '1900-01-01',
            'in_list': True,
        }
    },
    'engines_types_to_aircraft_types': {
        'id_engine_type': {
            'header': 'Модель двигателя',
            'title': 'Обязательное поле. Не более 50 символов. '
                     'Должно быть из предлагаемых на выбор',
            'display': 'input_select',
            'is_null': False,
            'type': 'text',
            'max_length': 50,
            'in_list': True,
        },
        'id_aircraft_type': {
            'header': 'Модель самолета',
            'title': 'Обязательное поле. Не более 80 символов. '
                     'Должно быть из предлагаемых на выбор',
            'display': 'input_select',
            'is_null': False,
            'type': 'text',
            'max_length': 80,
            'in_list': True,
        },
    },
    # основные таблицы
    'operators': {
        'operator_name': {
            'header': 'Наименование авиакомпании',
            'title': 'Обязательное поле. Не более 80 символов. '
                     'Только кириллица, латиница, цифры, пробелы и знак тире',
            'display': 'input',
            'is_null': False,
            'type': 'text',
            'max_length': 80,
            'text_regx': r'^[а-яА-Яa-zA-Z]+[а-яА-Яa-zA-Z0-9\s\-]*$',
            'is_unique': True,
            'max_value': '',
            'min_value': '',
            'in_list': True,
        },
        'country': {
            'header': 'Страна регистрации',
            'title': 'Обязательное поле. Не более 80 символов. '
                     'Должно быть из предлагаемых на выбор',
            'display': 'input_select',
            'is_null': False,
            'type': 'text',
            'max_length': 80,
            'in_list': True,
        },
        'ICAO_code': {
            'header': 'Код авиаперевозчика',
            'title': 'Обязательное поле. От 2 до 4 символов. '
                     'Только заглавные буквы латинского алфавита',
            'display': 'input',
            'is_null': False,
            'type': 'text',
            'max_length': 10,
            'text_regx': r'^[A-Z]{2,4}$',
            'is_unique': True,
            'max_value': '',
            'min_value': '',
            'in_list': True,
        },
    },
    'disasters': {
        'disaster_datetime': {
            'header': 'Время и дата катастрофы',
            'title': 'Обязательное поле. '
                     'Дата из диапазона [1900-01-01; 2500-01-01]',
            'display': 'input',
            'is_null': False,
            'type': 'datetime-local',
            'max_value': '2500-01-01 00:00:00',
            'min_value': '1900-01-01 00:00:00',
            'in_list': True,
        },
        'aircraft_model_type': {
            'header': 'Модель самолета',
            'title': 'Обязательное поле. Не более 80 символов. '
                     'Должно быть из предлагаемых на выбор',
            'display': 'input_select',
            'is_null': False,
            'type': 'text',
            'max_length': 80,
            'in_list': False,
        },
        'engine_model_type': {
            'header': 'Модель двигателя',
            'title': 'Обязательное поле. Не более 50 символов. '
                     'Должно быть из предлагаемых на выбор',
            'display': 'input_select',
            'is_null': False,
            'type': 'text',
            'max_length': 50,
            'in_list': False,
        },
        'registration_code': {
            'header': 'Регистрационный знак воздушного судна',
            'title': 'Обязательное поле. Не более 6 символов. '
                     'Только заглавные латинские буквы формата AA-A[AA]',
            'display': 'input',
            'is_null': False,
            'type': 'text',
            'max_length': 40,
            'text_regx': r'^[A-Z][A-Z]-[A-Z0-9]{1,3}$',
            'max_value': '',
            'min_value': '',
            'in_list': False,
        },
        'flight_number': {
            'header': 'Код полета',
            'title': 'Необязательное поле. Не более 30 символов. '
                     'Только заглавные латинские буквы и цифры '
                     'формата A[AAA]-0[000]',
            'display': 'input',
            'is_null': True,
            'type': 'text',
            'max_length': 30,
            'text_regx': r'^[A-Z]{1,4}-[0-9]{1,4}$',
            'max_value': '',
            'min_value': '',
            'in_list': False,
        },
        'flight_type': {
            'header': 'Тип полета',
            'title': 'Необязательное поле. '
                     'Должно быть из предлагаемых на выбор',
            'display': 'select',
            'is_null': True,
            'type': 'number',
            'number': 'int',
            'in_list': False,
        },
        'operator': {
            'header': 'Наименование авиаперевозчика',
            'title': 'Необязательное поле. Не более 80 символов. '
                     'Должно быть из предлагаемых на выбор',
            'display': 'input_select',
            'is_null': True,
            'type': 'text',
            'max_length': 80,
            'in_list': False,
        },
        'departure_place': {
            'header': 'Наименование аэропорта отправления',
            'title': 'Необязательное поле. Не более 80 символов. '
                     'Должно быть из предлагаемых на выбор',
            'display': 'input_select',
            'is_null': True,
            'type': 'text',
            'max_length': 80,
            'in_list': False,
        },
        'departure_date': {
            'header': 'Время и дата отправления',
            'title': 'Необязательное поле. '
                     'Дата из диапазона [1900-01-01; 2500-01-01]',
            'display': 'input',
            'is_null': True,
            'type': 'datetime-local',
            'max_value': '2500-01-01 00:00:00',
            'min_value': '1900-01-01 00:00:00',
            'in_list': False,
        },
        'destination_place': {
            'header': 'Наименование аэропорта прибытия',
            'title': 'Необязательное поле. Не более 80 символов',
            'display': 'input_select',
            'is_null': True,
            'type': 'text',
            'max_length': 80,
            'in_list': False,
        },
        'destination_date': {
            'header': 'Время и дата прибытия',
            'title': 'Необязательное поле. '
                     'Дата из диапазона [1900-01-01; 2500-01-01]',
            'display': 'input',
            'is_null': True,
            'type': 'datetime-local',
            'max_value': '2500-01-01 00:00:00',
            'min_value': '1900-01-01 00:00:00',
            'in_list': False,
        },
        'crew_survived': {
            'header': 'Количество выживших членов экипажа',
            'title': 'Обязательное поле. Число из диапазона [0; 10]',
            'is_null': False,
            'display': 'input',
            'type': 'number',
            'number': 'int',
            'max_value': 10,
            'min_value': 0,
            'in_list': True,
        },
        'crew_fatalities': {
            'header': 'Количество погибших членов экипажа',
            'title': 'Обязательное поле. Число из диапазона [0; 10]',
            'is_null': False,
            'display': 'input',
            'type': 'number',
            'number': 'int',
            'max_value': 10,
            'min_value': 0,
            'in_list': True,
        },
        'passengers_survived': {
            'header': 'Количество выживших пассажиров',
            'title': 'Обязательное поле. Число из диапазона [0; 1000]',
            'is_null': False,
            'display': 'input',
            'type': 'number',
            'max_value': 1000,
            'min_value': 0,
            'in_list': True,
        },
        'passengers_fatalities': {
            'header': 'Количество погибших пассажиров',
            'title': 'Обязательное поле. Число из диапазона [0; 1000]',
            'is_null': False,
            'display': 'input',
            'type': 'number',
            'max_value': 1000,
            'min_value': 0,
            'in_list': True,
        },
        'temperature': {
            'header': 'Температура на момент аварии (градусы)',
            'title': 'Необязательное поле. Число из диапазона [-100; 100]',
            'display': 'input',
            'is_null': True,
            'type': 'number',
            'number': 'float',
            'max_value': 100,
            'min_value': -100,
            'in_list': False,
        },
        'pressure': {
            'header': 'Атмосферное давление (мм.рт.ст.)',
            'title': 'Необязательное поле. Число из диапазона [0; 825]',
            'display': 'input',
            'is_null': True,
            'type': 'number',
            'number': 'float',
            'max_value': 825,
            'min_value': 0,
            'in_list': False,
        },
        'weather_condition': {
            'header': 'Вид погодных условий',
            'title': 'Необязательное поле. '
                     'Должно быть из предлагаемых на выбор',
            'display': 'input_select',
            'is_null': False,
            'type': 'number',
            'number': 'int',
            'in_list': False,
        },
        'wind_speed': {
            'header': 'Скорость ветра (м/с)',
            'title': 'Необязательное поле. Число из диапазона [0; 100]',
            'display': 'input',
            'is_null': True,
            'type': 'number',
            'number': 'float',
            'max_value': 100,
            'min_value': 0,
            'in_list': False,
        },
        'country': {
            'header': 'Страна происшествия',
            'title': 'Обязательное поле. Не более 80 символов. '
                     'Должно быть из предлагаемых на выбор',
            'display': 'input_select',
            'is_null': False,
            'type': 'text',
            'max_length': 80,
            'in_list': True,
        },
        'latitude': {
            'header': 'Широта',
            'title': 'Необязательное поле. Число из диапазона [-90;90]',
            'display': 'input',
            'is_null': True,
            'type': 'number',
            'number': 'float',
            'max_value': 90,
            'min_value': -90,
            'in_list': False,
        },
        'longitude': {
            'header': 'Долгота',
            'title': 'Необязательное поле. Число из диапазона [-180;180]',
            'display': 'input',
            'is_null': True,
            'type': 'number',
            'number': 'float',
            'max_value': 180,
            'min_value': -180,
            'in_list': False,
        },
        'height': {
            'header': 'Высота',
            'title': 'Необязательное поле. Число из диапазона [-433;15000]',
            'display': 'input',
            'is_null': True,
            'type': 'number',
            'number': 'float',
            'max_value': 15000,
            'min_value': -433,
            'in_list': False,
        },
        'flight_phase': {
            'header': 'Фаза полета',
            'title': 'Обязательное поле. '
                     'Должно быть из предлагаемых на выбор',
            'display': 'select',
            'is_null': False,
            'type': 'number',
            'number': 'int',
            'in_list': True,
        },
        'aircraft_condition': {
            'header': 'Состояние самолета после аварии',
            'title': 'Обязательное поле. '
                     'Должно быть из предлагаемых на выбор',
            'display': 'select',
            'is_null': False,
            'type': 'number',
            'number': 'int',
            'in_list': False,
        },
        'disaster_accident': {
            'header': 'Тип происшествия',
            'title': 'Обязательное поле. '
                     'Должно быть из предлагаемых на выбор',
            'display': 'select',
            'is_null': False,
            'type': 'number',
            'number': 'int',
            'in_list': True,
        },
        'location_description': {
            'header': 'Развернутое описание места катастрофы',
            'title': 'Необязательное поле. Не более 3000 символов',
            'display': 'textarea',
            'is_null': True,
            'type': 'text',
            'max_length': 3000,
            'in_list': False,
        },
        'accident_description': {
            'header': 'Развернутое описание произошедшей катастрофы',
            'title': 'Необязательное поле. Не более 3000 символов',
            'display': 'textarea',
            'is_null': True,
            'type': 'text',
            'max_length': 3000,
            'in_list': False,
        },
        'photo_of_result': {
            'header': 'Фото произошедшей катастрофы',
            'title': 'Необязательное поле.',
            'is_null': True,
            'display': 'input',
            'type': 'file',
            'in_list': False,
        }
    },
    # таблицы пользователей
    'users_actions': {
        'action_name': {
            'header': 'Тип действия',
            'title': 'Обязательное поле. Не более 40 символов. '
                     'Только кириллица, латиница, пробелы и знак тире',
            'display': 'input',
            'is_null': False,
            'type': 'text',
            'max_length': 40,
            'text_regx': r'^[а-яА-Я]+[а-яА-Я\s\-]*$',
            'is_unique': True,
            'in_list': True,
        }
    },
    'users': {
        'user_name': {
            'header': 'Имя пользователя',
            'title': 'Обязательное поле. '
                     'Только кириллица, пробел и знак тире',
            'display': 'input',
            'is_null': False,
            'type': 'text',
            'max_length': 40,
            'text_regx': r'^[а-яА-Я]+[а-яА-Я\s\-]*$',
            'is_unique': False,
            'in_list': True,
        },
        'user_surname': {
            'header': 'Фамилия пользователя',
            'title': 'Обязательное поле. '
                     'Только кириллица, пробел и знак тире',
            'display': 'input',
            'is_null': False,
            'type': 'text',
            'max_length': 40,
            'text_regx': r'^[а-яА-Я]+[а-яА-Я\s\-]*$',
            'is_unique': False,
            'in_list': True,
        },
        'user_patronymic': {
            'header': 'Отчество пользователя',
            'title': 'Обязательное поле. '
                     'Только кириллица, пробел и знак тире',
            'display': 'input',
            'is_null': False,
            'type': 'text',
            'max_length': 40,
            'text_regx': r'^[а-яА-Я]+[а-яА-Я\s\-]*$',
            'is_unique': False,
            'in_list': True,
        },
        'login': {
            'header': 'Имя входа пользователя',
            'title': 'Обязательное поле. '
                     'Только латиница, цифры, знак "_" и знак "-". '
                     'От 5 до 40 символов',
            'display': 'input',
            'is_null': False,
            'type': 'text',
            'max_length': 40,
            'text_regx': r'^[a-zA-Z]+[a-zA-Z0-9\-\_]{4,40}$',
            'is_unique': True,
            'in_list': True,
        },
        'user_password': {
            'header': 'Пароль пользователя',
            'title': 'Обязательное поле. '
                     'Только латиница, цифры и знак тире. '
                     'От 10 до 40 символов',
            'display': 'input',
            'is_null': False,
            'type': 'text',
            'max_length': 40,
            'text_regx': r'^[a-zA-Z0-9\-]{10,40}$',
            'is_unique': False,
            'in_list': False,
        },
        'id_role': {
            'header': 'Роль пользователя',
            'title': 'Обязательное поле. '
                     'Должно быть из предлагаемых на выбор',
            'display': 'select',
            'is_null': False,
            'type': 'number',
            'number': 'int',
            'in_list': True,
        },
    },
    'history_of_users': {
        'user_id': {
            'header': 'Имя входа пользователя',
            'display': 'input',
            'type': 'number',
            'is_null': False,
            'in_list': True,
        },
        'user_action': {
            'header': 'Наименование действия',
            'display': 'input',
            'type': 'number',
            'is_null': False,
            'in_list': True,
        },
        'related_table': {
            'header': 'Таблица, с которой проведено действие',
            'display': 'input',
            'type': 'text',
            'is_null': True,
            'max_length': 100,
            'in_list': True,
        },
        'row_before_action': {
            'header': 'Строка до действия',
            'display': 'text',
            'is_null': True,
            'in_list': True,
        },
        'row_after_action': {
            'header': 'Строка после действия',
            'display': 'text',
            'is_null': True,
            'in_list': True,
        },
        'action_datetime': {
            'header': 'Время и дата действия',
            'display': 'input',
            'is_null': False,
            'type': 'datetime-local',
            'max_value': '2500-01-01',
            'min_value': '1900-01-01',
            'in_list': True,
        }
    },
    'roles': {
        'role_name': {
            'header': 'Наименование роли пользователя',
            'display': 'input',
            'type': 'text',
            'is_null': False,
            'max_length': 40,
            'in_list': True,
        }
    },
}

# Список, в котором имя поля фильтров связано с именами кнопок, чтобы
# Можно было по нажатой кнопке определить какое поле должно быть изменено
allowed_filters_actions = {
    'Выбрать тип полета': 'flight_type',
    'Исключить тип полета': 'flight_type',
    'Очистить выбранные типы полетов': 'flight_type',

    'Выбрать авиаперевозчика': 'operator',
    'Исключить авиаперевозчика': 'operator',
    'Очистить выбранных авиаперевозчиков': 'operator',

    'Выбрать модель самолета': 'aircraft_model_type',
    'Исключить модель самолета': 'aircraft_model_type',
    'Очистить выбранные модели самолетов': 'aircraft_model_type',

    'Выбрать модель двигателя': 'engine_model_type',
    'Исключить модель двигателя': 'engine_model_type',
    'Очистить выбранные модели двигателей': 'engine_model_type',

    'Выбрать вид погодных условий': 'weather_condition',
    'Исключить вид погодных условий': 'weather_condition',
    'Очистить выбранные погодные условия': 'weather_condition',

    'Выбрать страну происшествия': 'country',
    'Исключить страну происшествия': 'country',
    'Очистить выбранные страны происшествий': 'country',

    'Выбрать фазу полета': 'flight_phase',
    'Исключить фазу полета': 'flight_phase',
    'Очистить выбранные фазы полетов': 'flight_phase',

    'Выбрать состояние самолета': 'aircraft_condition',
    'Исключить состояние самолета': 'aircraft_condition',
    'Очистить выбранные состояния самолетов': 'aircraft_condition',

    'Выбрать тип катастрофы': 'disaster_accident',
    'Исключить тип катастрофы': 'disaster_accident',
    'Очистить выбранные типы катастроф': 'disaster_accident',
}

# Ограничения для фильтров
#   default - первоначальное значение пустое
#   title - заголовок в форме
#   type - вид поля ввода данных при отображении в шаблоне
#   in_list - True если поле может хранить список значений, False - строка
#   select - дополняет select часть запроса, формируемого
#   в методе get_report_all класса Disasters
#   max, min - ограничения для численных значений поля
disasters_filters_meta = {
    'min_datetime': {
        'default': '',
        'title': 'Произошли с момента',
        'type': 'date',
        'in_list': True,
    },
    'max_datetime': {
        'default': '',
        'title': 'Произошли до момента',
        'type': 'date',
        'in_list': True,
    },
    'flight_type': {
        'default': [],
        'title': 'Типы полета',
        'type': 'select',
        'in_list': False,
        'select': '(select flight_type from flight_types '
                  'where id = d.flight_type) as "Тип полета", ',
    },
    'operator': {
        'default': [],
        'title': 'Авиаперевозчики',
        'type': 'input_select',
        'in_list': False,
        'select': '(select operator_name from operators '
                  'where id = d.operator) as "Авиаперевозчик", ',
    },
    'aircraft_model_type': {
        'default': [],
        'title': 'Модели самолетов',
        'type': 'input_select',
        'in_list': False,
        'select': '(select model_name from aircraft_types '
                  'where id = d.aircraft_model_type) as "Модель самолета", ',
    },
    'engine_model_type': {
        'default': [],
        'title': 'Модели двигателей',
        'type': 'input_select',
        'in_list': False,
        'select': '(select model_name from engine_types '
                  'where id = d.engine_model_type) as "Модель двигателя", ',
    },
    'departure_place': {
        'default': '',
        'title': 'На рейсе из аэропорта',
        'type': 'input_select',
        'in_list': True,
    },
    'destination_place': {
        'default': '',
        'title': 'На рейсе в аэропорт',
        'type': 'input_select',
        'in_list': True,
    },
    'is_any_crew_dead': {
        'default': '',
        'title': 'Есть потери среди экипажа',
        'type': 'bool',
        'in_list': True,
    },
    'is_any_passengers_dead': {
        'default': '',
        'title': 'Есть потери среди пассажиров',
        'type': 'bool',
        'in_list': True,
    },
    'temperature_min': {
        'default': '',
        'title': 'Нижняя температурная граница',
        'type': 'float',
        'min': -100,
        'max': 100,
        'in_list': True,
    },
    'temperature_max': {
        'default': '',
        'title': 'Верхняя температурная граница',
        'type': 'float',
        'min': -100,
        'max': 100,
        'in_list': True,
    },
    'pressure_min': {
        'default': '',
        'title': 'Нижняя граница давления (мм.рт.ст.)',
        'type': 'float',
        'min': 0,
        'max': 825,
        'in_list': True,
    },
    'pressure_max': {
        'default': '',
        'title': 'Верхняя граница давления (мм.рт.ст.)',
        'type': 'float',
        'min': 0,
        'max': 825,
        'in_list': True,
    },
    'weather_condition': {
        'default': [],
        'title': 'Виды погодных условий',
        'type': 'input_select',
        'in_list': False,
        'select': '(select condition_name from weather_conditions '
                  'where id = d.weather_condition) as weather_condition, ',
    },
    'country': {
        'default': [],
        'title': 'Страны происшествий',
        'type': 'input_select',
        'in_list': False,
        'select': '(select country_name from countries '
                  'where id = d.country) as country, ',
    },
    'flight_phase': {
        'default': [],
        'title': 'Фазы полета',
        'type': 'select',
        'in_list': False,
        'select': '(select phase_name from flight_phases '
                  'where id = d.flight_phase) as "Фаза полета", ',
    },
    'aircraft_condition': {
        'default': [],
        'title': 'Состояния самолетов после аварии',
        'type': 'select',
        'in_list': False,
        'select': '(select condition_name from aircraft_conditions '
                  'where id = d.aircraft_condition) as '
                  '"Состояние самолета после катастрофы", ',
    },
    'disaster_accident': {
        'default': [],
        'title': 'Типы катастроф',
        'type': 'select',
        'in_list': False,
        'select': '(select accident_type from aviation_accident_types '
                  'where id = d.disaster_accident) as "Тип катастрофы", ',
    }
}

# Заголовки в pdf файл
pdf_headers = {
    'tables_block_1': 'Сводные данные сгруппированные по характеристике ',
    'tables_block_2': 'Данные по наихудшим ситуациям'
}

# Коды ошибок полученных из триггера
error_messages = {
    'disasters': {
        'tr_dis00': 'Дата вылета не может быть позже текущей даты\n',
        'tr_dis01': 'Даты прилета не может быть позже текущей даты\n',
        'tr_dis1': 'Дата вылета не может быть позже даты прилета\n',
        'tr_dis2': 'Выбранный двигатель не устанавливался '
                   'в данный тип самолета\n',
        'tr_dis3': 'Сумма погибших и выживших членов экипажа не может '
                   'превышать максимальное число экипажа для модели самолета\n',
        'tr_dis4': 'Сумма погибших и выживших пассажиров не может превышать '
                   'максимальное число пассажиров для модели самолета\n',
        'tr_dis5': 'Дата катастрофы должна быть позже даты '
                   'первого полета модели\n',
        'tr_dis6': 'Дата катастрофы должна быть раньше даты последнего '
                   'полета модели\n',
        'tr_dis7': 'Место отправления не должно совпадать с место прибытия\n',
        'tr_dis8': 'Дата отправления должна быть позже даты первого '
                   'полета у модели\n',
    },
    'engine_types': {
        'tr_engtyp1': 'Дата окончания разработки должна быть раньше '
                      'текущего момента времени\n',
    },
    'aircraft_types': {
        'tr_airtyp1': 'Дата первого полета должна быть раньше '
                      'текущего момента времени\n',
        'tr_airtyp2': 'Дата последнего полета должна быть раньше '
                      'текущего момента времени\n',
        'tr_airtyp3': 'Дата первого полета должна быть '
                      'раньше даты последнего полета\n'
    },
    'engines_types_to_aircraft_types': {
        'tr_ettatt3': 'Дата последне полета модели должна быть '
                      'позже даты окончания разработки двигателя\n'
    }
}
