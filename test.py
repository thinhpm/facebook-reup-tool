import sqlite3
from sqlite3 import Error

database = r"database/pythonsqlite.db"


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


conn = create_connection(database)


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def create_access_token(conn, data):
    """
    Create a new project into the projects table
    :param conn:
    :param data:
    :return: project id
    """
    sql = ''' INSERT INTO access_tokens(name,access_token,channel_id,page_number,status)
              VALUES(?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, data)
    conn.commit()
    return cur.lastrowid


def create_channel(conn, data2):
    """
    Create a new project into the projects table
    :param conn:
    :param data2:
    :return: project id
    """
    sql = ''' INSERT INTO channels(source)
              VALUES(?) '''
    cur = conn.cursor()
    print(data2)
    cur.execute(sql, data2)
    conn.commit()
    return cur.lastrowid


def create_data(conn, data):
    """
    Create a new project into the projects table
    :param conn:
    :param data:
    :return: project id
    """
    sql = ''' INSERT INTO datas(channel_id,video_id)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, data)
    conn.commit()
    return cur.lastrowid


def add_page(data):
    item_channel = (data['source'])
    id_channel = create_channel(conn, item_channel)

    item_access_token = (data['name'], data['accesstoken'], id_channel, data['page_number'], 1)
    create_access_token(conn, item_access_token)


def main():
    sql_create_access_tokens_table = """ CREATE TABLE IF NOT EXISTS access_tokens (
                                        id integer PRIMARY KEY,
                                        name text,
                                        access_token text,
                                        channel_id integer,
                                        page_number integer,
                                        status integer
                                    ); """

    sql_create_channels_table = """CREATE TABLE IF NOT EXISTS channels (
                                    id integer PRIMARY KEY,
                                    source text,
                                    created_at timestamp
                                );"""

    sql_create_datas_table = """CREATE TABLE IF NOT EXISTS datas (
                                        id integer PRIMARY KEY,
                                        channel_id integer,
                                        video_id text,
                                        created_at timestamp,
                                        FOREIGN KEY (channel_id) REFERENCES channels (id)
                                    );"""

    # create a database connection
    conn = create_connection(database)

    # create tables
    if conn is not None:
        # create projects table
        create_table(conn, sql_create_access_tokens_table)
        create_table(conn, sql_create_channels_table)
        create_table(conn, sql_create_datas_table)
        # item = ('test1', 'EAA1', 1, 1, 0)
        # create_access_token(conn, item)
    else:
        print("Error! cannot create the database connection.")


if __name__ == '__main__':
    main()
    data = {
        'source': "source1",
        "name": "name1",
        "accesstoken": "accesstoken1",
        "page_number": 2
    }
    add_page(data)