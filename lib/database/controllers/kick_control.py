class KickController:

    def __init__(self, database):
        self.database = database

    # fetchs the 5 newest kicks from the database
    def kick_list(self, guild_id: int):
        query = "SELECT * FROM kicks WHERE guild_id = ? ORDER BY created_at DESC LIMIT 5;"
        fetch = self.database._exec_query(query, (guild_id,), fetch_all=True)
        return fetch

    # adds a user to the kicks database
    def add_kick(self, user_id: int, discord_name: str, guild_id: int, reason: str, kicked_by: int):
        timestamp = self.database._timestamp()
        query = '''
                INSERT INTO kicks (discord_id, discord_name, guild_id, reason, kicked_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?);
                '''
        push = self.database._exec_query(query, (user_id, discord_name, guild_id, reason, kicked_by, timestamp), commit=True)
        return push
