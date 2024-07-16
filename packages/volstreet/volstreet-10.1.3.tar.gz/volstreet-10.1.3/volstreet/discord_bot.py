from discord.ext import commands
import discord
import os
import json
import asyncio


token = os.getenv("PROSPERE_DISCORD_BOT_TOKEN")

prefix = "!"
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=prefix, intents=intents)

user_id_map = {"742733209732776006": "RAHUL"}


@bot.event
async def on_ready():
    print(f"I am ready as {bot.user}")


@bot.command(name="myid")
async def get_my_id(ctx):
    await ctx.send(f"Your ID is {ctx.message.author.id}")


@bot.command(name="params")
async def see_params(ctx, client_code=None):

    if client_code is None:
        await ctx.send("Please provide your client name.")
        return

    client_code = client_code.upper()

    discord_user_id = str(ctx.message.author.id)
    if discord_user_id in user_id_map:
        # Giving myself the ability to see any client's strategy
        check = (user_id_map[discord_user_id] == client_code) or (
            user_id_map[discord_user_id] == "RAHUL"
        )
        if (
            check
        ):  # The user has correctly mentioned their client code. Allow them to proceed.
            with open(f"client_config.json", "r") as file:
                client_config = json.load(file)
            client_data = client_config.get(client_code, None)
            if client_data is None:
                await ctx.send(f"Your data is not found in the client config.")
                return
            strategies = client_data.get("strategies", None)
            if strategies is None:
                await ctx.send(f"Your strategies are none.")
                return
            json_str = json.dumps(strategies, indent=2)
            if len(json_str) > 2000:
                for strategy in strategies:
                    await ctx.send(f"```json\n{json.dumps(strategy, indent=2)}```")
                    await asyncio.sleep(0.5)
        else:
            await ctx.send(f"Provide the correct client code you cheeky monkey.")
    else:
        await ctx.send(f"Your user id is not found in the user id map.")


@bot.command(name="modify")
async def modify_strategy(
    ctx, client_code=None, strategy_index=None, key=None, value=None
):
    if client_code is None:
        await ctx.send("Please provide your client name.")
        return

    client_code = client_code.upper()

    discord_user_id = str(ctx.message.author.id)
    if discord_user_id in user_id_map:
        # Giving myself the ability to modify any client's strategy
        check = (user_id_map[discord_user_id] == client_code) or (
            user_id_map[discord_user_id] == "RAHUL"
        )
        if check:
            with open(f"client_config.json", "r") as file:
                client_config = json.load(file)
            client_data = client_config.get(client_code, None)
            if client_data is None:
                await ctx.send(f"Your data is not found in the client config.")
                return
            strategies = client_data.get("strategies", None)
            if strategies is None:
                await ctx.send(f"Your strategies are none.")
                return
            if strategy_index is None:
                await ctx.send(
                    f"Please provide the strategy index. The strategy index is the serial number of the strategy in the list of strategies. To see the list of strategies, use the `params` command."
                )
                return
            strategy_index = int(strategy_index) - 1
            if key is None:
                await ctx.send(f"Please provide the key you want to modify.")
                return
            if value is None:
                await ctx.send(f"Please provide the value you want to set.")
                return
            else:
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    await ctx.send(f"Value is not in the correct JSON format.")
                    return

            if strategy_index >= len(strategies):
                await ctx.send(f"Strategy index out of bounds.")
                return
            strategy = strategies[strategy_index]
            if (
                key not in strategy["init_params"]
                and key not in strategy["init_params"]["parameters"]
            ):
                await ctx.send(f"Parameter is invalid.")
                return
            elif key in strategy["init_params"]:
                strategy["init_params"][key] = value
            elif key in strategy["init_params"]["parameters"]:
                strategy["init_params"]["parameters"][key] = value
            client_config[client_code]["strategies"] = strategies
            with open(f"client_config.json", "w") as file:
                json.dump(client_config, file, indent=2)
            await ctx.send(
                f"Strategy modified successfully. Use the `params` command to see the changes."
            )
        else:
            await ctx.send(f"Provide the correct client code you cheeky monkey.")
    else:
        await ctx.send(f"Your user id is not found in the user id map.")


def run_bot(token):
    bot.run(token)


run_bot(token)
