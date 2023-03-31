import random
import lightbulb

from hikari.interactions.command_interactions import (
    AutocompleteInteraction,
    AutocompleteInteractionOption,
)
from hikari.users import UserImpl
import datetime

import itertools
from automation.simulator.deck import Card, Deck
from automation.simulator.player import Player
from automation.simulator.encounter import Encounter
from automation.templates.bestiary import Bestiary, list_attribs, list_skills
from ..utils.logger import DEBUG, logger

pc_plugin = lightbulb.Plugin("pc_plugin", "Sim character")

bestiary_pcs = Bestiary(
    input_files=["06_Bestiary.yaml", "07_PCs.yaml"],
    limit_types=["PC"],
)
bestiary_gm = Bestiary(
    input_files=["06_Bestiary.yaml", "07_PCs.yaml"],
    limit_types=["Dealer", "NPC", "Boss", "PC"],
)
options_pc = list(bestiary_pcs.as_dict.keys())[:24]
options_gm = list(bestiary_gm.as_dict.keys())[:24]
list_stats = [*list_attribs, *list_skills]
result_types = Deck().result_types
int_as_str = [str(n) for n in range(6)]

pcs = dict()
beasts = dict()


def assign_default_attack(dict, key):
    powers = [v for k, v in dict[key].Powers.items() if "Attack" in k]
    dict[key].Powers["Attack"] = powers[0] if powers else None


def get_user_pc(username, pc_selection=None, pc_name=None):
    this_pc = pcs.get(username)
    # logger.info(f"{username}, selected {pc_selection} named {pc_name}: {this_pc}")
    if not this_pc or pc_selection:
        if pc_selection:
            pc_dict = bestiary_pcs.raw_data[pc_selection]
            pc_dict.update(dict(Name=pc_name or username, id=pc_selection))
            pcs[username] = Player(**pc_dict)
            # Assign default Attack
            assign_default_attack(pcs, username)
        else:
            pcs[username] = Player(
                Name=f"{pc_name or username} - Default", id="Default", Type="PC"
            )
        this_pc = pcs[username]
    return this_pc


def get_beast(username, beast_name, beast_selection=None):
    this_beast = beasts.get(beast_name)
    if not this_beast:
        if beast_selection:
            beast_dict = bestiary_gm.raw_data[beast_selection]
            beast_dict.update(dict(Name=beast_name, id=beast_selection))
            beasts[beast_name] = Player(**beast_dict)
            assign_default_attack(beasts, beast_name)
        else:
            beasts[beast_name] = Player(
                Name=f"{beast_name or username} - Default", id="Default", Type="PC"
            )
        this_beast = beasts[beast_name]
    return this_beast


def pc_powers_auto(power=None, auto_interaction=None):
    logger.info(f"pc_powers_auto: {power}, {auto_interaction}")
    this_pc = get_user_pc(auto_interaction.user.username)
    if len(power.value) < 2:
        powers = this_pc.Powers.keys()
    else:
        powers = [p for p in this_pc.Powers.keys() if power.value in p]
    return list(powers)


def gm_powers_auto(power=None, auto_interaction=None):
    logger.info(f"3 {power}")
    logger.info(f"4 {auto_interaction}")

    if not pcs and not beasts:
        return []

    if len(power.value) < 2:
        powers = set(
            power_name
            for pc in [*pcs.values(), *beasts.values()]
            for power_name in pc.Powers.keys()
        )
    else:
        powers = set(
            power_name
            for pc in [*pcs.values(), *beasts.values()]
            for power_name in pc.Powers.keys()
            if power.value in power_name
        )
    return list(itertools.islice(powers, 25))


# save to file


