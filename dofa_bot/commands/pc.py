import lightbulb
from automation.simulator.player import Player
from automation.templates.bestiary import Bestiary
from ..utils.logger import DEBUG

pc_plugin = lightbulb.Plugin("pc_plugin", "Sim character")

bestiary = Bestiary(
    input_files=["06_Bestiary.yaml", "07_PCs.yaml"],
    limit_types=["PC"],
)
pc_options = bestiary.as_dict.keys()

# NOTE: Bad practice referencing globals. This should pull from a database.
def get_user_pc(username, pc_selection=None, pc_name=None):
    this_pc = globals().get(f"pc_{username}")
    if not this_pc and pc_selection:
        pc_dict = bestiary.raw_data[pc_selection]
        pc_dict.update(dict(Name=pc_name or username, id=username))
        globals()[f"pc_{username}"] = Player(**pc_dict)
        this_pc = globals()[f"pc_{username}"]
    return this_pc


@pc_plugin.command()
@lightbulb.option("pc", "Premade PCs", choices=pc_options)
@lightbulb.option("name", "Name your pc")
@lightbulb.command("select_pc", "Selects a PC from premades")
@lightbulb.implements(lightbulb.SlashCommand)
async def select_pc(ctx: lightbulb.Context) -> None:
    this_pc = get_user_pc(ctx.author.username, ctx.options.pc, ctx.options.name)
    await ctx.respond(f"Selected {ctx.options.pc}\n{this_pc}")


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(pc_plugin)


def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(pc_plugin)
