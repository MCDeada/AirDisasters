import base64
import copy
import json
from dataclasses import dataclass
from datetime import datetime

from dateutil import parser
from flask_cors import CORS
from flask import (
    Flask, request, render_template,
    url_for, flash, redirect, session, Response
)
from typing import Optional, Dict, Any
from check_errors import CheckErrors
from create_pdf import create_pdf
from interfaces.aircraft_conditions import AircraftConditions
from interfaces.aircraft_types import AircraftTypes
from interfaces.airports import Airports
from interfaces.aviation_accident_types import AviationAccidentTypes
from interfaces.engine_types import EngineTypes
from interfaces.engines_types_to_aircraft_types import (
    EnginesTypesToAircraftTypes
)
from interfaces.flight_phases import FlightPhases
from interfaces.flight_types import FlightTypes
from interfaces.history_of_users import HistoryOfUsers
from interfaces.operators import Operators
from interfaces.countries import Countries
from interfaces.roles import Roles
from interfaces.users import Users
from interfaces.disasters import Disasters
from interfaces.base import Base
from flask_session import Session
from interfaces.users_actions import UsersActions
from interfaces.weather_conditions import WeatherConditions

from table_consts import (
    table_names, tables_fields, path_titles,
    disasters_filters_meta, error_messages, table_names_dt,
    allowed_filters_actions, no_data
)
import locale
locale.setlocale(
    category=locale.LC_ALL,
    locale="Russian"
)

# настройки сессии
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
Session(app)
app.config['SECRET_KEY'] = '8fe4efa51c6a36a3ca982a0757d2302493c8d9bef8763f74'
CORS(app)

# инициализация вспомогательных классов
users = Users('users')
check_errors = CheckErrors()


@dataclass
class ErrorMessage:
    # факт наличия ошибки. True - нет ошибки, False - есть
    is_ok: bool = True
    # строка с маршрутом перехода, в случае ошибки, None - если нет ошибки
    redirect_path: Optional[str] = None
    # строка с сообщением об ошибке, None - если нет ошибки
    error_message: Optional[str] = None
    # Максимальое количество строк в проверяемой таблице или 0 по умолчанию
    page_number: int = 0


def get_redirect_path(table_name: Optional[str] = None) -> str:
    """
    Возвращает маршрут, по которому нужно перейти в случае ошибки.
    :param table_name: Имя таблицы, путь по которой не удалось открыть
    :return: Строка с адресом
    """
    route = f'/get_all/{table_name}/1' if table_name else '/get_all/disasters/1'
    return route


