import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def create_connection():
    connection = psycopg2.connect(
        dbname='telegram',
        user='postgres', 
        password='toor',
        host='0.0.0.0',
        port='5432'
    )
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    return connection.cursor()    


def create_table(cursor):
    requests = [
        '''
            CREATE TABLE accounts (
                id serial PRIMARY KEY,
                username VARCHAR ( 255 ) UNIQUE NOT NULL,
                user_id INT UNIQUE NOT NULL,
                stage INT DEFAULT 0
            )
        ''',
        '''
            CREATE TABLE files (
                id serial PRIMARY KEY,
                file_path VARCHAR ( 255 ) UNIQUE NOT NULL,
                account_id INT NOT NULL REFERENCES accounts(id)
            )
        '''
    ]
    for request in requests:
        cursor.execute(request)


def insert_account(cursor, username, user_id):
    request = '''
        INSERT INTO accounts (
            username, user_id, stage
        ) VALUES (
            '{}', {}, 0
        )
    '''.format(username, user_id)
    cursor.execute(request)


def update_account(cursor, username, stage):
    request = '''
        UPDATE accounts SET stage = {} WHERE username = '{}'
    '''.format(stage, username)
    cursor.execute(request)


def select_account(cursor, username):
    request = '''
        SELECT * FROM accounts WHERE username = '{}'
    '''.format(username)
    cursor.execute(request)
    return cursor.fetchone()


def insert_file(cursor, file_path, account_pk):
    request = '''
        INSERT INTO files (
            file_path, account_id
        ) VALUES (
            '{}', {}
        )
    '''.format(file_path, account_pk)
    cursor.execute(request)


def select_file(cursor, account_pk):
    request = '''
        SELECT * FROM files WHERE account_id = {} ORDER BY ID DESC LIMIT 1
    '''.format(account_pk)
    cursor.execute(request)
    return cursor.fetchone()


if __name__ == '__main__':
    cursor = create_connection()
    create_table( cursor )
    cursor.close()

