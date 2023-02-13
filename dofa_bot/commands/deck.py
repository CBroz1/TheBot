import lightbulb
from automation.simulator.deck import Deck
from ..utils.logger import DEBUG

deck_plugin = lightbulb.Plugin("deck_plugin", "Sim deck")

# NOTE: Bad practice referencing globals. This should pull from a database.
def get_user_deck(username):
    this_deck = globals().get(f"deck_{username}", False)
    if not this_deck:
        globals()[f"deck_{username}"] = Deck()
        this_deck = globals()[f"deck_{username}"]
    return this_deck


@deck_plugin.command()
@lightbulb.command("draw", "draws a card")
@lightbulb.implements(lightbulb.SlashCommand)
async def draw(ctx: lightbulb.Context) -> None:
    this_deck = get_user_deck(ctx.author.username)
    result = this_deck.draw()
    await ctx.respond(f"Drew {result}\n{this_deck}")


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(deck_plugin)


def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(deck_plugin)
