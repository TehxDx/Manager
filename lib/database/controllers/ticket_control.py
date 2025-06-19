class TicketController:

    def __init__(self, database):
        self.database = database

    def ticket_setup(self, guild_id: int, discord_id: int, message_id: int, category: int, channel: int, roles: str, ticket_embed: str):
        timestamp = self.database._timestamp()
        query = '''
                INSERT INTO ticket_setup(guild_id, discord_id, message_id, category, channel, roles, embed, created_at) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                '''
        self.database._exec_query(query, (guild_id, discord_id, message_id, category, channel, roles, ticket_embed, timestamp), commit=True)
        fetch = self.ticket_setup_fetch(message_id=message_id)
        return fetch

    def ticket_setup_fetch(self, message_id: int = None, ticket_id: int = None, guild_id: int = None, fetch_all: bool = False):
        if message_id and ticket_id is None and guild_id is None:
            query = "SELECT * FROM ticket_setup WHERE message_id = ?"
            fetch = self.database._exec_query(query, (message_id,), fetch_all=fetch_all, fetch_one=not fetch_all)
            return fetch
        if ticket_id and guild_id and message_id is None:
            query = "SELECT * FROM ticket_setup WHERE id = ? AND guild_id = ?"
            fetch = self.database._exec_query(query, (ticket_id, guild_id), fetch_all=fetch_all, fetch_one=not fetch_all)
            return fetch
        if guild_id and message_id is None and ticket_id is None:
            query = "SELECT * FROM ticket_setup WHERE guild_id = ?"
            fetch = self.database._exec_query(query, (guild_id,), fetch_all=fetch_all, fetch_one=not fetch_all)
            return fetch
        else:
            return None

    def ticket_setup_role_modifier(self, guild_id: int, ticket_id: int, roles: str):
        query = "UPDATE ticket_setup SET roles = ? WHERE id = ? AND guild_id = ?"
        self.database._exec_query(query, (roles, ticket_id, guild_id), commit=True)
        fetch = self.ticket_setup_fetch(guild_id=guild_id, ticket_id=ticket_id)
        return fetch

    def ticket_setup_drop(self, guild_id: int, message_id: int):
        query = "DELETE FROM ticket_setup WHERE guild_id = ? AND message_id = ?"
        self.database._exec_query(query, (guild_id, message_id), commit=True)
        return

    def ticket_add(self, guild_id: int, user_id: int, channel_id: int, status: bool):
        timestamp = self.database._timestamp()
        query = "INSERT INTO tickets (guild_id, discord_id, channel, status, created_at) VALUES (?, ?, ?, ?, ?)"
        self.database._exec_query(query, (guild_id, user_id, channel_id, status, timestamp), commit=True)
        return

    def ticket_search(self, guild_id: int, user_id: int):
        query = "SELECT * FROM tickets WHERE guild_id = ? AND discord_id = ?"
        fetch = self.database._exec_query(query, (guild_id, user_id), fetch_all=True)
        return fetch

    def ticket_update(self, guild_id: int, user_id: int, channel_id: int, status: bool):
        query = "UPDATE tickets SET status = ? WHERE guild_id = ? AND discord_id = ? AND channel = ?"
        self.database._exec_query(query, (status, guild_id, user_id, channel_id), commit=True)
        return
