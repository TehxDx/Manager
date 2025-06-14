class TimeoutController:

    def __init__(self, database):
        self.database = database

    def timeout_list(self, guild_id: int):
        query = "SELECT * FROM timeout WHERE guild_id = ? ORDER BY created_at DESC"
        fetch = self.database._exec_query(query, (guild_id,), fetch_all=True)
        return fetch

    def add_timeout(self, user_id: int, discord_name: str, guild_id: int, reason: str, timeout_by: int, timeout_until: int):
        timestamp = self.database._timestamp()
        query = '''
                INSERT INTO timeout (discord_id, discord_name, guild_id, reason, timeout_by, timeout_until, created_at) 
                VALUES (?, ?, ?, ?, ?, ?, ?);
                '''
        push = self.database._exec_query(query, (user_id, discord_name, guild_id, reason, timeout_by, timeout_until, timestamp), commit=True)
        return push