def allowed_file(file: str) -> bool:
    """
    Проверяет принадлежность расширения загружаемого файла к разрешенным
    :param file: Имя файла целиком
    :return: True/False
    """
    return (
        '.' in file and file.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def get_metadata(
    table_name: Optional[str], title: Optional[str]
) -> Dict[str, Any]:
    """
    Получает словарь с вспомогательной информацией для отображения страниц
    :param table_name: Имя таблицы в запросе.
    :param title: Указывает какой заголовок нужен
    :return: Словарь
    """
    alert_style = 'alert__container__fail'
    if request.args.get('is_success', False) == 'True':
        alert_style = 'alert__container__success'
    is_sorting = True if table_name == 'disasters' else False
    base_metadata = {
        'is_sorting': is_sorting,
        'alert__container__background': alert_style,
        'table_name': table_name,
        'table_fields': tables_fields.get(table_name, {}),
    }
    if title in ['login', 'registration']:
        return base_metadata
    user_role = users.get_user_role(session["key"]).get_json()
    if user_role['error']:
        flash('Ошибка при извлечении метаданных для страницы')
        redirect('/get_all/disasters/1')
    base_metadata |= {
        'user_role': user_role['res'],
    }
    if table_name is None:
        return base_metadata

    filters_values = {}
    for field, value in session['disasters_filters'].items():
        if isinstance(value, list):
            filters_values[field] = str(session['disasters_filters'][field])[1:-1]
        else:
            filters_values[field] = str(session['disasters_filters'][field])

    return base_metadata | {
        'title': path_titles[table_name][title],
        'disasters_filters_titles': disasters_filters_meta,
        'disasters_filters_values': filters_values,
    }


def is_authenticated() -> ErrorMessage:
    """
    Проверяет авторизованность пользователя
    :return: Класс со статусом проверки и описанием ошибки
    """
    if not session.get("key", False):
        return ErrorMessage(False, "/login", "Войдите в систему")
    else:
        return ErrorMessage()


def is_correct_path(
    url: str, table_name: Optional[str] = None
) -> ErrorMessage:
    """
    Проверяет существование адреса, по которому обращается пользователь
    :param url: Часть отвечающая за описание действия
    :param table_name: Часть отвечающая за имя таблицы
    :return: Класс со статусом проверки и описанием ошибки
    """
    if table_name not in table_names:
        return ErrorMessage(
            False,
            get_redirect_path(),
            f'URL: /{url}/{table_name} не существует'
        )
    else:
        return ErrorMessage()


def is_correct_page_number(
    table_name: str, page_number: str, filters_str: str = ''
) -> ErrorMessage:
    """
    Проверяет есть ли данные для введенного номера страницы
    :param table_name: Имя таблицы для которой может не быть данных.
    :param page_number: Номер страницы.
    :param filters_str: Фильтры, которые влияют на возможное число строк.
    :return: Класс со статусом проверки и описанием ошибки
    """
    is_valid_page_number = (
        check_errors.is_valid_page_number(
            table_name, page_number, filters_str).get_json()
    )
    if is_valid_page_number['error']:
        return ErrorMessage(
            is_ok=False,
            redirect_path=get_redirect_path(table_name),
            error_message=is_valid_page_number['error'],
            page_number=0
        )
    else:
        return ErrorMessage(page_number=is_valid_page_number['total_rows'])


def is_restricted(
    table_name: str, is_get: bool
) -> ErrorMessage:
    """
    Проверяет достаточность прав для доступа
    к таблицам связанным с подсистемой пользователей
    :param table_name: Имя таблицы
    :param is_get: В случае False закрывает всякий доступ
    :return: Класс со статусом проверки и описанием ошибки
    """
    # не пытается ли пользователь обратиться к таблицам главного администратора
    if table_name in ['history_of_users', 'roles', 'users', 'users_cations']:
        if is_get and not is_main_admin():
            return ErrorMessage(
                is_ok=False,
                redirect_path='/get_all/disasters/1',
                error_message='Недостаточно прав для взаимодействия '
                              'с подсистемой пользователей'
            )
        elif not is_get and table_name != 'users':
            return ErrorMessage(
                is_ok=False,
                redirect_path='/get_all/disasters/1',
                error_message=f'Невозможно изменять таблицу '
                              f'{table_names_dt[table_name]}'
            )
        else:
            return ErrorMessage()
    else:
        return ErrorMessage()


def is_admin(table_name: str) -> ErrorMessage:
    """
    Функция проверки, что роль пользователя - администратор и выше
    :param table_name: Имя таблицы
    :return: Класс со статусом проверки и описанием ошибки
    """
    # извлечение наименования роли пользователя из бд
    current_role = users.get_user_role(session.get("key", '')).get_json()
    res = ErrorMessage()
    if current_role['error']:
        res.is_ok = False
        res.redirect_path = get_redirect_path(table_name)
        res.error_message = current_role['error']
    if (
        current_role['res'] is None or
        current_role['res'] not in ['Администратор', 'Главный администратор']
    ):
        res.is_ok = False
        res.redirect_path = get_redirect_path(table_name)
        res.error_message = 'Недостаточно прав для внесения изменений'
    return res


def is_main_admin() -> bool:
    """
    Функция проверки, что роль пользователя - главный администратор
    :return: True/False
    """
    current_role = users.get_user_role(session.get("key", '')).get_json()
    if not current_role['error'] and current_role['res'] == 'Главный администратор':
        return True
    return False


def is_correct_row_id(
    table_name: str, row_id: str
) -> ErrorMessage:
    """
    Проверка, что номер записи - целое число больше 0
    :param table_name: Номер таблицы
    :param row_id: Проверяемое значение
    :return: Класс со статусом проверки и описанием ошибки
    """
    is_valid_row_id = check_errors.is_is_valid_id(row_id).get_json()
    if is_valid_row_id['error']:
        return ErrorMessage(
            is_ok=False,
            redirect_path=get_redirect_path(table_name),
            error_message=is_valid_row_id['error'],
        )
    else:
        return ErrorMessage()


def is_redirect_base(
    used_path: str, table_name: str
) -> ErrorMessage:
    """
    Функция проверки базовых условий на доступ к данным по маршруту get
    :param used_path: Маршрут, по которому было обращение.
    :param table_name: Имя таблицы.
    :return: Класс со статусом проверки и описанием ошибки
    """
    check = is_authenticated()
    if not check.is_ok:
        return check
    check = is_correct_path(used_path, table_name)
    if not check.is_ok:
        return check
    return ErrorMessage()


def is_redirect_get_all(
    table_name: str, page_number: str
) -> ErrorMessage:
    """
    Функция проверки условий на доступ к данным по маршруту с действием get_all
    :param table_name: имя таблицы из запроса
    :param page_number: номер страницы данных
    :return: Класс со статусом проверки и описанием ошибки
    """
    check = is_redirect_base('get_all', table_name)
    if not check.is_ok:
        return check
    check = is_restricted(table_name, True)
    if not check.is_ok:
        return check
    interface = get_interface(table_name)
    filters_str = interface.get_filters(session['disasters_filters'], session['find'])
    check = is_correct_page_number(table_name, page_number, filters_str)
    if not check.is_ok:
        return check
    return check


def is_redirect_upgrade(
    row_id: str = ''
) -> ErrorMessage:
    """
    Функция проверки условий на возможность повысить/понизить
    пользователя в правах
    :param row_id: номер записи пользователя в базе
    :return: Класс со статусом проверки и описанием ошибки
    """
    check = is_authenticated()
    if not check.is_ok:
        return check
    if not is_main_admin():
        return ErrorMessage(
            is_ok=False,
            redirect_path='/get_all/disasters/1',
            error_message='Недостаточно прав'
        )
    check = is_correct_row_id('users', row_id)
    if not check.is_ok:
        return check
    return check


def is_redirect_modification(
    route_name: str, table_name: str, row_id: str = ''
) -> ErrorMessage:
    """
    Функция проверки условий на доступ к созданию/модификации/удалению
    данных для данной таблицы и данного пользователя
    :param route_name: имя команды модификации
    :param table_name: имя таблицы
    :param row_id: номер записи в базе
    :return: Класс со статусом проверки и описанием ошибки
    """
    check = is_redirect_base(route_name, table_name)
    if not check.is_ok:
        return check
    check = is_admin(table_name)
    if not check.is_ok:
        return check
    check = is_restricted(table_name, False)
    if not check.is_ok:
        return check
    if route_name in ['update-view', 'delete']:
        check = is_correct_row_id(table_name, row_id)
    return check


def is_redirect_filters() -> ErrorMessage:
    """
    Проверка, что пользователю разрешено задавать фильтры
    :return: Класс со статусом проверки и описанием ошибки
    """
    check = is_authenticated()
    return check


def get_interface(table_name: str) -> Optional[Base]:
    """
    Получение экземпляра класса в зависимости от запроса пользователя
    :param table_name: Имя таблицы
    :return: Объект для общения с определенной таблицей
    """
    if table_name == 'weather_conditions':
        return WeatherConditions(table_name=table_name)
    elif table_name == 'flight_phases':
        return FlightPhases(table_name=table_name)
    elif table_name == 'aircraft_conditions':
        return AircraftConditions(table_name=table_name)
    elif table_name == 'aviation_accident_types':
        return AviationAccidentTypes(table_name=table_name)
    elif table_name == 'countries':
        return Countries(table_name=table_name)
    elif table_name == 'flight_types':
        return FlightTypes(table_name=table_name)
    elif table_name == 'airports':
        return Airports(table_name=table_name)
    elif table_name == 'aircraft_types':
        return AircraftTypes(table_name=table_name)
    elif table_name == 'engine_types':
        return EngineTypes(table_name=table_name)
    elif table_name == 'engines_types_to_aircraft_types':
        return EnginesTypesToAircraftTypes(table_name=table_name)
    elif table_name == 'operators':
        return Operators(table_name=table_name)
    elif table_name == 'disasters':
        return Disasters(table_name=table_name)
    elif table_name == 'users_actions':
        return UsersActions(table_name=table_name)
    elif table_name == 'history_of_users':
        return HistoryOfUsers(table_name=table_name)
    elif table_name == 'users':
        return Users(table_name=table_name)
    elif table_name == 'roles':
        return Roles(table_name=table_name)
    else:
        return None


def get_error_message(
    code: int, table_name: str, field_name: str
) -> str:
    """
    Составляет сообщения об ошибках для действий по их кодам
    :param code: Код ошибки
    :param table_name: Имя таблицы
    :param field_name: Имя поля, с которым возникла проблема
    :return: Строка с ошибкой
    """
    if code == 3819:
        return tables_fields[table_name][field_name]
    elif code == 1048:
        return (f"Поле '{tables_fields[table_name][field_name]['header']}' "
                f"не может быть пусто")
    elif code == 1265:
        return (f"Поле '{tables_fields[table_name][field_name]['header']}' "
                f"не может быть пусто")
    elif code == 1062:
        return (f"'{tables_fields[table_name][field_name]['header']}' "
                f"должен быть уникальным")
    elif code == 1452:
        return (f"Значение поля '{tables_fields[table_name][field_name]['header']}' "
                f"не найдено в списке")
    elif code in [1292, 1366]:
        return (f"Неверное значение поля "
                f"'{tables_fields[table_name][field_name]['header']}'")
    elif code == 1064:
        return "SQL запрос содержит ошибку"
    elif code == 1406:
        return (f"Поле '{tables_fields[table_name][field_name]['header']}' "
                f"может содержать максимум "
                f"{tables_fields[table_name][field_name]['max_length']} символов")
    elif code == 1644:
        return error_messages[table_name][field_name]
    else:
        return f"Ошибка ввода"


def prepare_data_display(
    data: Dict[str, Any]
) -> None:
    """
    Заменяет пустые значения на соответствующее сообщение
    :param data: Словарь, в котором есть пустые значения
    :return: Измененный по ссылке data
    """
    for field, value in data.items():
        if value is None or value == '':
            data[field] = no_data


def prepare_data(
    table_name: str, data: Dict[str, Any]
) -> None:
    """
    Приводит пустые поля к None
    :param table_name: Имя таблицы
    :param data: Данные
    :return: Измененный по ссылке data
    """
    for field, value in data.items():
        if field not in tables_fields[table_name]:
            continue
        if value == '':
            data[field] = None


def set_default_filters() -> None:
    """
    Устанавливает в сессии пользователя поля для хранения состояния
    текущих выбранных фильтров
    :return: None
    """
    dt = {}
    for key in disasters_filters_meta:
        dt[key] = disasters_filters_meta[key]['default']
    session["disasters_filters"] = dt
    session["disasters_filters_lists"] = {
        "flight_type": [],
        "operator": [],
        "aircraft_model_type": [],
        "engine_model_type": [],
        "weather_condition": [],
        "country": [],
        "flight_phase": [],
        "aircraft_condition": [],
        "disaster_accident": [],
    }
    session['find'] = {
        'table_name': '',
        'value': ''
    }


def convert_dict_for_history(
    table_name: str,
    data_row: Dict[str, Any],
    foreign_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Формирует словарь данных для отображения в статистике действий
    :param table_name: Имя таблицы.
    :param data_row: Данные, которые надо преобразовать.
    :param foreign_data: Словари, из которых нужно взять данные для подстановки.
    :return: Словарь с человекочитаемым полями и значениями
    """
    data_row_history = {}
    for column_name, column_value in data_row.items():
        if column_name not in tables_fields[table_name]:
            continue
        col_name = tables_fields[table_name][column_name]['header']
        display_status = tables_fields[table_name][column_name]['display']
        if column_value is not None:
            if column_name in foreign_data and display_status != 'input_select':
                data_row_history[col_name] = (
                    foreign_data[column_name][str(column_value)]
                )
            else:
                data_row_history[col_name] = column_value
        else:
            data_row_history[col_name] = no_data
        if (
            column_name in foreign_data and
            display_status == 'input_select'
            and column_value in foreign_data[column_name]
        ):
            data_row[column_name] = foreign_data[column_name][column_value]

    return data_row_history


# Функции входа и регистрации
@app.route('/login', methods=['GET', 'POST'])
def login():
    """ Функция входа. Демонстрирует форму и авторизует пользователя """
    if request.method == 'POST':
        user_login = request.form['login']
        user_password = request.form['password']
        # Если эти поля не пустые
        if user_login and user_password:
            # получение уникального ключа пользователя
            user_key = users.get_users_by_login_password(
                user_login, user_password
            )
            # Если не нашлось ключа в базе
            if user_key is None:
                flash('Неверный логин или пароль')
            else:
                # Заметка об входе в систему пользователем
                users.write_action(
                    user_key=user_key,
                    action_type='Вход в систему'
                )
                # Если логин и пароль подошли,
                # то в браузере открывается сессия с ключом
                session["key"] = user_key
                set_default_filters()
                # Перенаправление на главную страницу
                return redirect(
                    url_for(
                        'get_all',
                        table_name='disasters',
                        page_number=1
                    )
                )
        else:
            flash('Остались пустые поля')
    # Если отправки данных с формы не произошло,
    # то просто нужно отрисовать форму
    metadata = get_metadata(None, 'login')

    return render_template('login.html', metadata=metadata)


@app.route('/user_page', methods=['GET', 'POST'])
def user_page():
    """ Маршрут перехода в личный кабинет пользователя """
    # Проверка авторизован ли пользователь
    is_allowed = is_authenticated()
    if not is_allowed.is_ok:
        flash(is_allowed.error_message)
        return redirect(is_allowed.redirect_path)

    metadata = get_metadata('users', 'title_get')

    # Если переход по маршруту произошел с GET запросом
    if request.method == 'GET':
        # Получение информации о пользователе по ключу его сессии
        user_info = users.get_user_info(session["key"])
        # Если получить информацию из бд не получилось
        if not user_info:
            flash("Ошибка входа в личный кабинет")
            return redirect(get_redirect_path())
        # если информация о пользователе получена, то её можно отобразить
        return render_template(
            'user_page.html',
            user_info=user_info,
            metadata=metadata
        )
    # Если переход по маршруту произошел после отправки формы с данными
    if request.method == 'POST':
        data_row_str = json.dumps(request.form)
        data_row = json.loads(data_row_str)
        login_new = data_row.get('login', None)
        password_new = data_row.get('user_password', None)
        prepare_data('users', data_row)
        # Проверка наличия ошибок
        data_foreign = users.get_foreign_fields().get_json()
        found_errors = check_errors.check_fields(
            data_row, 'users', data_foreign
        )
        if found_errors:
            for error in found_errors:
                flash(error)
            return redirect(
                url_for(
                    'user_page',
                    metadata=metadata,
                    is_success=False
                )
            )
        # Получение первоначальных данных о пользователе
        user_info = users.get_user_info(session.get("key", ""))
        login_old = user_info['login']
        password_old = user_info['user_password']
        # Получение данных о действии
        data = {}
        action_str = ''
        if login_new is not None and login_new != login_old:
            data = {'login': login_new, 'id': user_info['id']}
            action_str = 'логин'
        elif password_new is not None and password_new != password_old:
            data = {'password': password_new, 'id': user_info['id']}
            action_str = 'пароль'
        if not action_str:
            flash('Данные не были изменены')
            return redirect(
                url_for(
                    'user_page',
                    metadata=metadata,
                    is_success=False
                )
            )
        result = users.update(data).get_json()
        # Если найдены ошибки
        error = result['error']
        if error:
            if login_new is not None:
                flash('Ошибка при обновлении логина')
            elif password_new is not None:
                flash('Ошибка при обновлении пароля')
            return redirect(
                url_for(
                    'user_page',
                    metadata=metadata,
                    is_success=False
                )
            )

        data_row_history_before = convert_dict_for_history(
            'users', {'login': login_old}, data_foreign
        )
        data_row_history_new = convert_dict_for_history(
            'users', {'login': login_new}, data_foreign
        )

        users.write_action(
            user_key=session['key'],
            action_type=f'Обновлен {action_str}',
            row_before_action=data_row_history_before,
            row_after_action=data_row_history_new,
            table_name='users'
        )

        # В случае успеха отображение данных
        flash(f'Поле {action_str} успешно обновлено')
        return redirect(
            url_for('user_page', metadata=metadata, is_success=True)
        )


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    """ Маршрут с формой регистрации """
    if request.method == 'POST':
        # данные с формы
        row_data = json.loads(json.dumps(request.form))
        # проверка корректности полей данных
        errors = check_errors.check_fields(
            row_data, 'users', {}
        )
        # Если ошибок нет
        if not errors:
            # создается уникальный ключ и пользователь заносится в бд
            key = users.create_user(row_data)
            if key:
                # регистрация запоминается в действиях
                users.write_action(
                    user_key=key,
                    action_type='Регистрация',
                    table_name='users'
                )
                # У пользователя в браузере открывается сесиия с этим ключом
                session["key"] = key
                set_default_filters()
                # Переход на главную страницу
                return redirect(url_for('get_all',
                                        table_name='disasters',
                                        page_number=1))
            else:
                flash('Ошибка при создании пользователя. '
                      'Обратитесь к главному администратору')
        else:
            for error in errors:
                flash(error)

    metadata = get_metadata('users', 'registration')

    # отображение формы
    return render_template(
        'registration.html', metadata=metadata
    )


@app.get("/change-role/<action>/<row_id>")
def change_role(action: str, row_id: str):
    # Проверки возможности обращения по данному маршруту
    is_allowed = is_redirect_upgrade(row_id)
    if not is_allowed.is_ok:
        flash(is_allowed.error_message)
        return redirect(is_allowed.redirect_path)

    action_name = ''
    if action == 'upgrade':
        data_row = Users.upgrade_user_role(row_id).get_json()
        action_name = 'Выданы права'
    elif action == 'downgrade':
        data_row = Users.downgrade_user_role(row_id).get_json()
        action_name = 'Отозваны'
    else:
        data_row = {'error': "Невозможное действие с ролью пользователя"}

    if data_row['error']:
        flash(data_row['error'])
    else:
        users.write_action(
            user_key=session["key"],
            action_type=action_name
        )

    return redirect(f"/get_all/users/1")


@app.get("/logout")
def logout():
    """ Маршрут для закрытия сессии в браузере """
    check = is_authenticated()
    if not check.is_ok:
        flash('Все сессии подключений уже завешены')
        return redirect("/login")
    # пометка о выходе из системы
    users.write_action(
        user_key=session["key"],
        action_type='Выход из системы'
    )
    # очистка ключа
    session["key"] = None
    session["disasters_filters"] = None
    session["disasters_filters_lists"] = None
    session['find'] = None
    return redirect("/login")


@app.get('/get_all/<table_name>/<page_number>')
def get_all(table_name: str, page_number: str):
    """
    Маршрут для отображения общих данных таблицы
    :param table_name: Имя таблицы
    :param page_number: Номер страницы данных. Одна страница содержит 10 записей
    :return: html-шаблон get_all с данными
    """
    # проверки возможности отображения данных
    is_allowed = (
        is_redirect_get_all(table_name, page_number)
    )
    if not is_allowed.is_ok:
        flash(is_allowed.error_message)
        return redirect(is_allowed.redirect_path)

    # извлечение нужного количества строк определенной таблицы
    interface = get_interface(table_name)
    filters_str = interface.get_filters(session['disasters_filters'], session['find'])
    data_rows = interface.get_rows(page_number, filters_str).get_json()

    # Проверка, что извлечение прошло успешно
    if data_rows['error']:
        flash(data_rows['error'])
        return redirect(f"/get_all/{table_name}/1")
    data_rows = data_rows['result']

    # Подмена пустых строк на более понятные 'Нет данных'
    for data_row in data_rows:
        prepare_data_display(data_row)

    # Получение вспомогательных данных
    data_rows_length = len(data_rows)
    page_number = int(page_number)
    metadata = get_metadata(table_name, 'title_get') | {
        'active': path_titles[table_name]['active'],
        'data_rows_length': data_rows_length,
        'isNext': data_rows_length * page_number != is_allowed.page_number,
        'in_search': session['find'],
    }
    template = 'get_all_admin.html'
    if (
        metadata['user_role'] == 'Пользователь' or
        table_name in ['history_of_users', 'roles', 'users_actions']
    ):
        template = 'get_all_user.html'

    # Если по выбранным фильтрам не нашлось записей выводится ошибка
    if not data_rows_length:
        flash('Нет данных удовлетворяющих фильтрам')

    # Отображение страницы
    return render_template(
        template,
        metadata=metadata,
        data_rows=data_rows,
        page_number=page_number,
    )


@app.get('/filters-view/<discard>')
def filters_view(discard: str):
    """
    Маршрут для отображения общих данных таблицы
    :param discard: False - изменить фильтры, True - очистить фильтры
    :return: html-шаблон disasters_filters с данными
    """
    # Проверки возможности обращения по данному маршруту
    is_allowed = is_redirect_filters()
    if not is_allowed.is_ok:
        flash(is_allowed.error_message)
        return redirect(is_allowed.redirect_path)

    # Проверка корректности значения параметра запроса
    if not (discard == 'False' or discard == 'True'):
        flash('Неверный параметр для маршрута /filters-view/')
        return redirect(f"/get_all/disasters/1")

    # Действия если пользователь захотел очистить выбранные фильтры
    if discard == 'True':
        set_default_filters()
        return redirect(f"/get_all/disasters/1")

    # Извлечение данных для полей-внешних ключей
    interface = get_interface('disasters')
    data_foreign = interface.get_foreign_fields().get_json()
    # Дополнение полей-списков пунктом,
    # который сигнализирует о неактивности поля
    for field in data_foreign:
        if (
            tables_fields['disasters'][field]['display'] == 'select'
            and disasters_filters_meta[field]['in_list']
        ):
            data_foreign[field] |= {'': 'Не выбрано'}
    # текущие фильтры получены или из сохраненных в сессии или
    # если ввели ошибочные данные, то введенные ошибочные данных
    disasters_filters_lists = copy.deepcopy(session["disasters_filters_lists"])
    disasters_filters_cur = json.loads(
        request.args.get('entered_filter_values', '{}')
    )
    if not disasters_filters_cur:
        disasters_filters_cur = copy.deepcopy(session["disasters_filters"])
    # Корректировка отображения дат
    if disasters_filters_cur["min_datetime"] != '':
        disasters_filters_cur["min_datetime"] = (
            parser.parse(disasters_filters_cur["min_datetime"]).date()
        )
    if disasters_filters_cur["max_datetime"] != '':
        disasters_filters_cur["max_datetime"] = (
            parser.parse(disasters_filters_cur["max_datetime"]).date()
        )

    metadata = get_metadata(None, 'title_get')

    return render_template(
        'disasters_filters.html',
        metadata=metadata,
        disasters_filters=disasters_filters_cur,
        disasters_filters_lists=disasters_filters_lists,
        data_foreign=data_foreign
    )


@app.post('/update_filters')
def update_filters():
    """
    Маршрут проверяющий корректность обновленных данных, введенных в форму
    :return: None
    """
    # Проверки возможности обращения по данному маршруту
    is_allowed = is_redirect_filters()
    if not is_allowed.is_ok:
        flash(is_allowed.error_message)
        return redirect(is_allowed.redirect_path)

    # Получение обновленных данных с формы
    filters = json.loads(json.dumps(request.form))
    # Списки допустимых значений для полей, являющихся внешними ключами
    filters_valid_values = Disasters('disasters').get_foreign_fields().get_json()
    field_name = None
    # Проверка корректности имени действия
    if (
        filters.get('action', False) and
        not filters.get('action', '') in allowed_filters_actions
    ):
        flash('Неверное имя действия при попытки задать фильтр')
        redirect(url_for(
            'filters_view',
            discard=False,
            entered_filter_values=json.dumps(filters)
        ))

    # В зависимости от нажатой кнопки проверяется 0, 1 или все введенные поля
    if filters.get('action', False):
        field_name = allowed_filters_actions[filters['action']]
        if 'Очистить' not in filters['action']:
            found_errors = check_errors.is_valid_filter(
                filters[field_name], field_name, filters_valid_values[field_name]
            )
        else:
            found_errors = []
    else:
        found_errors = check_errors.is_valid_filters(filters,
                                                     filters_valid_values)
    # если при проверке выявились ошибки
    if found_errors:
        # Отображает ошибки
        for error in found_errors:
            flash(error)
        # Возвращение на форму с сообщением об ошибке
        return redirect(url_for(
            'filters_view',
            discard=False,
            entered_filter_values=json.dumps(filters)
        ))
    else:
        # Сохранение введенных данных в зависимости от действия
        if filters.get('action', False):
            # Выбрано одно значение поля
            if (
                'Выбрать' in filters['action'] and
                filters[field_name] not in
                session['disasters_filters_lists'][field_name]
            ):
                session['disasters_filters_lists'][field_name].append(
                    filters[field_name]
                )
            # Исключено одно значение поля
            elif (
                'Исключить' in filters['action'] and
                filters[field_name] in
                session['disasters_filters_lists'][field_name]
            ):
                session['disasters_filters_lists'][field_name].remove(
                    filters[field_name]
                )
            # Очищены все значения поля
            elif 'Очистить' in filters['action']:
                session['disasters_filters_lists'][field_name] = []

            return redirect(url_for(
                'filters_view',
                discard=False,
                entered_filter_values=json.dumps(filters)
            ))
        # Если нажата кнопка Найти
        else:
            for field, value in disasters_filters_meta.items():
                if value['in_list']:
                    if filters[field] == 'False':
                        filters[field] = 'Нет'
                    if filters[field] == 'True':
                        filters[field] = 'Есть'
                    session['disasters_filters'][field] = filters[field]
                else:
                    session['disasters_filters'][field] = (
                        session['disasters_filters_lists'][field]
                    )

        flash('Фильтры применены')
        return redirect(
            url_for(
                'get_all', table_name='disasters',
                page_number=1, is_success=True
            )
        )


@app.get('/update-view/<table_name>/<row_id>')
def update_view(table_name: str, row_id: str):
    """
    Маршрут отображающий форму обновления данных
    :param table_name: Имя таблицы
    :param row_id: Номер записи
    :return: html-шаблон update-view.html с формой
    """
    # Проверки возможности обращения по данному маршруту
    is_allowed = is_redirect_modification(
        'update-view', table_name, row_id
    )
    if not is_allowed.is_ok:
        flash(is_allowed.error_message)
        return redirect(is_allowed.redirect_path)

    # Извлечение данных о строке и о значениях для внешних ключей
    interface = get_interface(table_name)
    data_row = interface.get_row_by_id_all(
        row_id, interface.sql_get_row_by_id_fancy).get_json()
    # Если в извлеченных данных есть ошибка
    if data_row['error']:
        flash(data_row['error'])
        return redirect(f"/get_all/{table_name}/1")
    data_row = data_row['result']
    # data_foreign - все варианты значений для внешних ключей
    data_foreign = interface.get_foreign_fields().get_json()
    # Дополнение списков пунктом о невыбранности
    for field in data_foreign:
        if tables_fields[table_name][field]['display'] == 'select':
            data_foreign[field] |= {'': no_data}

    data_row = get_inserted(
        data_row, json.loads(request.args.get('data_row', '{}'))
    )

    # Убрано отображение считанного изображения
    if table_name == 'disasters':
        data_row['photo_of_result'] = None

    metadata = get_metadata(table_name, 'title_update')

    return render_template(
        'update.html',
        metadata=metadata,
        data_row=data_row,
        row_id=row_id,
        data_foreign=data_foreign
    )


@app.post('/update/<table_name>')
def update(table_name):
    """
    Маршрут проверяющий корректность обновленных данных, введенных в форму
    :param table_name: Имя таблицы
    :return: None
    """
    # Проверки возможности обращения по данному маршруту
    is_allowed = is_redirect_modification(
        'update', table_name
    )
    if not is_allowed.is_ok:
        flash(is_allowed.error_message)
        return redirect(is_allowed.redirect_path)

    # Получение обновленных данных
    data_row_str = json.dumps(request.form)
    data_row = json.loads(data_row_str)
    prepare_data(table_name, data_row)
    # Внешние поля и проверка ошибок
    interface = get_interface(table_name)
    data_foreign = interface.get_foreign_fields().get_json()
    # извлечение предыдущей версии изменяемой записи
    data_row_old = interface.get_row_by_id_all(
        data_row['row_id'], interface.sql_get_row_by_id).get_json()
    if data_row_old['error']:
        flash('Ошибка при извлечении прежней версии изменяемой строки')
        return redirect(url_for(
            'get_all',
            table_name=table_name,
            page_number=1,
        ))
    data_row_old = data_row_old['result']
    found_errors = check_errors.check_fields(
        data_row, table_name, data_foreign, data_row_old
    )
    if found_errors:
        for error in found_errors:
            flash(error)
        return redirect(url_for(
            'update_view',
            table_name=table_name,
            row_id=data_row['row_id'],
            data_row=data_row_str,
        ))
    # Кодировка переданной фотографии в случае изменения катастрофы
    if table_name == 'disasters':
        file = request.files['photo_of_result']
        if file and allowed_file(file.filename):
            data_row['photo_of_result'] = base64.b64encode(file.read())
        else:
            data_row['photo_of_result'] = None

    data_row_new = convert_dict_for_history(
        table_name, data_row, data_foreign
    )

    # обновляется запись в бд
    result = interface.update(data_row).get_json()
    # Если найдены ошибки
    error = result['error']
    if error:
        for field_name in error_messages[table_name]:
            if field_name in error[1]:
                flash(get_error_message(
                    error[0], table_name, field_name
                ))
        # то ввод должен быть повторен при помощи предыдущего маршрута
        return redirect(url_for(
            'update_view',
            table_name=table_name,
            row_id=data_row['row_id']
        ))
    action_type = 'Изменена запись'
    flash('Успешно изменено')
    # Фото извлекается, из-за сложности отображения
    if table_name == 'disasters':
        if 'photo_of_result' in data_row:
            data_row.pop('photo_of_result')
        if 'photo_of_result' in data_row_old:
            data_row_old.pop('photo_of_result')
        data_row_old['photo_of_result'] = None
        data_row_new['Фото произошедшей катастрофы'] = None

    data_row_history = convert_dict_for_history(
        table_name, data_row_old, data_foreign
    )

    # вносится пометка об этом действии
    users.write_action(
        user_key=session["key"],
        action_type=action_type,
        table_name=table_names_dt[table_name],
        row_before_action=data_row_history,
        row_after_action=data_row_new
    )
    # переход к данным измененной строки
    return redirect(
        url_for(
            'get', table_name=table_name,
            row_id=data_row['row_id'], is_success=True
        )
    )


def get_inserted(
    tables_data: Dict[str, Any], data_row: Dict[str, Any]
) -> Dict[str, str]:
    """
    Перебрасывает значения из data_row в tables_data
    :param tables_data: Словарь принимающий значения
    :param data_row: Словарь отдающий значения
    :return: Измененный tables_data
    """
    for table_name in tables_data:
        if tables_data[table_name] is None:
            tables_data[table_name] = ''
        elif table_name in data_row:
            tables_data[table_name] = data_row[table_name]

    return tables_data


@app.get('/create-view/<table_name>')
def create_view(table_name: str) -> str | Response:
    """
    Маршрут отображающий форму создания записей
    :param table_name: Имя таблицы
    :return: html-шаблон create.html с формой
    """
    # Проверки возможности обращения по данному маршруту
    is_allowed = is_redirect_modification(
        'create-view', table_name
    )
    if not is_allowed.is_ok:
        flash(is_allowed.error_message)
        return redirect(is_allowed.redirect_path)

    interface = get_interface(table_name)
    # data_default - все поля таблицы - пустые значения
    data_default = interface.get_empty()
    # data_foreign - все варианты значений для внешних ключей
    data_foreign = interface.get_foreign_fields().get_json()
    # Дополнение списков пунктом о невыбранности
    for field in data_foreign:
        if tables_fields[table_name][field]['display'] == 'select':
            data_foreign[field] |= {'': no_data}

    data_row = get_inserted(
        data_default, json.loads(request.args.get('data_row', '{}'))
    )

    metadata = get_metadata(table_name, 'title_create')

    return render_template(
        'create.html',
        metadata=metadata,
        data_row=data_row,
        data_foreign=data_foreign
    )


@app.post('/create/<table_name>')
def create(table_name: str):
    """
    Маршрут проверяющий корректность введенных данных
    :param table_name: Имя таблицы
    :return: None
    """
    # Проверки возможности обращения по данному маршруту
    is_allowed = is_redirect_modification(
        'create', table_name
    )
    if not is_allowed.is_ok:
        flash(is_allowed.error_message)
        return redirect(is_allowed.redirect_path)

    # Извлечение данных введенных в форму
    data_row_str = json.dumps(request.form)
    data_row = json.loads(data_row_str)
    prepare_data(table_name, data_row)
    # Внешние поля и проверка ошибок
    interface = get_interface(table_name)
    data_foreign = interface.get_foreign_fields().get_json()
    found_errors = check_errors.check_fields(data_row, table_name, data_foreign)
    # Если есть ошибки
    if found_errors:
        for error in found_errors:
            flash(error)
        return redirect(url_for(
            'create_view',
            table_name=table_name,
            data_row=data_row_str,
        ))
    # Преобразование всех индексов к именным полям для восприятия в таблице
    # history_of_users
    data_row_history = convert_dict_for_history(
        table_name, data_row, data_foreign
    )
    # Кодировка переданной фотографии в случае изменения катастрофы
    if table_name == 'disasters':
        file = request.files['photo_of_result']
        if file and allowed_file(file.filename):
            data_row['photo_of_result'] = base64.b64encode(file.read())
        else:
            data_row['photo_of_result'] = None
    # Попытка создания записи в базе
    result = interface.create(data_row).get_json()
    # Если найдены ошибки, то ввод должен быть повторен
    # при помощи предыдущего маршрута
    error = result['error']
    if error:
        for field_name in error_messages[table_name]:
            if field_name in error[1]:
                flash(get_error_message(
                    error[0], table_name, field_name
                ))
        return redirect(url_for(
            'create_view',
            table_name=table_name,
            data_row=data_row_str,
        ))
    # В случае успешного добавления делается заметка об этом
    users.write_action(
        user_key=session["key"],
        action_type='Добавлена запись',
        table_name=table_names_dt[table_name],
        row_after_action=data_row_history
    )
    flash('Успешно добавлено')
    return redirect(
        url_for(
            'get_all', table_name=table_name,
            page_number=1, is_success=True
        )
    )


@app.get('/delete/<table_name>/<row_id>')
def delete(table_name: str, row_id: str):
    """
    Удаляет запись из таблицы
    :param table_name: Имя таблицы
    :param row_id: Номер записи в бд
    """
    # Проверки возможности обращения по данному маршруту
    is_allowed = is_redirect_modification(
        'delete', table_name, row_id
    )
    if not is_allowed.is_ok:
        flash(is_allowed.error_message)
        return redirect(is_allowed.redirect_path)

    # Сохранение удаляемой записи в переменной data_row_old
    interface = get_interface(table_name)
    data_foreign = interface.get_foreign_fields().get_json()
    data_row_old = interface.get_row_by_id_all(
        row_id, interface.sql_get_row_by_id_fancy).get_json()['result']
    # Удаление из бд по id записи
    result = interface.delete(row_id).get_json()
    error = result['error']
    # Если при удалении была ошибка
    if error:
        for field_name in error_messages[table_name]:
            if field_name in error[1]:
                flash(get_error_message(
                    error[0], table_name, field_name
                ))

    data_row_history = convert_dict_for_history(
        table_name, data_row_old, data_foreign
    )

    # заметка о совершенном действии
    users.write_action(
        user_key=session["key"],
        action_type='Удалена запись',
        table_name=table_names_dt[table_name],
        row_before_action=data_row_history
    )

    flash(f'Строка успешно удалена')

    return redirect(
        url_for(
            'get_all', table_name=table_name,
            page_number=1, is_success=True
        )
    )


@app.get('/get/<table_name>/<row_id>')
def get(table_name: str, row_id: str):
    """
    Маршрут страницу с данными одной записи
    :param table_name: Имя таблицы
    :param row_id: Номер записи в бд
    :return: html-шаблон get.html
    """
    # Проверки возможности обращения по данному маршруту
    is_allowed = is_redirect_base('get', table_name)
    if not is_allowed.is_ok:
        flash(is_allowed.error_message)
        return redirect(is_allowed.redirect_path)

    metadata = get_metadata(table_name, 'title_get')
    # Получен данных о строке
    interface = get_interface(table_name)
    data_row = interface.get_row_by_id_all(
        row_id, interface.sql_get_row_by_id_fancy).get_json()
    # Если получение данных прошло с ошибкой
    if data_row['error']:
        flash(data_row['error'])
        return redirect(f"/get_all/{table_name}/1")
    # Замена пустот на понятную запись
    prepare_data_display(data_row['result'])
    # Получение изображения в отдельную переменную для отображения в случае
    # записи таблицы катастроф
    image = None
    if table_name == 'disasters':
        image = data_row['result']['photo_of_result']
        data_row['result'].pop('photo_of_result')
    # Если обращение идет к таблице history_of_users
    # надо преобразовать к словарям следующие поля
    if data_row['result'].get('row_before_action', False):
        data_row['result']['row_before_action'] = (
            json.loads(data_row['result']['row_before_action'])
        )
    if data_row['result'].get('row_after_action', False):
        data_row['result']['row_after_action'] = (
            json.loads(data_row['result']['row_after_action'])
        )

    # заметка о совершенном действии
    users.write_action(
        user_key=session["key"],
        action_type='Просмотрена запись',
        table_name=table_names_dt[table_name],
        row_before_action=data_row['result']
    )

    return render_template(
        'get.html',
        metadata=metadata,
        data_row=data_row['result'],
        row_id=row_id,
        image=image
    )


@app.get('/create-report')
def create_report():
    """
    Маршрут инициирующий создание отчета по катастрофам
    :return: None
    """
    # Проверки возможности обращения по данному маршруту
    is_allowed = is_redirect_filters()
    if not is_allowed.is_ok:
        flash(is_allowed.error_message)
        return redirect(is_allowed.redirect_path)
    # Получение данных о пользователе
    user_info = Users(table_name='users').get_user_info(session.get('key', ''))
    user = {
        'Имя': user_info['user_name'],
        'Фамилия': user_info['user_surname'],
        'Отчество': user_info['user_patronymic'],
        'Роль': user_info['id_role']
    }
    # Текущие параметры фильтрации
    interface = get_interface('disasters')
    filters_str = interface.get_filters(session['disasters_filters'], session['find'])
    # Сбор по анализируемы полям статистики
    errors = []
    all_data_1 = {}
    for field_name, value in disasters_filters_meta.items():
        if not value['in_list']:
            data_all = Disasters.get_report_all(
                filters_str, field_name, value['select']
            ).get_json()
            if data_all['error']:
                errors.append(data_all['error'])
            else:
                all_data_1[disasters_filters_meta[field_name]['title']] = (
                    data_all['result']
                )
    # Сбор наихудших случаев
    all_data_2 = []
    data_worst_cases = Disasters.get_report_worst(filters_str).get_json()
    if data_worst_cases['error']:
        errors.append(data_worst_cases['error'])
    else:
        all_data_2 = data_worst_cases['result']
    # если в извлечении информации замечены ошибки
    if errors:
        for error in errors:
            flash(error)

    # Формирование уникального имени файла
    datetime_now = datetime.now()
    current_date = datetime(
        year=datetime_now.year,
        month=datetime_now.month,
        day=datetime_now.day,
    )
    seconds = (datetime_now - current_date).seconds
    filename = (
        user_info['login'] + '_' + str(current_date.date()) +
        '_' + str(seconds) + '.pdf'
    )
    # момент времени формирования отчета для отображения в отчете
    datetime_now_converted = datetime_now.strftime("%d.%m.%Y %H:%M")
    # Запрос на создание
    create_pdf(
        user_info=user,
        data1=all_data_1,
        data2=all_data_2,
        filename='documents/' + filename,
        current_date=datetime_now_converted,
        filters=session['disasters_filters']
    )

    users.write_action(
        user_key=session["key"],
        table_name=filename,
        action_type='Создан отчет'
    )

    flash(f'Отчёт создан с именем {filename}')
    return redirect(
        url_for(
            'get_all', table_name='disasters',
            page_number=1, is_success=True
        )
    )


@app.post("/find/<table_name>")
def find(table_name: str):
    is_allowed = is_redirect_filters()
    if not is_allowed.is_ok:
        flash(is_allowed.error_message)
        return redirect(is_allowed.redirect_path)

    # Извлечение данных введенных в форму
    data_row_str = json.dumps(request.form)
    data_row = json.loads(data_row_str)
    if data_row.get('exec_find', False):
        session['find'] = {
            'table_name': table_name,
            'value': data_row['find']
        }
    if data_row.get('clear_find', False):
        session['find'] = {
            'table_name': '',
            'value': ''
        }

    return redirect(
        url_for(
            'get_all', table_name='disasters',
            page_number=1
        )
    )


# точка входа программы
if __name__ == '__main__':
    app.run(debug=True)
