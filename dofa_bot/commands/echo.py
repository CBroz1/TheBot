import lightbulb

from ..utils.logger import DEBUG

echo_plugin = lightbulb.Plugin("echo_plugin", "Test bot functionality via echo")


@echo_plugin.command()
@lightbulb.command("echo", "Repeats the user's input")
@lightbulb.implements(lightbulb.PrefixCommand)
async def echo(ctx: lightbulb.Context) -> None:
    if DEBUG:
        await ctx.respond(f"Debug mode. {ctx.options.text}")
    else:
        await ctx.respond(ctx.options.text)


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(echo_plugin)


def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(echo_plugin)
