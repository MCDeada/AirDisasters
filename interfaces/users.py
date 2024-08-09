import json

import mysql.connector

from interfaces.base import Base
from interfaces.connection_config import connection_params, database_name
from typing import Tuple, Dict, Any
import hashlib
from base64 import b64encode
from flask import jsonify, Response
from datetime import datetime

from interfaces.roles import Roles
from table_consts import no_data


class Users(Base):
    def __init__(self, table_name: str):
        Base().__init__(table_name=table_name)
        self.table_name = table_name
        self.sql_get_row_by_id_fancy = f"""
        SELECT
            user_name, user_surname, user_patronymic,
            login, id_role
        FROM
            Users
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
            u.id, user_name, user_surname, user_patronymic,
            login, role_name as id_role
        FROM
            Users u
        LEFT JOIN
            Roles r ON r.id = u.id_role
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
        # данные из таблицы, на которую ссылается id_role
        all_roles = (
            Roles('roles').get_rows_all().get_json()
        )
        if all_roles['error']:
            return jsonify(all_roles)
        field_values = {'id_role': all_roles['result']}
        return jsonify(field_values)

    def delete(self, row_id: int) -> Response:
        sql = f"""
               DELETE FROM Users WHERE id = {row_id};
           """
        res = Base.delete_by_sql(sql)
        return jsonify(res)

    def get_rows_all(self) -> Response:
        sql = f"""
        SELECT
            id, login
        FROM
            Users
        """
        res = Base.get_rows_by_sql(sql)
        if res['error']:
            return jsonify(res)
        res_dict = {row['id']: row['login'] for row in res['result']}
        return jsonify({'error': False, 'result': res_dict})

    @staticmethod
    def upgrade_user_role(row_id: str) -> Response:
        """
        Функция, с помощью которой Главный администратор может повысить
        в правах пользователя
        :param row_id: номер записи о пользователе
        :return: Статус операции
        """
        sql = f"""
        UPDATE users
        SET id_role = CASE
            WHEN (select role_name from roles 
                  where id = id_role) = 'Пользователь'
            THEN (select id from roles 
                  where role_name = 'Администратор')
            
            WHEN (select role_name from roles 
                  where id = id_role) = 'Администратор'
            THEN (select id from roles 
                  where role_name = 'Главный администратор')
            
            ELSE id_role
        END
        WHERE id = %s;
        """
        tupled_data = (row_id, )
        res = Base.create_or_update_row_by_sql(sql, tupled_data)
        return jsonify(res)

    @staticmethod
    def downgrade_user_role(row_id: str) -> Response:
        """
        Функция, с помощью которой Главный администратор может понизить
        в правах пользователя
        :param row_id: номер записи о пользователе
        :return: Статус операции
        """
        sql = f"""
            UPDATE users
            SET id_role = CASE
                WHEN (select role_name from roles 
                      where id = id_role) = 'Администратор'
                THEN (select id from roles 
                      where role_name = 'Пользователь')

                WHEN (select role_name from roles 
                      where id = id_role) = 'Главный администратор'
                THEN (select id from roles 
                      where role_name = 'Администратор')

                ELSE id_role
            END
            WHERE id = %s;
            """
        tupled_data = (row_id,)
        res = Base.create_or_update_row_by_sql(sql, tupled_data)
        return jsonify(res)

    def get_users_by_login_password(
        self, user_login, user_password
    ) -> str | None:
        """
        Возвращает значение поля user_key
        для конкретного пользователя с логином и паролем.
        Используется для аутентификации
        :param user_login: логин введенный в форме авторизации
        :param user_password: пароль введенный в форме авторизации
        :return: ключ, соответствующий этому пользователю
        """
        # подключение к серверу бд
        with mysql.connector.connect(**connection_params) as conn:
            cur = conn.cursor()
            sql = f""" 
                select user_key from {database_name}.users 
                where login = '{user_login}' and user_password = '{user_password}'
            """
            # исполнение запроса
            cur.execute(sql)
            res = cur.fetchone()
            cur.close()

        if res:
            return res[0]
        else:
            return res

    def get_user_role(self, user_key: str) -> Response:
        """
        Получает имя уровня прав доступа у пользователя с ключом user_key
        :param user_key: ключ сессии
        :return: Имя роли, если данное поле у пользователя заполнено в таблице
                 None, если не нашлось записи по такому ключу
        """
        error = False
        res = [None]
        # подключение к серверу бд
        try:
            with mysql.connector.connect(**connection_params) as conn:
                cur = conn.cursor()
                sql = f""" 
                    select role_name from {database_name}.users u 
                    join {database_name}.roles r on u.id_role = r.id
                    where user_key = '{user_key}';
                """
                cur.execute(sql)
                res = cur.fetchone()
                cur.close()
        except Exception:
            error = 'Ошибка при проверке роли пользователя'

        if res is None:
            error = 'Ошибка при проверке роли пользователя'

        return jsonify({'error': error, 'res': res[0]})

    def create_user(self, row_data: Dict[str, Any]) -> bool | str:
        """
        Создает пользователя, используется при регистрации
        :param row_data: данные о пользователе
        :return: уникальный ключ сессии пользователя,
            если запись в бд была создана корректно, или False, если
            не удалось создать запись о пользователе
        """
        try:
            # подключение к серверу бд
            with mysql.connector.connect(**connection_params) as conn:
                cur = conn.cursor()
                # Ключ получается на основе поля логин, которое уникально
                key = (hashlib.sha256(b64encode(
                    row_data['login'].encode('ascii'))
                ).hexdigest()[:40])
                sql = f""" 
                    insert into {database_name}.users(
                        user_name, user_surname, user_patronymic, 
                        login, user_key, user_password, id_role)
                    values (
                        '{row_data['user_name']}', 
                        '{row_data['user_surname']}', 
                        '{row_data['user_patronymic']}', 
                        '{row_data['login']}', 
                        '{key}', 
                        '{row_data['user_password']}', 1
                    ) 
                """
                cur.execute(sql)
                cur.close()
                # фиксация изменений в базе данных
                conn.commit()
            return key
        except Exception as e:
            return False

    def get_user_id(self, user_key: str):
        """
        На основе ключа пользователя получает идентификатор
        записи о пользователе в бд
        :param user_key: ключ сессии пользователя
        :return: идентификатор записи о пользователя, если запись в бд
            была найдена. None, если не удалось найти запись
            о пользователе по user_key
        """
        # подключение к серверу бд
        with mysql.connector.connect(**connection_params) as conn:
            cur = conn.cursor()
            sql = f""" 
                select id from {database_name}.users
                where user_key = '{user_key}';
            """
            cur.execute(sql)
            res = cur.fetchone()
            cur.close()

        if res:
            return res[0]
        else:
            return res

    def get_action_id(self, action_type: str):
        """
        На основе имени действия получает
        идентификатор соответствующей записи в бд
        :param action_type: имя действия
        :return: идентификатор записи о действии с таким именем,
            если запись в бд была найдена. None, если не удалось найти
            запись о действии по action_type
        """
        # подключение к серверу бд
        with mysql.connector.connect(**connection_params) as conn:
            cur = conn.cursor()
            sql = f""" 
                SELECT id FROM {database_name}.users_actions
                WHERE action_name = '{action_type}'
            """
            cur.execute(sql)
            res = cur.fetchone()
            cur.close()

        if res:
            return res[0]
        else:
            return res

    def write_action(
        self,
        user_key: str,
        action_type: str,
        table_name: str = no_data,
        row_before_action: Dict[str, Any] | str = no_data,
        row_after_action: Dict[str, Any] | str = no_data
    ) -> None:
        """
        Создает запись с действием пользователя в таблице history_of_users
        :param user_key: ключ сессии пользователя
        :param action_type: наименование действия
        :param table_name: имя таблицы
        :param row_before_action: номер записи или номер страницы с данными
        :param row_after_action: номер записи или номер страницы с данными
        :return: None
        """
        # подключение к серверу бд
        with mysql.connector.connect(**connection_params) as conn:
            cur = conn.cursor()
            # получение идентификатора пользователя
            user_id = self.get_user_id(user_key)
            # получение идентификатора действия
            action_id = self.get_action_id(action_type)
            # Если имя таблицы не None значит действие
            # было связано с конкретной таблицей
            # тогда нужно использовать один запрос
            if table_name:
                sql = f""" 
                    INSERT INTO {database_name}.history_of_users (
                        user_id, user_action,
                        related_table, row_before_action,
                        row_after_action, action_datetime
                    ) VALUES (%s, %s, %s, %s, %s, %s);
                """
                data_tuple = (
                    int(user_id), int(action_id),
                    str(table_name), json.dumps(row_before_action),
                    json.dumps(row_after_action), datetime.now()
                )
            # Если действие с таблицей не связано, то другой запрос
            else:
                sql = f""" 
                    INSERT INTO {database_name}.history_of_users(
                        user_id, user_action, action_datetime
                    ) 
                    VALUES (%s, %s, %s);
                """
                data_tuple = (
                    int(user_id), int(action_id), datetime.now()
                )
            # выполнение запроса
            cur.execute(sql, data_tuple)
            cur.close()
            # фиксация добавленной записи в бд
            conn.commit()

    def get_user_info(self, user_key: str) -> Dict[str, str] | None:
        """
        Получает полную информацию о пользователе по ключу сессии
        :param user_key: ключ сессии пользователя
        :return: строка с данными о пользователе, если пользователь был найден
                 None, если не удалось найти запись о пользователе по user_key
        """
        # подключение к серверу бд
        with mysql.connector.connect(**connection_params) as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(f'use {database_name}')
            sql = f""" 
                SELECT a1.id, a1.user_name, a1.user_surname, a1.user_patronymic,
                       a1.login, a1.user_password, a2.role_name as id_role
                FROM {database_name}.users as a1
                LEFT JOIN roles as a2 on a2.id = a1.id_role
                WHERE a1.user_key = '{user_key}'
            """
            cur.execute(sql)
            res = cur.fetchone()
            cur.close()

        return res

    def update(self, data: Dict[str, Any]) -> Response:
        sql_login = "login = %s"
        sql_password = "user_password = %s"
        sql = f"""
        UPDATE users SET
            {sql_login if 'login' in data else sql_password}
        WHERE id = %s;
        """
        if 'login' in data:
            tupled_data = (data['login'], data['id'],)
        else:
            tupled_data = (data['password'], data['id'],)
        res = Base.create_or_update_row_by_sql(sql, tupled_data)
        return jsonify(res)
