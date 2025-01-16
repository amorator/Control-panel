# from sqlite3 import connect
import mysql.connector as mysql

from classes.user import User
from modules.core import Config


class SQL(Config):
    def __init__(self):
        super().__init__()

    def with_conn(func):
        def _with_conn(self, command, args=[]):
            self.conn = mysql.connect(
                host=self.config["db"]["host"],
                user=self.config["db"]["user"],
                password=self.config["db"]["password"],
                database=self.config["db"]["name"],
            )
            self.cur = self.conn.cursor()
            data = func(self, command, args)
            self.cur.close()
            self.conn.close()
            return data

        return _with_conn

    @with_conn
    def execute_non_query(self, command, args=[]):
        self.cur.execute(command, args)
        self.conn.commit()

    @with_conn
    def execute_scalar(self, command, args=[]):
        self.cur.execute(command, args)
        return self.cur.fetchone()

    @with_conn
    def execute_query(self, command, args=[]):
        self.cur.execute(command, args)
        return self.cur.fetchall()


class SQLUtils(SQL):
    def __init__(self):
        super().__init__()
        self.init_tables()

    def init_tables(self):
        self.execute_non_query(
            f"""CREATE TABLE IF NOT EXISTS {self.config['db']['prefix']}_user (
	id INTEGER UNIQUE AUTO_INCREMENT,
	login VARCHAR(255) NOT NULL UNIQUE,
	name VARCHAR(255) NOT NULL UNIQUE,
	password VARCHAR(32) NOT NULL,
	enabled INTEGER DEFAULT 1,
	permission VARCHAR(50) NOT NULL DEFAULT ",,,",
	PRIMARY KEY(id)
);"""
        )
        self.execute_non_query(
            f"INSERT IGNORE INTO {self.config['db']['prefix']}_user VALUES (%s, %s, %s, %s, %s, %s);",
            [
                1,
                "admin",
                self.config["admin"]["name"],
                self.config["admin"]["password"],
                1,
                "z," * (int(self.config["db"]["permission_length"]) - 1) + "z",
            ],
        )

    def permission_length(self):
        data = self.execute_scalar(
            f"SELECT permission FROM {self.config['db']['prefix']}_user LIMIT 1;"
        )
        return len(data[0].split(","))

    def user_by_id(self, args):
        data = self.execute_scalar(
            f"SELECT * FROM {self.config['db']['prefix']}_user WHERE id = %s;", args
        )
        return User(*data) if data else None

    def user_by_login(self, args):
        data = self.execute_scalar(
            f"SELECT * FROM {self.config['db']['prefix']}_user WHERE login LIKE %s;",
            args,
        )
        return User(*data) if data else None

    def user_exists(self, login, name, id=0):
        uid = self.execute_scalar(
            f"SELECT id FROM {self.config['db']['prefix']}_user WHERE login LIKE %s OR name LIKE %s;",
            [login, name],
        )
        return False if not uid else uid[0] != int(id)

    def user_all(self):
        data = self.execute_query(f"SELECT * FROM {self.config['db']['prefix']}_user;")
        return [User(*d) for d in data] if data else None

    def user_toggle(self, args):
        self.execute_non_query(
            f"UPDATE {self.config['db']['prefix']}_user SET enabled = %s WHERE id = %s;",
            args,
        )

    def user_add(self, args):
        self.execute_non_query(
            f"INSERT INTO {self.config['db']['prefix']}_user (login, name, password, enabled, permission) VALUES (%s, %s, %s, %s, %s, %s);",
            args,
        )

    def user_edit(self, args):
        self.execute_non_query(
            f"UPDATE {self.config['db']['prefix']}_user SET login = %s, name = %s, enabled = %s, permission = %s WHERE id = %s;",
            args,
        )

    def user_delete(self, args):
        self.execute_non_query(
            f"DELETE FROM {self.config['db']['prefix']}_user WHERE id = %s;", args
        )

    def user_reset(self, args):
        self.execute_non_query(
            f"UPDATE {self.config['db']['prefix']}_user SET password = %s WHERE id = %s;",
            args,
        )

    #################


SQLUtils()
