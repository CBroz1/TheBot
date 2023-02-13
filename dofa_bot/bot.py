"""Discord Bot.
Adapted from https://github.com/lionel-panhaleux/archon-bot/tree/master/archon_bot
"""
import os
import lightbulb
import logging

logger = logging.getLogger("lightbulb.app")


def main() -> None:
    """Entrypoint for the Discord Bot."""
    if not (os.getenv("BOT_ID", False)):
        logger.error("Could not find credentials")
        return
    bot = lightbulb.BotApp(
        token=os.getenv("DISCORD_TOKEN"),
        suppress_optimization_warning=True,
        # default_enabled_guilds=(os.getenv("GUILD_ID")),  # only this server
        logs="INFO",  # "DEBUG"
    )

    bot.load_extensions_from("./dofa_bot/commands", recursive=True)

    bot.run()


if __name__ == "__main__":
    main()
