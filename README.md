# TheBot

Python-based Discord bot to post GitHub issues. This bot relies on [hikari-lightbulb](https://github.com/tandemdude/hikari-lightbulb/) to handle commands, then passed to [hikari](https://github.com/hikari-py/hikari).

To use...

1. Set up a bot through the [Discord developer portal](https://discord.com/developers/docs/intro).
2. Provide credentials through a local `.env` file, substituting `<notes below>` with values.
3. Run the main bot with optimization: `python -O dofa_bot/bot.py`

```
BOT_ID=<19-digit numeric ID>
DISCORD_TOKEN=<72-character alphanumeric ID>
GUILD_ID=<18-digit Discord server ID>
GITHUB_USER=<username>
GITHUB_TOKEN=<40-character alphanumeric ID>
REPO_OWNER=<Repo fork>
REPO_NAME=<Repo name, forming URL with above>
```

## Usage

`/issue <TITLE> <DESCRIPTION>`

Returns either URL if successful or full API content if unsuccessful.
