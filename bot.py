import json
import os

import discord
from discord.ext import commands


def get_prefix(bot, message):
    """A callable Prefix for our bot. This could be edited to allow per server prefixes."""
    if os.path.isfile('cogs/config.json'):
        with open('assets/json/config.json', 'r') as f:
            config = json.load(f)
        if config[str(message.guild.id)]['prefix']:
            prefixes = config[str(message.guild.id)]['prefix']
    else:
        prefixes = ['?']

    # Check to see if we are outside of a guild. e.g DM's etc.
    if not message.guild:
        # Only allow ? to be used in DMs
        return '?'

    # If we are in a guild, we allow for the user to mention us or use any of the prefixes in our list.
    return commands.when_mentioned_or(*prefixes)(bot, message)


# Below cogs represents our folder our cogs are in. Following is the file name. So 'meme.py' in cogs, would be cogs.meme
# Think of it like a dot path import
initial_cogs = ['cogs.members', 'cogs.owner', 'cogs.simple', 'cogs.timer', 'cogs.uptime', 'cogs.friend',
                'cogs.level', 'cogs.triumphant', 'cogs.welcome', 'cogs.wish', 'cogs.ironwork', 'cogs.canvas']
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=get_prefix, description='A bot for GoldxGuns', intents=intents)

# Here we load our extensions(cogs) listed above in [initial_extensions].
if __name__ == '__main__':
    for extension in initial_cogs:
        bot.load_extension(extension)


@bot.event
async def on_ready():
    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')
    print(f'Successfully logged in and booted...!')


token = open("token.txt", "r").readline()
bot.run(token, bot=True, reconnect=True)
