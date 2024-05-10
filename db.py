# db.py

import psycopg2
from config import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD


def create_connection():
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None

# Пример использования
# conn = create_connection()
# if conn is not None:
#     # Взаимодействие с базой данных
#     conn.close()


def search_by_name(conn, name):
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM udmega WHERE name = %s", (name,))
        return cursor.fetchall()


def search_whitelist(conn, user_id):
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM whitelist WHERE user_id = %s", (user_id,))
        return cursor.fetchall()


def get_whitelist(conn):
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM whitelist")
        return cursor.fetchall()


def delete_from_whitelist(conn, user_phone):
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM whitelist WHERE phone = %s", (user_phone,))
    conn.commit()


def log_action(conn, user_id, phone, username, search):
    with conn.cursor() as cursor:
        query = """
        INSERT INTO loggs (user_id, phone, username, search)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, phone, username, search))
    conn.commit()


def last_loggs(conn, phone):
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM loggs WHERE phone = %s ORDER BY date_create DESC LIMIT 100", (phone,))
        return cursor.fetchall()


def search_by_phone(conn, phone):
    with conn.cursor() as cursor:
        if phone.startswith('99677') or phone.startswith('99622'):
            cursor.execute("SELECT * FROM udbeeline WHERE phone = %s", (phone,))
        elif phone.startswith('99655') or phone.startswith('99699'):
            cursor.execute("SELECT * FROM udmega WHERE phone = %s", (phone,))
        else:
            cursor.execute("SELECT * FROM udoshka WHERE phone = %s", (phone,))
        return cursor.fetchall()


def get_record_by_id_1(conn, record_id):
    with conn.cursor() as cursor :
        cursor.execute("SELECT * FROM udmega WHERE id = %s", (record_id,))
        return cursor.fetchone()  # Предполагается, что ID является уникальным


def get_record_by_id_2(conn, record_id):
    with conn.cursor() as cursor :
        cursor.execute("SELECT * FROM udoshka WHERE id = %s", (record_id,))
        return cursor.fetchone()  # Предполагается, что ID является уникальным


def get_record_by_id_3(conn, record_id):
    with conn.cursor() as cursor :
        cursor.execute("SELECT * FROM udbeeline WHERE id = %s", (record_id,))
        return cursor.fetchone()  # Предполагается, что ID является уникальным

# def get_records_by_id(conn, record_id):
#     results = []
#     tables = ['webapp_udmega', 'webapp_udoshka', 'webapp_udbee']
#
#     for table in tables:
#         with conn.cursor() as cursor:
#             cursor.execute(f"SELECT * FROM {table} WHERE id = %s", (record_id,))
#             result = cursor.fetchone()
#             if result:
#                 results.append(result)
#
#     return results