# ------ GM TARGET ------
@pc_plugin.command()
@lightbulb.add_checks(lightbulb.has_roles(1014868119791075508))
@lightbulb.option(
    "attacker",
    "Attacking creature.",
    choices=list(*beasts.keys(), *pcs.keys())[:24],
    default="Random beast",
)
@lightbulb.option(
    "target",
    "Who to target.",
    choices=list(*beasts.keys(), *pcs.keys())[:24],
    default="Random PC",
)
@lightbulb.option(
    "power",
    "Which power to use. Must use exact power name",
    default="Random",
    # autocomplete=gm_powers_auto,
)
@lightbulb.command(
    "gm_target", "GM uses beat to target entity with power.", aliases=["gm target"]
)
@lightbulb.implements(lightbulb.SlashCommand)
async def gm_target(ctx: lightbulb.Context) -> None:
    all_creatures = {**pcs, **beasts, **{pc.Name: pc for pc in pcs.values()}}
    this_beast = all_creatures.get(
        ctx.options.attacker, random.choice(list(beasts.values()))
    )
    this_target = all_creatures.get(
        ctx.options.target, random.choice(list(pcs.values()))
    )
    this_power = this_beast.Powers.get(ctx.options.power, "Attack")

    encounter = Encounter(PCs=[this_beast], Enemies=[this_target])

    await ctx.respond(
        encounter._apply_power(
            attacker=this_beast,
            targets=this_target,
            power=this_power,
            return_string=True,
        )
    )


# ------ PC TARGET ------
@pc_plugin.command()
@lightbulb.option(
    "target", "Who to target.", choices=list(beasts.keys()), default="Random"
)
@lightbulb.option(
    "power",
    "Which power to use. Must use name shown in your /pc_show_more.",
    default="Random",
    # autocomplete=pc_powers_auto,
)
@lightbulb.command("pc_target", "Target an enemy with a power.", aliases=["target"])
@lightbulb.implements(lightbulb.SlashCommand)
async def pc_target(ctx: lightbulb.Context) -> None:
    this_pc = get_user_pc(ctx.author.username)
    this_target = beasts.get(ctx.options.target)
    this_power = this_pc.Powers.get(ctx.options.power)
    if not this_power:
        this_power = this_pc.take_action(random.choice(["Major", "Minor"]))

    encounter = Encounter(PCs=[this_pc], Enemies=[this_target])

    await ctx.respond(
        encounter._apply_power(
            attacker=this_pc, targets=this_target, power=this_power, return_string=True
        )
    )


# ------ ACTIVATE BEAST ------
@pc_plugin.command()
@lightbulb.add_checks(lightbulb.has_roles(1014868119791075508))
@lightbulb.option("beast", "Bestiary entry", choices=options_gm)
@lightbulb.option("name", "Name your creature")
@lightbulb.command(
    "gm_add",
    "Activates a beast from Bestiary.",
    aliases=["add beast"],
)
@lightbulb.implements(lightbulb.SlashCommand)
async def gm_add(ctx: lightbulb.Context) -> None:
    this_beast = get_beast(ctx.author.username, ctx.options.name, ctx.options.beast)
    await ctx.respond(f"Activated {ctx.options.beast}\n{this_beast}")


# ------ REMOVE BEAST ------
@pc_plugin.command()
@lightbulb.add_checks(lightbulb.has_roles(1014868119791075508))
@lightbulb.option("name", "Which creature to remove.", choices=list(beasts.keys()))
@lightbulb.command(
    "gm_remove",
    "Removes a beast from memory.",
    aliases=["remove beast"],
)
@lightbulb.implements(lightbulb.SlashCommand)
async def gm_remove(ctx: lightbulb.Context) -> None:
    this_beast = beasts.pop(ctx.options.name)
    await ctx.respond(f"Removed {this_beast.Name}")


