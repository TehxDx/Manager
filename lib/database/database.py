"""
    I did not like the way lowDB worked, so I am redoing the database and moving to SQLite3
"""
import os
import datetime
import sqlite3
import logging
from lib.database.controllers.ban_control import BanController
from lib.database.controllers.kick_control import KickController
from lib.database.controllers.ticket_control import TicketController
from lib.database.controllers.timeout_control import TimeoutController


class ManagerDB:

    def __init__(self):
        self.db_name = "database.db"
        self.db_schema = "schema/schema.sql"
        self._create_init()
        self._load_controls()

    def _exec_query(self, query, params=(), fetch_one=False, fetch_all=False, commit=False):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)

            if commit:
                conn.commit()
                logging.info("[+] Committing changes")
            if fetch_one:
                logging.info("[+] Fetching result")
                return cursor.fetchone()
            if fetch_all:
                logging.info("[+] Fetching all results")
                return cursor.fetchall()
            return cursor.rowcount

    def _create_init(self):
        logging.info("[+] Initializing database")
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                if not os.path.exists(self.db_schema):
                    logging.error(f"[+] Can not locate {self.db_schema}")
                    return
                with open(self.db_schema, 'r') as file:
                    scheme_data = file.read()

                cursor.executescript(scheme_data)
                conn.commit()
            logging.info("[+] Database initialized")
        except sqlite3.Error as e:
            logging.error(f"[!] Database initialization failed: {e}")
            exit() # temporary placement

    # role modifier to tickets
    def ticket_setup_role_modifier(self, guild_id: int, ticket_id: int, roles: str):
        query = "UPDATE ticket_setup SET roles = ? WHERE id = ? AND guild_id = ?"
        self._exec_query(query, (roles, ticket_id, guild_id), commit=True)
        return self.ticket_setup_fetch(guild_id, ticket_id)

    @staticmethod
    def _timestamp():
        return int(datetime.datetime.now(datetime.timezone.utc).timestamp())

    def _load_controls(self):
        self.ban = BanController(self)
        self.kick = KickController(self)
        self.timeout = TimeoutController(self)
        self.ticket = TicketController(self)