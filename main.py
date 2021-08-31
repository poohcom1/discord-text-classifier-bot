import discord
from discord.ext import commands
import util.config_loader as cfg
from cog_AI import AI
from cog_stats import Stats


client = commands.Bot(command_prefix=cfg.get('prefix'))


@client.event
async def on_ready():
    print('Logged on as {0}!'.format(client.user))


client.add_cog(AI(client))
client.add_cog(Stats(client))

try:
    client.run(cfg.get('token'))
except discord.errors.LoginFailure:
    print("Auth error! Have you set the token in bot.cfg yet?")
