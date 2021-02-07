from discord.ext import commands
import os
import json
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import discord
from cogs.level import LevelCog
from cogs.triumphant import TriumphantCog



def get_prefix(bot, message):
    if os.path.isfile('assets/json/config.json'):
        with open('assets/json/config.json', 'r') as f:
            config = json.load(f)
        if config[str(message.guild.id)]['prefix']:
            prefixes = config[str(message.guild.id)]['prefix']
    else:
        prefixes = ['?']
    if not message.guild:
        return 'w^'
    return commands.when_mentioned_or(*prefixes)(bot, message)


initial_cogs = ['cogs.owner', 'cogs.canvas', 'cogs.friend', 'cogs.ironwork', 'cogs.level', 'cogs.members',
                'cogs.simple',
                'cogs.starboard', 'cogs.timer', 'cogs.triumphant', 'cogs.uptime', 'cogs.welcome', 'cogs.wish']
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=get_prefix, description='A bot designed for GoldxGuns', intents=intents)
if __name__ == '__main__':
    for extension in initial_cogs:
        bot.load_extension(extension)
schedule = AsyncIOScheduler()


async def daily():
    """Daily Reset Timer"""
    for server in bot.guilds:
        with open(f'assets/json/config.json', 'r') as f:
            config = json.load(f)
        await LevelCog.remove_birthday(LevelCog(bot), server)
        channel = bot.get_channel(int(config[str(server.id)]['botpost']))
        await channel.send('Ran Daily Reset')


async def weekly():
    """Weekly reset timer"""
    for server in bot.guilds:
        with open(f'assets/json/config.json', 'r') as f:
            config = json.load(f)
        await TriumphantCog.triumphant_reset(TriumphantCog(bot), server)
        channel = bot.get_channel(int(config[str(server.id)]['botpost']))
        await channel.send('Ran Weekly Reset')


async def monthly():
    """Monthly reset timer"""
    for server in bot.guilds:
        with open(f'assets/json/config.json', 'r') as f:
            config = json.load(f)
        await LevelCog.level_reset(LevelCog(bot), server)
        channel = bot.get_channel(int(config[str(server.id)]['botpost']))
        await channel.send('Ran Monthly Reset')


@bot.event
async def on_ready():
    print(f'\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}')
    print(f'Successfully logged in and booted...!')
    schedule.add_job(daily, 'cron', day='*', hour=23)
    schedule.add_job(weekly, 'cron', week='*', day_of_week='sun', hour=12)
    schedule.add_job(monthly, 'cron', month='*', day='last')

    schedule.start()


async def on_disconnect():
    schedule.shutdown(wait=False)


print('\nLoading token and connecting to client...')
token = open("token.txt", "r").readline()
bot.run(token, bot=True, reconnect=True)