# ------ WOUND BEAST ------
@pc_plugin.command()
@lightbulb.add_checks(lightbulb.has_roles(1014868119791075508))
@lightbulb.option("name", "Which creature to wound.", choices=list(beasts.keys()))
@lightbulb.option("wound_val", "Damage value", default="1")
@lightbulb.option("bypass_hp", "Bypass HP", choices=["True", "False"], default=False)
@lightbulb.command(
    "gm_wound",
    "Removes a beast from memory.",
    aliases=["wound beast"],
)
@lightbulb.implements(lightbulb.SlashCommand)
async def gm_wound(ctx: lightbulb.Context) -> None:
    this_beast = beasts.pop(ctx.options.name)
    bypass_hp = True if ctx.options.bypass_hp == "True" else False
    this_beast.wound(wound_val=int(ctx.options.wound_val), bypass_HP=bypass_hp)
    await ctx.respond(this_beast)


# ------ PICK PC ------
@pc_plugin.command()
@lightbulb.option("pc", "Premade PCs", choices=options_pc)
@lightbulb.option("name", "Name your pc")
@lightbulb.command(
    "pc_select",
    "Selects a PC from premades to be associated with you.",
    aliases=["pick", "select"],
)
@lightbulb.implements(lightbulb.SlashCommand)
async def pc_select(ctx: lightbulb.Context) -> None:
    this_pc = get_user_pc(ctx.author.username, ctx.options.pc, ctx.options.name)
    await ctx.respond(f"Selected {ctx.options.pc}\n{this_pc}")


# ------ PC CHECK ------
@pc_plugin.command()
@lightbulb.option(
    "stat",
    "Stat. For no mod, use 'None'.",
    choices=[*list_stats, "None"],
    default="None",
)
@lightbulb.option("dr", "DR", choices=int_as_str, default="3")
@lightbulb.option(
    "tc",
    "TC. Two letters to represent a card by suit (S,C,H,D) and value (2,K,T, etc.). "
    + "ST for Ten of Spades.",
    default="Random",
)
@lightbulb.option("upper_lower", "[U]pper/[L]ower hand or [N]either", default="N")
@lightbulb.option("draw_n", "Draw count.", default=1)
@lightbulb.command("pc_check", "Run a check with your PC.", aliases=["check"])
@lightbulb.implements(lightbulb.SlashCommand)
async def pc_check(ctx: lightbulb.Context) -> None:
    this_pc = get_user_pc(ctx.author.username)

    await ctx.respond(
        this_pc.check_by_skill(
            TC=Card(ctx.options.tc),
            DR=int(ctx.options.dr),
            skill=ctx.options.stat,
            upper_lower=ctx.options.upper_lower,
            draw_n=int(ctx.options.draw_n),
            return_string=True,
        )
    )


# ------ PC SAVE ------
@pc_plugin.command()
@lightbulb.option(
    "stat",
    "Attrib. For no mod, use 'None'.",
    choices=[*list_attribs, "None"],
    default="None",
)
@lightbulb.option("dr", "DR", choices=int_as_str, default="3")
@lightbulb.option("upper_lower", "[U]pper/[L]ower hand or [N]either", default="N")
@lightbulb.option("draw_n", "Draw count.", default=1)
@lightbulb.command("pc_save", "Run a save against PC's TC.", aliases=["save"])
@lightbulb.implements(lightbulb.SlashCommand)
async def pc_save(ctx: lightbulb.Context) -> None:
    this_pc = get_user_pc(ctx.author.username)

    await ctx.respond(
        this_pc.save(
            DR=int(ctx.options.dr),
            attrib=ctx.options.stat,
            upper_lower=ctx.options.upper_lower,
            draw_n=ctx.options.draw_n,
            return_val=True,
            return_string=True,
        )
    )


# ------ PC DRAW ------
@pc_plugin.command()
@lightbulb.option("draw_n", "Draw count.", default="1")
@lightbulb.command("pc_draw", "Draw any number of cards.", aliases=["draw"])
@lightbulb.implements(lightbulb.SlashCommand)
async def pc_check(ctx: lightbulb.Context) -> None:
    this_pc = get_user_pc(ctx.author.username)
    await ctx.respond(this_pc.discard(n=int(ctx.options.draw_n), return_string=True))


