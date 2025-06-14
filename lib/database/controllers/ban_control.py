class BanController:

    def __init__(self, database):
        self.database = database

    # return a list of banned users (limited to 5)
    def ban_list(self, guild_id: int):
        query = "SELECT * FROM banned WHERE guild_id = ? ORDER BY created_at DESC"
        fetch = self.database._exec_query(query, (guild_id,), fetch_all=True)
        return fetch

    # add a ban to the database
    def add_ban(self, guild_id: int, user_id: int, discord_name: str, banned_by: int, reason: str):
        timestamp = self.database._timestamp()
        query = '''
                INSERT INTO banned (guild_id, discord_id, discord_name, reason, banned_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?);
                '''
        push = self.database._exec_query(query, (guild_id, user_id, discord_name, reason, banned_by, timestamp), commit=True)
        return push

    # removes a user from the ban database
    def unban(self, guild_id: int, user_id: int):
        query = "DELETE FROM banned WHERE guild_id = ? and discord_id = ?"
        push = self.database._exec_query(query, (guild_id, user_id))
        return push