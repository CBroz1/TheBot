import lightbulb
from automation.simulator.deck import Card, Deck
from automation.templates.bestiary import list_attribs, list_skills
from ..utils.logger import DEBUG

deck_plugin = lightbulb.Plugin("deck_plugin", "Sim deck")

result_types = Deck().result_types
int_as_str = [str(n) for n in range(6)]

decks = dict()


# NOTE: Bad practice referencing globals. This should pull from a database.
def get_user_deck(username):
    this_deck = decks.get(f"deck_{username}", False)
    if not this_deck:
        decks[f"deck_{username}"] = Deck()
        this_deck = decks[f"deck_{username}"]
    return this_deck


# ------ DECK DRAW ------
@deck_plugin.command()
@lightbulb.command(
    "draw_rand_card", "draws a card from a persistent deck", aliases=["random draw"]
)
@lightbulb.implements(lightbulb.SlashCommand)
async def draw_rand_card(ctx: lightbulb.Context) -> None:
    this_deck = get_user_deck(ctx.author.username)
    result = this_deck.draw()
    await ctx.respond(f"Drew {result}\n{this_deck}")


# ------ DECK CHECK ------
@deck_plugin.command()
@lightbulb.option("dr", "DR", choices=int_as_str, default="3")
@lightbulb.option(
    "mod",
    "Mod to apply to check.",
    choices=int_as_str,
    default="0",
)
@lightbulb.option(
    "tc",
    "TC. Two letters to represent a card by suit (S,C,H,D) and value (2,K,T, etc.). "
    + "ST for Ten of Spades.",
    default="Random",
)
@lightbulb.option("upper_lower", "[U]pper/[L]ower hand or [N]either", default="N")
@lightbulb.option("draw_n", "Draw count.", default=1)
@lightbulb.command("deck_check", "Run a check with your deck.", aliases=["deck check"])
@lightbulb.implements(lightbulb.SlashCommand)
async def deck_check(ctx: lightbulb.Context) -> None:
    this_deck = get_user_deck(ctx.author.username)

    await ctx.respond(
        this_deck.check_by_skill(
            TC=Card(ctx.options.tc),
            DR=int(ctx.options.dr),
            mod=ctx.options.mod,
            upper_lower=ctx.options.upper_lower,
            draw_n=ctx.options.draw_n,
            return_string=True,
        )
    )


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(deck_plugin)


def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(deck_plugin)
