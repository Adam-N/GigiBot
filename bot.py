import os
import json
import discord
from discord.ext import commands


def get_prefix(bot, message):
    if os.path.isfile('cogs/config.json'):
        with open('assets/json/config.json', 'r') as f:
            config = json.load(f)
        if config[str(message.guild.id)]['prefix']:
            prefixes = config[str(message.guild.id)]['prefix']
    else:
        prefixes = ['?']
    if not message.guild:
        return '?'
    return commands.when_mentioned_or(*prefixes)(bot, message)


initial_cogs = ['cogs.owner']
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=get_prefix, description='A bot designed for GoldxGuns', intents=intents)
if __name__ == '__main__':
    for extension in initial_cogs:
        bot.load_extension(extension)


@bot.event
async def on_ready():
    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')
    print(f'Successfully logged in and booted...!')


token = open("token.txt", "r").readline()
bot.run(token, bot=True, reconnect=True)