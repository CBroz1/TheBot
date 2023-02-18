import lightbulb
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

from ..utils.logger import logger, DEBUG

feedback_plugin = lightbulb.Plugin(
    "feedback_plugin", "Send feedback to GitHub via DeckOfAdventuresBot"
)

timecode = datetime.now().strftime("%m-%d %H:%M:%S")


@feedback_plugin.command
@lightbulb.command("start_time", "Time bot started", aliases=["version", "time"])
@lightbulb.implements(lightbulb.SlashCommand)
async def start_time(ctx):
    return await ctx.edit_response(timecode)


@feedback_plugin.command
@lightbulb.option("desc", "Description")
@lightbulb.option("title", "Title")
@lightbulb.command("feedback", "Post GitHub Issue")
@lightbulb.implements(lightbulb.SlashCommand)
async def feedback(ctx):
    if load_dotenv() or load_dotenv("TheBot/the_bot/.env"):
        GITHUB_USER = os.environ.get("GITHUB_USER")
        GITHUB_PASS = os.environ.get("GITHUB_TOKEN")
        REPO_OWNER = os.environ.get("REPO_OWNER")
        REPO_NAME = os.environ.get("REPO_NAME")
        if not all([GITHUB_USER, GITHUB_PASS, REPO_OWNER, REPO_NAME]):
            logger.error("Could not find all credentials")
            return
    else:
        logger.error("Could not find env file")
        return

    logger.info(f"New issue from {ctx.author.username}")
    issue = {
        "title": ctx.options.title,
        "body": ctx.options.desc + f"\n\nPosted by {ctx.author.username}",
        "assignee": GITHUB_USER,  # assigned to user who provided credentials
        "labels": ["DiscordBot", "Under Consideration"],
    }
    url = "https://api.github.com/repos/%s/%s/issues" % (REPO_OWNER, REPO_NAME)
    # Create an authenticated session to create the issue

    if DEBUG:
        logger.info(f"Issue created in debug mode: {ctx.options.title}")
        await ctx.edit_response(
            "Bot in development mode. If active, would post " + f"{ctx.options.title}"
        )
    else:
        session = requests.Session()
        session.auth = (GITHUB_USER, GITHUB_PASS)
        response = session.post(url, json.dumps(issue))
        if response.status_code == 201:
            logger.info(f"Successfully created Issue: {ctx.options.title}")
            resp_url = json.loads(response.content)["html_url"]
            await ctx.edit_response(f"Issue URL: {resp_url}")
        else:
            logger.error("Response: ", response.content)
            await ctx.edit_response(
                f"Could not create Issue {ctx.options.title}. Please contact Admin."
            )


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(feedback_plugin)


def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(feedback_plugin)
