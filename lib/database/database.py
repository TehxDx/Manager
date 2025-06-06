"""
    I did not like the way lowDB worked, so I am redoing the database and moving to SQLite3
"""
import sqlite3
import logging
class ManagerDB:

    def __init__(self):
        self.db_name = "database.db"
        self._create_init()

    def _exec_query(self, query, params=(), fetch_one=False, fetch_all=False, commit=False):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)

            if commit:
                conn.commit()
            if fetch_one:
                return cursor.fetchone()
            if fetch_all:
                return cursor.fetchall()
            return cursor.rowcount

    def _create_init(self):

        # lets initialize the banned table
        ban_table = '''
                    CREATE TABLE IF NOT EXISTS banned (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        guild_id INTEGER NOT NULL,
                        discord_id INTEGER NOT NULL,
                        discord_name TEXT NOT NULL,
                        reason TEXT,
                        banned_by INTEGER NOT NULL,
                        timestamp INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
                        UNIQUE (guild_id, discord_id)
                    );
                    '''
        ban_table_index = '''CREATE INDEX IF NOT EXISTS idx_banned_guild_user ON banned (guild_id, discord_id);'''
        ban_table_index_2 = '''CREATE INDEX IF NOT EXISTS idx_banned_user ON banned (discord_id);'''
        self._exec_query(ban_table, commit=True)
        self._exec_query(ban_table_index, commit=True)
        self._exec_query(ban_table_index_2, commit=True)

        # lets initialize the kick table
        kick_table = '''
                     CREATE TABLE IF NOT EXISTS kicks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        discord_id INTEGER NOT NULL,
                        discord_name TEXT NOT NULL,
                        guild_id INTEGER NOT NULL,
                        reason TEXT,
                        kicked_by INTEGER NOT NULL,
                        timestamp INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
                     );
                     '''
        kick_table_index = '''CREATE INDEX IF NOT EXISTS idx_kicks_discord_id ON kicks (discord_id);'''
        kick_table_index_2 = '''CREATE INDEX IF NOT EXISTS idx_kicks_guild_id ON kicks (guild_id);'''
        kick_table_index_3 = '''CREATE INDEX IF NOT EXISTS idx_kicks_guild_discord_id ON kicks (guild_id, discord_id);'''
        self._exec_query(kick_table, commit=True)
        self._exec_query(kick_table_index, commit=True)
        self._exec_query(kick_table_index_2, commit=True)
        self._exec_query(kick_table_index_3, commit=True)

        # lets initialize the timeout table
        timeout_table = '''
                        CREATE TABLE IF NOT EXISTS timeout (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            discord_id INTEGER NOT NULL,
                            discord_name TEXT NOT NULL,
                            guild_id INTEGER NOT NULL,
                            reason TEXT,
                            timeout_by INTEGER NOT NULL,
                            timeout_until INTEGER NOT NULL,
                            timestamp INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
                        );
                        '''
        timeout_table_index = '''CREATE INDEX IF NOT EXISTS idx_timeouts_discord_id ON timeout (discord_id);'''
        timeout_table_index_2 = '''CREATE INDEX IF NOT EXISTS idx_timeouts_guild_id ON timeout (guild_id);'''
        timeout_table_index_3 = '''CREATE INDEX IF NOT EXISTS idx_timeouts_guild_discord_id ON timeout (guild_id, discord_id);'''
        timeout_table_index_4 = '''CREATE INDEX IF NOT EXISTS idx_timeouts_timeout_until ON timeout (timeout_until);'''
        self._exec_query(timeout_table, commit=True)
        self._exec_query(timeout_table_index, commit=True)
        self._exec_query(timeout_table_index_2, commit=True)
        self._exec_query(timeout_table_index_3, commit=True)
        self._exec_query(timeout_table_index_4, commit=True)

        ticket_setup_table = '''
                             CREATE TABLE IF NOT EXISTS ticket_setup (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                guild_id INTEGER NOT NULL,
                                discord_id INTEGER NOT NULL,
                                message_id INTEGER NOT NULL,
                                category INTEGER NOT NULL,
                                channel INTEGER NOT NULL,
                                roles TEXT,
                                timestamp INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
                             );
                             '''
        ticket_setup_index = '''CREATE INDEX IF NOT EXISTS idx_ticket_id ON ticket_setup (guild_id, discord_id);'''
        ticket_setup_index2 = '''CREATE INDEX IF NOT EXISTS idx_ticket_message ON ticket_setup (message_id);'''
        self._exec_query(ticket_setup_table, commit=True)
        self._exec_query(ticket_setup_index, commit=True)

        ticket_table = '''
                        CREATE TABLE IF NOT EXISTS tickets (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            guild_id INTEGER NOT NULL,
                            discord_id INTEGER NOT NULL,
                            channel INTEGER NOT NULL,
                            status BOOLEAN NOT NULL CHECK (status IN (0, 1)),
                            timestamp INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
                        );
                       '''
        ticket_index = '''CREATE INDEX IF NOT EXISTS idx_tickets_guild_id ON tickets (guild_id);'''
        ticket_index_2 = '''CREATE INDEX IF NOT EXISTS idx_tickets_discord_id ON tickets (discord_id);'''
        self._exec_query(ticket_table, commit=True)
        self._exec_query(ticket_index, commit=True)
        self._exec_query(ticket_index_2, commit=True)

    # add a user to the banned table
    def add_user_banned(
            self,
            guild_id: int,
            discord_id: int,
            discord_name: str,
            reason: str,
            banned_by: int,
            timestamp: int
    ):
        query = '''
                INSERT INTO banned (guild_id, discord_id, discord_name, reason, banned_by, timestamp) 
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT (guild_id, discord_id)
                DO NOTHING;
                '''
        self._exec_query(query, (guild_id, discord_id, discord_name, reason, banned_by, timestamp), commit=True)

    # add a user to the kicked table, though, if they are banned and exist in the table, it doesn't need to do anything
    # though this will change, as unbans do happen, but at the moment its left as is
    def add_user_kicked(
            self,
            guild_id: int,
            discord_id: int,
            discord_name: str,
            reason: str,
            kicked_by: int,
            timestamp: int
    ):
        query = '''
                INSERT INTO kicks (discord_id, discord_name, guild_id, reason, kicked_by, timestamp) 
                VALUES (?, ?, ?, ?, ?, ?);
                '''
        self._exec_query(query, (discord_id, discord_name, guild_id, reason, kicked_by, timestamp), commit=True)

    # add a user to the timeout table
    def add_user_timeout(
            self,
            discord_id: int,
            discord_name: str,
            guild_id: int,
            reason: str,
            timeout_by: int,
            timeout_until: int,
            timestamp: int
    ):
        query = '''
                INSERT INTO timeout (discord_id, discord_name, guild_id, reason, timeout_by, timeout_until, timestamp) 
                VALUES (?, ?, ?, ?, ?, ?, ?);
                '''
        self._exec_query(query, (discord_id, discord_name, guild_id, reason, timeout_by, timeout_until, timestamp), commit=True)

    # fetch the last 5 banned
    def fetch_ban_list(self, guild_id: int):
        query = '''
                SELECT * FROM banned 
                WHERE guild_id = ?
                ORDER BY id DESC
                LIMIT 5;
                '''
        fetch = self._exec_query(query, (guild_id,), fetch_all=True)
        return fetch

    # fetch the last 5 kicked
    def fetch_kick_list(self, guild_id: int):
        query = '''
                SELECT * FROM kicks 
                WHERE guild_id = ?
                ORDER BY id DESC
                LIMIT 5;
                '''
        fetch = self._exec_query(query, (guild_id,), fetch_all=True)
        return fetch

    # fetch the last 5 of the timeout list
    def fetch_timeout_list(self, guild_id: int):
        query = '''
                SELECT * FROM timeout
                WHERE guild_id = ?
                ORDER BY id DESC
                LIMIT 5;
                '''
        fetch = self._exec_query(query, (guild_id,), fetch_all=True)
        return fetch

    # ticket database
    # guild_id, discord_id, message_id, category, channel, roles, timestamp
    def setup_ticket(self, guild_id: int, discord_id: int, message_id: int, category: int, channel: int, roles: str, timestamp: int):
        query = '''
                INSERT INTO ticket_setup(guild_id, discord_id, message_id, category, channel, roles, timestamp) 
                VALUES (?, ?, ?, ?, ?, ?, ?);
                '''
        self._exec_query(query, (guild_id, discord_id, message_id, category, channel, roles, timestamp), commit=True)
        query2 = '''
                SELECT * FROM ticket_setup
                WHERE message_id = ?
                '''
        return self._exec_query(query2, (message_id,), fetch_all=True)