# ------ PC DRAW TC ------
@pc_plugin.command()
@lightbulb.command("pc_draw_tc", "Draw any number of cards.", aliases=["tc"])
@lightbulb.implements(lightbulb.SlashCommand)
async def pc_draw_tc(ctx: lightbulb.Context) -> None:
    this_pc = get_user_pc(ctx.author.username)
    this_pc.draw_TC()
    await ctx.respond(this_pc)


# ------ PC FATE ------
@pc_plugin.command()
@lightbulb.command("pc_fate", "Exchange a PC's Fate Card.", aliases=["fate"])
@lightbulb.implements(lightbulb.SlashCommand)
async def pc_fate(ctx: lightbulb.Context) -> None:
    this_pc = get_user_pc(ctx.author.username)
    await ctx.respond(this_pc.exchange_fate(return_string=True))


# ------ PC REST ------
@pc_plugin.command()
@lightbulb.option("type", "Quick or Full", choices=["Quick", "Full"], default="Quick")
@lightbulb.command("pc_rest", "Rest your PC.", aliases=["rest"])
@lightbulb.implements(lightbulb.SlashCommand)
async def pc_rest(ctx: lightbulb.Context) -> None:
    this_pc = get_user_pc(ctx.author.username)
    if ctx.options.type == "Quick":
        result = this_pc.quick_rest(return_string=True)
    else:
        result = this_pc.full_rest(return_string=True)
    await ctx.respond(result)


# ------ PC WOUND ------
@pc_plugin.command()
@lightbulb.option("wound_val", "Damage value", default="1")
@lightbulb.option("bypass_hp", "Bypass HP", choices=["True", "False"], default=False)
@lightbulb.command("pc_wound", "Wound your PC. Includes AP.", aliases=["wound"])
@lightbulb.implements(lightbulb.SlashCommand)
async def pc_wound(ctx: lightbulb.Context) -> None:
    this_pc = get_user_pc(ctx.author.username)
    bypass_hp = True if ctx.options.bypass_hp == "True" else False
    this_pc.wound(wound_val=int(ctx.options.wound_val), bypass_HP=bypass_hp)
    await ctx.respond(this_pc)


# ------ PC SHOW ------
@pc_plugin.command()
@lightbulb.command("pc_show", "Show PC's basic stats.", aliases=["show"])
@lightbulb.implements(lightbulb.SlashCommand)
async def pc_show(ctx: lightbulb.Context) -> None:
    await ctx.respond(
        get_user_pc(ctx.author.username, ctx.options.pc, ctx.options.name)
    )


# ------ PC SHOW MORE ------
@pc_plugin.command()
@lightbulb.command("pc_show_more", "Show additional PC stats.", aliases=["more"])
@lightbulb.implements(lightbulb.SlashCommand)
async def pc_show_more(ctx: lightbulb.Context) -> None:
    this_pc = get_user_pc(ctx.author.username)
    non_zero_attribs = str(this_pc.Attribs).split("(")[1][:-1]
    non_zero_skills = ", ".join([f"{s}={n}" for s, n in this_pc.Skills.non_defaults])
    # Filter out default Attack
    power_names = ", ".join([p for p in this_pc.Powers.keys() if p != "Attack"])

    output = ""
    output += f"Name: {this_pc.Name}, Level {this_pc.Level} {this_pc.Role}\n"
    output += f"AR: {this_pc.AR}/{this_pc.AR_Max}, "
    output += f"Speed: {this_pc.Speed}/{this_pc.Speed_Max}\n"
    output += f"Non-zero Attribs: {non_zero_attribs}\n"
    output += f"Non-zero Skills: {non_zero_skills}\n"
    output += f"Powers: {power_names}\n"

    await ctx.respond(output)


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(pc_plugin)
    get_user_pc("Broz", "Clubs1", "1")
    get_beast("2", "Grunt")


def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(pc_plugin)
