CREATE TABLE IF NOT EXISTS ticket_setup (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    discord_id INTEGER NOT NULL,
    message_id INTEGER NOT NULL,
    category INTEGER NOT NULL,
    channel INTEGER NOT NULL,
    roles TEXT,
    embed TEXT DEFAULT 'ticket_example',
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_ticket_id ON ticket_setup (guild_id, discord_id);

CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    discord_id INTEGER NOT NULL,
    channel INTEGER NOT NULL,
    ticket_setup INTEGER NOT NULL,
    status BOOLEAN NOT NULL CHECK (status IN (0, 1)),
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_tickets_guild_id ON tickets (guild_id);
CREATE INDEX IF NOT EXISTS idx_tickets_discord_id ON tickets (discord_id, status);

CREATE TABLE IF NOT EXISTS banned (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    discord_id INTEGER NOT NULL,
    discord_name TEXT NOT NULL,
    reason TEXT,
    banned_by INTEGER NOT NULL,
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_banned_guild_user ON banned (guild_id, discord_id);
CREATE INDEX IF NOT EXISTS idx_banned_user ON banned (discord_id);

CREATE TABLE IF NOT EXISTS kicks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_id INTEGER NOT NULL,
    discord_name TEXT NOT NULL,
    guild_id INTEGER NOT NULL,
    reason TEXT,
    kicked_by INTEGER NOT NULL,
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_kicks_discord_id ON kicks (discord_id);
CREATE INDEX IF NOT EXISTS idx_kicks_guild_id ON kicks (guild_id);
CREATE INDEX IF NOT EXISTS idx_kicks_guild_discord_id ON kicks (guild_id, discord_id);

CREATE TABLE IF NOT EXISTS timeout (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_id INTEGER NOT NULL,
    discord_name TEXT NOT NULL,
    guild_id INTEGER NOT NULL,
    reason TEXT,
    timeout_by INTEGER NOT NULL,
    timeout_until INTEGER NOT NULL,
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_timeouts_discord_id ON timeout (discord_id);
CREATE INDEX IF NOT EXISTS idx_timeouts_guild_id ON timeout (guild_id);
CREATE INDEX IF NOT EXISTS idx_timeouts_guild_discord_id ON timeout (guild_id, discord_id);
CREATE INDEX IF NOT EXISTS idx_timeouts_timeout_until ON timeout (timeout_until);