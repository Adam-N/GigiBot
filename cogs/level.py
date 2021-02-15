import os
import random
import datetime as dt
from math import sqrt
import discord
from discord.ext import commands, tasks
import json


class LevelCog(commands.Cog, name='Levels'):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            with open(f'assets/json/config.json', 'r') as f:
                config = json.load(f)

            if str(message.channel.id) in config[str(message.guild.id)]['bot_channel'] or 'bot' in message.channel.name:
                return
            with open(f'assets/json/server/{str(message.guild.id)}/level.json', 'r') as f:
                users = json.load(f)
            try:
                if dt.datetime.strptime(users[message.author.id]['timestamp'], "%Y-%m-%d %H:%M:%S") + \
                        dt.timedelta(seconds=30) <= dt.datetime.utcnow():
                    return
            except KeyError:
                pass
            await self.update_data(self, users, message.author)
            await self.add_experience(self, users, message.author,
                                      random.randint(170, 200))
            await self.level_up(self, users, message.author, message.channel)
            users[str(message.author.id)]['timestamp'] = str(
                dt.datetime.strftime(dt.datetime.utcnow(), "%Y-%m-%d %H:%M:%S"))
            with open(f'assets/json/server/{str(message.guild.id)}/level.json', 'w') as f:
                json.dump(users, f)

    @staticmethod
    async def update_data(self, users, user):
        if not str(user.id) in users:
            users[str(user.id)] = {}
            users[str(user.id)]['experience'] = 0
            users[str(user.id)]['level'] = 1
            users[str(user.id)]['timestamp'] = str(dt.datetime.strftime(
                dt.datetime.utcnow(), "%Y-%m-%d %H:%M:%S"))
        elif not str(user.id) in users:
            users[str(user.id)] = {}
            users[str(user.id)]['experience'] = 0
            users[str(user.id)]['level'] = 1
            users[str(user.id)]['timestamp'] = str(dt.datetime.strftime(
                dt.datetime.utcnow(), "%Y-%m-%d %H:%M:%S"))

    @staticmethod
    async def add_experience(self, users, user, exp):
        users[str(user.id)]['experience'] = int(
            users[str(user.id)]['experience'] + (exp + (exp * (0.02 * users[str(user.id)]['level']))))

    @staticmethod
    async def level_up(self, users, user, channel):
        with open('assets/json/config.json', 'r') as f:
            config = json.load(f)
        experience = users[str(user.id)]['experience']
        level_dt = 1.75
        lvl_start = users[str(user.id)]['level']
        lvl_end = sqrt(((85 ** level_dt) + (experience ** level_dt))) / (85 ** 2) + 1
        if int(lvl_end) > 5:
            lvl_end = 5
        top_5_dict = {}
        top_5 = []
        exclusion_list = await self.exclusion_list_generator(channel.guild)
        top_5_role = user.guild.get_role(int(config[str(user.guild.id)]['top5']))
        for key in users:
            top_5_dict[key] = users[key]["experience"]
        top_5_dict_sorted = {k: top_5_dict[k] for k in sorted(top_5_dict, key=top_5_dict.get, reverse=True)}
        if len(top_5_dict_sorted) >= 5:
            i = 0
            while len(top_5) < 5:
                if int(list(top_5_dict_sorted.keys())[i]) in exclusion_list:
                    i += 1
                    continue
                top_5.append(list(top_5_dict_sorted.keys())[i])
                i += 1
        if top_5_role.members:
            current_top_5 = list(top_5_role.members)
            member_id = []
            for member in current_top_5:
                member_id.append(member.id)
                if not set(member_id).issubset((set(list(top_5)))):
                    for top_5_member in current_top_5:
                        if str(top_5_member.id) not in top_5:
                            await member.remove_roles(top_5_role)
            if not set(member_id).issubset(set(list(top_5))):
                for member in top_5:
                    top_5_user = channel.guild.get_member(user_id=int(member))
                    await top_5_user.add_roles(top_5_role)

        users[str(user.id)]['level'] = lvl_end

        if lvl_end >= (int(lvl_start) + 1) and lvl_start > 1:

            if int(lvl_start) > 1:
                try:
                    await user.remove_roles(discord.utils.get(user.guild.roles, name=f"Level {int(lvl_start)}"))
                    await user.add_roles(discord.utils.get(user.guild.roles, name=f"Level {int(lvl_end)}"))
                except discord.errors.Forbidden as f:
                    # creating/opening a file
                    f = open("errors.txt", "a")

                    # writing in the file
                    f.write(str(f))

                    # closing the file
                    f.close()

        if lvl_end < 2:
                for i in range(2, 5):
                    level_check_role = discord.utils.get(user.guild.roles, name=f"Level {int(i)}")

                    if user not in level_check_role.members:
                        try:
                            await user.remove_roles(level_check_role)
                        except discord.Forbidden:
                            continue

    @commands.command(aliases=['rank', 'lvl'])
    async def level(self, ctx, member: discord.Member = None):
        """This tells you what your current level and experience are. It also has other various traits it tracks"""
        with open('assets/json/config.json', 'r') as f:
            config = json.load(f)

        if str(ctx.channel.id) in config[str(ctx.guild.id)]['bot_channel'] or 'bot' in str(ctx.channel.name):

            if member is None:
                member = ctx.message.author
            if member.bot:
                return
            try:
                with open(f'assets/json/server/{str(ctx.guild.id)}/level.json', 'r') as f:
                    users = json.load(f)
                lvl = int(users[str(member.id)]['level'])
                exp = users[str(member.id)]['experience']
                embed = discord.Embed(title='Level {}'.format(int(lvl)), description=f"{exp} XP ",
                                      color=member.top_role.colour)
                embed.set_author(name=member, icon_url=ctx.author.avatar_url)
                try:
                    thanks = users[str(member.id)]['numberofthanks']
                    embed.add_field(name="Number of thanks this month:", value=f"{thanks}")
                except KeyError:
                    pass
                try:
                    all_time_thanks = users[str(member.id)]['alltimethanks']
                    embed.add_field(name="Number of thanks all time:", value=f"{all_time_thanks}")
                except KeyError:
                    pass
                try:
                    thanker = users[str(member.id)]["thanker"]
                    embed.add_field(name="Number of times you thanked someone:", value=f'{thanker}')
                except KeyError:
                    pass
                try:
                    thanker_alltime = users[str(member.id)]["thankeralltime"]
                    embed.add_field(name="Number of times you thank someone (all-time):", value=f'{thanker_alltime}')
                except KeyError:
                    pass
                embed.set_thumbnail(url=member.avatar_url)
                await ctx.send(embed=embed)
            except:
                await ctx.send("Something seems to have gone wrong.")
        else:
            embed = discord.Embed(title='This must be done in a bot channel.')
            await ctx.send(embed=embed, delete_after=5)
            await ctx.message.delete()

    @commands.command(aliases=['build_json'], hidden=True)
    @commands.is_owner()
    @commands.guild_only()
    async def create_json(self, ctx):
        if not os.path.isfile(f'assets/json/server/{str(ctx.guild.id)}/level.json'):

            users = {}
            for member in ctx.guild.members:
                await self.update_data(self, users, member)
            with open(f'assets/json/server/{str(ctx.guild.id)}/level.json', 'w') as f:
                json.dump(users, f)
            await ctx.send("Done")

    @commands.is_owner()
    @commands.command(hidden=True)
    async def add_xp(self, ctx, number: int, member: discord.Member = None):
        """Adds XP to a member."""
        if member.bot:
            return
        if member is None:
            member = ctx.author
        if os.path.isfile(f'assets/json/server/{str(ctx.guild.id)}/level.json'):
            with open(f'assets/json/server/{str(ctx.guild.id)}/level.json', 'r') as f:
                users = json.load(f)
            users[str(member.id)]['experience'] = users[str(member.id)]['experience'] + number
            await self.level_up(self, users, member, ctx.channel)
            with open(f'assets/json/server/{str(ctx.guild.id)}/level.json', 'w+') as f:
                json.dump(users, f)
            await ctx.channel.send('XP Added')
            return
        elif not os.path.isfile(f'assets/json/server/{str(ctx.guild.id)}/level.json'):
            await ctx.channel.send("File Doesn't Exist")

    @commands.command(aliases=['thanks', 'thankyou'])
    async def thank(self, ctx, thankee: discord.Member):
        """Use this to thank another member who helps you with something! Cannot thank yourself or use in bot
        channels. """
        if thankee.bot:
            return
        with open(f'assets/json/config.json', 'r') as f:
            config = json.load(f)

        if str(ctx.channel.id) in config[str(ctx.guild.id)]['bot_channel'] or 'bot' in ctx.channel.name:
            await ctx.send('You must use this command in a non-bot channel.')
            return

        # This is the shame section.
        # It checks if the author is thanking themselves.
        if ctx.author.id == thankee.id:
            thank_yourself_embed = discord.Embed(title="\U0001f441  \U0001f441  You tried to thank yourself, shame on "
                                                       "you")
            shame_gifs = ['https://media.giphy.com/media/NSTS6t7qKTiDu/giphy.gif',
                          'https://media.giphy.com/media/vX9WcCiWwUF7G/giphy.gif',
                          'https://media.giphy.com/media/eP1fobjusSbu/giphy.gif',
                          'https://media.giphy.com/media/Db3OfoegpwajK/giphy.gif',
                          'https://media.giphy.com/media/8UGoOaR1lA1uaAN892/giphy.gif']
            thank_yourself_embed.set_image(url=random.choice(shame_gifs))
            await ctx.send(embed=thank_yourself_embed)
            return

        if os.path.isfile(f'assets/json/server/{str(ctx.guild.id)}/level.json'):
            with open(f'assets/json/server/{str(ctx.guild.id)}/level.json', 'r') as f:
                users = json.load(f)

            # This is a section that initializes the user if they don't exist in the database.
            try:
                if not users[str(thankee.id)]:
                    users[str(thankee.id)] = {}
                    users[str(thankee.id)]['experience'] = 0
                    users[str(thankee.id)]['level'] = 1
                    users[str(thankee.id)]['timestamp'] = str(dt.datetime.strftime(
                        dt.datetime.utcnow(), "%Y-%m-%d %H:%M:%S"))
            except KeyError:
                users[str(thankee.id)] = {}
                users[str(thankee.id)]['experience'] = 0
                users[str(thankee.id)]['level'] = 1
                users[str(thankee.id)]['timestamp'] = str(dt.datetime.strftime(
                    dt.datetime.utcnow(), "%Y-%m-%d %H:%M:%S"))

            # This checks to see if the user is able to thank.
            # Gives a 24 hour time limit on thanks.
            try:
                if users[str(ctx.author.id)]['thankcheck'] == 1:
                    tomorrow = dt.datetime.now(dt.timezone.utc)
                    midnight = dt.datetime.combine(tomorrow, dt.datetime.min.time())
                    day_delay_embed = discord.Embed(title="\U0001f550 You have to wait until Midnight UTC  \U0001f550")
                    day_delay_embed.set_footer(text='Thanks reset at midnight UTC. Local time:')
                    day_delay_embed.timestamp = midnight + dt.timedelta(days=1)

                    await ctx.send(embed=day_delay_embed)
                    return

            except KeyError:
                pass

            # Gives the person thanked XP based on their level.
            if users[str(thankee.id)]['level'] < 2:
                experience = 50 + users[str(thankee.id)]['level'] * 2
            elif 2 < users[str(thankee.id)]['level']:
                experience = 90 + users[str(thankee.id)]['level'] * 4
            else:
                experience = 50

            # Puts the experience into the Dict.
            users[str(thankee.id)]['experience'] += experience

            # Updates data and checks for leveling up.
            await self.update_data(self, users, thankee)
            await self.update_data(self, users, ctx.message.author)

            # Adds timestamp to be chacked against
            users[str(ctx.author.id)]['thankcheck'] = 1

            # Increases various variables, or initializes them if they don't exist.
            try:
                if users[str(thankee.id)]['numberofthanks']:
                    users[str(thankee.id)]['numberofthanks'] += 1
            except KeyError:
                users[str(thankee.id)]['numberofthanks'] = 1

            try:
                if users[str(thankee.id)]['alltimethanks']:
                    users[str(thankee.id)]['alltimethanks'] += 1
            except KeyError:
                users[str(thankee.id)]['alltimethanks'] = 1

            try:
                if users[str(ctx.author.id)]['thanker']:
                    users[str(ctx.author.id)]['thanker'] += 1
            except KeyError:
                users[str(ctx.author.id)]['thanker'] = 1
            try:
                if users[str(ctx.author.id)]['thankeralltime']:
                    users[str(ctx.author.id)]['thankeralltime'] += 1
            except KeyError:
                users[str(ctx.author.id)]['thankeralltime'] = 1

            # Writes it back to the JSON file and sends an Embed.
            with open(f'assets/json/server/{str(ctx.guild.id)}/level.json', 'w') as f:
                json.dump(users, f)

            thank_embed = discord.Embed(
                title=f'\U0001f49d {ctx.author.name} has '
                f'thanked {thankee.name} \U0001f49d', colour=discord.Colour.gold())
            await ctx.channel.send(embed=thank_embed)

            # Sends information to check if the person thanked levels up
            await self.level_up(self, users, thankee, ctx.channel)

    @commands.command(aliases=['top_thank', 'topthank', 'topthanks', 'thankleaders', 'thankleader', 'thankleaderboard'])
    async def top_thanks(self, ctx, arg: str = None):
        """Gives the leaderboard for number of thanks recieved!"""
        if not os.path.isfile(f'assets/json/server/{str(ctx.guild.id)}/level.json'):
            return
        with open('assets/json/config.json', 'r') as f:
            config = json.load(f)
        if str(ctx.channel.id) in config[str(ctx.guild.id)]['bot_channel'] or 'bot' in str(ctx.channel.name):

            if os.path.isfile(f'assets/json/server/{str(ctx.guild.id)}/level.json'):
                with open(f'assets/json/server/{str(ctx.guild.id)}/level.json', 'r') as f:
                    users = json.load(f)

            if arg == 'all':
                staff_list = []
            elif arg is None:
                staff_list = await self.staff_exclusion(ctx.guild)
            else:
                embed= discord.Embed(title='If you use `all` then everyone including staff will'
                                           ' show on the leaderboard. If you don\'t want to see staff,'
                                           ' leave it blank')
                await ctx.send(embed=embed, delete_after=5)
                await ctx.message.delete()
                return

            thank_dict = {}
            user = []
            # Adds user ids to a list.
            for key in users:
                user.append(key)

            # Uses the list to generate a dict
            for key in user:
                if int(key) in staff_list:
                    continue
                try:
                    thank_dict[key] = users[key]['numberofthanks']
                except KeyError:
                    continue

            # Sorts the dict by value from highest to lowest.
            thank_dict_sorted = {k: thank_dict[k] for k in sorted(thank_dict, key=thank_dict.get, reverse=True)}

            i = 1
            member_list = []
            number_list = []
            thank_list = []
            for key in thank_dict_sorted:
                try:
                    member_list.append(ctx.guild.get_member(user_id=int(key)).name)
                    number_list.append(str(i))
                    thank_list.append(str(thank_dict_sorted[key]))
                    i += 1
                    if i > 15:
                        break
                except AttributeError:
                    continue

            member_list_for_embed = "\n".join(member_list)
            number_list_for_embed = "\n".join(number_list)
            thank_list_for_embed = "\n".join(thank_list)

            thank_embed = discord.Embed(title="Thank Leaderboard")
            thank_embed.add_field(name="Position", value=f"{number_list_for_embed}", inline=True)
            thank_embed.add_field(name="Name:", value=f"{member_list_for_embed}", inline=True)
            thank_embed.add_field(name="Number of thanks:", value=f"{thank_list_for_embed}", inline=True)
            await ctx.channel.send(embed=thank_embed)

        else:
            embed = discord.Embed(title='This must be done in a bot channel.')
            await ctx.send(embed=embed, delete_after=5)
            await ctx.message.delete()

    @commands.command(aliases=['toplevel', 'leaderboard', 'expleader', 'top'])
    async def top_level(self, ctx, arg: str = None):
        """Gives the leaderboard for people with the highest level in the server."""
        if not os.path.isfile(f'assets/json/server/{str(ctx.guild.id)}/level.json'):
            return

        elif os.path.isfile(f'assets/json/server/{str(ctx.guild.id)}/level.json'):
            with open(f'assets/json/server/{str(ctx.guild.id)}/level.json', 'r') as f:
                users = json.load(f)

        with open('assets/json/config.json', 'r') as f:
            config = json.load(f)
        if str(ctx.channel.id) in config[str(ctx.guild.id)]['bot_channel'] or 'bot' in str(ctx.channel.name):
            if arg == 'all':
                staff_list = []
            elif arg is None:
                staff_list = await self.staff_exclusion(ctx.guild)
            else:
                embed = discord.Embed(title='If you use `all` then everyone including staff will'
                                            ' show on the leaderboard. If you don\'t want to see staff,'
                                            ' leave it blank')
                await ctx.send(embed=embed, delete_after=5)
                await ctx.message.delete()
                return

            thank_dict = {}
            user = []
            # Creates a list for the users and uses that list to create a smaller dict with just their user id
            # and their experience.
            for key in users:
                user.append(key)
            for key in user:
                if int(key) in staff_list:
                    continue
                try:
                    thank_dict[key] = int(users[key]['experience'])
                except KeyError:
                    continue

            # sorts the dictionary by the thank numbers
            exp_dict_sorted = {k: thank_dict[k] for k in sorted(thank_dict, key=thank_dict.get, reverse=True)}

            i = 1
            member_list = []
            number_list = []
            experience_list = []

            # Creates lists that include member names, positional numbers, and experience totals.
            for key in exp_dict_sorted:
                try:
                    member_list.append(ctx.guild.get_member(user_id=int(key)).name)
                    number_list.append(str(i))
                    experience_list.append(str(exp_dict_sorted[key]))
                    i += 1
                    if i > 15:
                        break
                except AttributeError:
                    pass

            # Initialize with returns so that each entry goes to a new line.
            number_list_for_embed = '\n'
            member_list_for_embed = '\n'
            exp_list_for_embed = '\n'

            # creates lists to insert into the embed.
            member_list_for_embed = member_list_for_embed.join(member_list)
            number_list_for_embed = number_list_for_embed.join(number_list)
            exp_list_for_embed = exp_list_for_embed.join(experience_list)

            thank_embed = discord.Embed(title="Leaderboard")
            thank_embed.add_field(name="Position", value=f"{number_list_for_embed}", inline=True)
            thank_embed.add_field(name="Name:", value=f"{member_list_for_embed}", inline=True)
            thank_embed.add_field(name="Amount of Experience:", value=f"{exp_list_for_embed}", inline=True)
            await ctx.channel.send(embed=thank_embed)
        else:
            embed = discord.Embed(title='This must be done in a bot channel.')
            await ctx.send(embed=embed, delete_after=5)
            await ctx.message.delete()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def generate(self, ctx):
        # This is for testing purposes only!
        # This generates random data for everyone on the server.
        x = ctx.message.guild.members
        users = {}
        if not os.path.isfile(f'assets/json/server/{str(ctx.guild.id)}/level.json'):
            for member in x:
                if not member.bot:
                    exp = random.randint(50, 100)
                    users[str(member.id)] = {}
                    users[str(member.id)]['experience'] = exp
                    users[str(member.id)]['level'] = (sqrt(625 + 100 * exp) - 25) / 20
                    users[str(member.id)]['timestamp'] = str(dt.datetime.strftime(
                        dt.datetime.utcnow(), "%Y-%m-%d %H:%M:%S"))
                    users[str(member.id)]['numberofthanks'] = random.randint(1, 20)
                    users[str(member.id)]['thanker'] = random.randint(5, 30)
                    users[str(member.id)]['thankeralltime'] = random.randint(30, 90)
                    users[str(member.id)]['alltimethanks'] = random.randint(40, 90)
                    with open(f'assets/json/server/{str(ctx.guild.id)}/level.json', 'w+') as f:
                        json.dump(users, f)
            await ctx.channel.send('File Created')

    @commands.command()
    async def daily(self, ctx, member: discord.Member = None):
        """Grants an amount of XP once every 24 hours"""
        if member is None:
            member = ctx.author
        with open(f'assets/json/server/{str(ctx.guild.id)}/level.json', 'r') as f:
            users = json.load(f)
        with open('assets/json/config.json', 'r') as f:
            config = json.load(f)
        if str(ctx.channel.id) in config[str(ctx.guild.id)]['bot_channel'] or 'bot' in str(ctx.channel.name):
            try:
                if users[str(ctx.author.id)]['daycheck'] == 1:
                    tomorrow = dt.datetime.now(dt.timezone.utc)
                    midnight = dt.datetime.combine(tomorrow, dt.datetime.min.time())
                    day_delay_embed = discord.Embed(title="\U0001f550 You have to wait until Midnight UTC \U0001f550")
                    day_delay_embed.set_footer(text='You can thank again tomorrow! Time Resets at: ')
                    day_delay_embed.timestamp = midnight + dt.timedelta(days=1)
                    await ctx.send(embed=day_delay_embed)
                    return
            except KeyError:
                pass
            bonus = 1
            if member.id != ctx.author.id:
                bonus = random.randint(2, 4)
            try:
                users[str(member.id)]["experience"] += ((60 * users[str(ctx.author.id)]['daycount']) / 2) * bonus
            except KeyError:
                await self.update_data(self, users, member)
                users[str(member.id)]["experience"] = 30 * bonus
            try:
                users[str(ctx.author.id)]['daycount'] += 1
            except KeyError:
                users[str(ctx.author.id)]['daycount'] = 1
            try:
                if dt.datetime.utcnow() > dt.datetime.strptime(users[str(ctx.author.id)]['daystamp'],
                                                               "%Y-%m-%d %H:%M:%S") + \
                        dt.timedelta(hours=36):
                    users[str(ctx.author.id)]["daycount"] = 1
                    day_embed = discord.Embed(title="You claimed your daily XP bonus!",
                                              description="You missed the bonus "
                                                          "window. Your streak has "
                                                          "been reset to 1")
            except KeyError:
                pass

            if users[str(ctx.author.id)]["daycount"] == 5:
                users[str(ctx.author.id)]["daycount"] = 0
                users[str(member.id)]["experience"] += 75
                day_embed = discord.Embed(title="You claimed your daily XP bonus!",
                                          description="\U00002728 Today is your "
                                                      "fifth day "
                                                      "in a row, you got even "
                                                      "more experience! ")
            elif 5 > users[str(ctx.author.id)]["daycount"]:
                day_embed = discord.Embed(title="You claimed your daily XP bonus!",
                                          description=f"You are on day {users[str(ctx.author.id)]['daycount']}"
                                          f". Keep it up "
                                          f"to get to day 5!  ")
            users[str(ctx.author.id)]['daycheck'] = 1
            users[str(ctx.author.id)]["daystamp"] = str(
                dt.datetime.strftime(dt.datetime.utcnow(), "%Y-%m-%d %H:%M:%S"))
            if member.id != ctx.author.id:
                day_embed.add_field(name='Friend Bonus!', value=f"You gave your friend {bonus} times the amount of xp!")
            day_embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/532380077896237061/800924153053970476'
                                        '/terry_coin.png')
            await ctx.send(embed=day_embed)
            with open(f'assets/json/server/{str(ctx.guild.id)}/level.json', 'w') as f:
                json.dump(users, f)
        else:
            embed = discord.Embed(title='This must be done in a bot channel.')
            await ctx.send(embed=embed, delete_after=5)
            await ctx.message.delete()

    @staticmethod
    async def exclusion_list_generator(server):
        with open('assets/json/config.json', 'r') as f:
            config = json.load(f)

        exclusion_list = []
        ringleader_role = server.get_role(int(config[str(server.id)]['ringleader']))
        mod_role = server.get_role(int(config[str(server.id)]['mod']))
        top_exp_role = server.get_role(int(config[str(server.id)]['toptalker']))
        top_thanked_role = server.get_role(int(config[str(server.id)]['topthanks']))
        top_thanks_role = server.get_role(int(config[str(server.id)]['topthanker']))

        for ringleader in ringleader_role.members:
            exclusion_list.append(ringleader.id)
        for mod in mod_role.members:
            exclusion_list.append(mod.id)
        for member in top_exp_role.members:
            exclusion_list.append(member.id)
        for member in top_thanked_role.members:
            exclusion_list.append(member.id)
        for member in top_thanks_role.members:
            exclusion_list.append(member.id)
        return exclusion_list

    @staticmethod
    async def staff_exclusion(server):
        with open('assets/json/config.json', 'r') as f:
            config = json.load(f)

        staff_list = []
        ringleader_role = server.get_role(int(config[str(server.id)]['ringleader']))
        mod_role = server.get_role(int(config[str(server.id)]['mod']))

        for ringleader in ringleader_role.members:
            staff_list.append(ringleader.id)
        for mod in mod_role.members:
            staff_list.append(mod.id)
        return staff_list

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def birthday(self, ctx, member: discord.Member):
        """Wish a user a happy birthday!"""
        with open(f'assets/json/server/{str(ctx.guild.id)}/level.json', 'r+') as f:
            users = json.load(f)
        with open('assets/json/config.json', 'r') as f:
            config = json.load(f)
        try:
            if dt.datetime.utcnow() <= dt.datetime.strptime(users[str(member.id)]['bdaystamp'], "%Y-%m-%d %H:%M:%S") + \
                    dt.timedelta(days=364):
                day_delay_embed = discord.Embed(title="\U0001f550 You have to wait until next year! \U0001f550 ")
                await ctx.send(embed=day_delay_embed)
                return
        except KeyError:
            pass
        except UnboundLocalError:
            pass
        he_role = discord.utils.get(ctx.message.guild.roles, name='He/Him')
        she_role = discord.utils.get(ctx.message.guild.roles, name='She/Her')
        they_role = discord.utils.get(ctx.message.guild.roles, name='They/Them')
        birthday_role = ctx.message.guild.get_role(int(config[str(ctx.message.guild.id)]['birthday']))

        if he_role in member.roles:
            birthday_embed = discord.Embed(title='\U0001f389 Happy Birthday! \U0001f389',
                                           description=f"Wish {member.display_name} a happy birthday! Let's celebrate "
                                           f"with him!")
        elif she_role in member.roles:
            birthday_embed = discord.Embed(title='\U0001f389 Happy Birthday! \U0001f389',
                                           description=f"Wish {member.display_name} a happy birthday! Let's celebrate "
                                           f"with her!")
        elif member in they_role.members:
            birthday_embed = discord.Embed(title='\U0001f389 Happy Birthday! \U0001f389',
                                           description=f"Wish {member.display_name} a happy birthday! Let's celebrate "
                                           f"with them!' ")
        else:
            birthday_embed = discord.Embed(title='\U0001f389 Happy Birthday! \U0001f389',
                                           description=f"Wish {member.display_name} a happy birthday! Let's celebrate "
                                           f"with them!")
        birthday_embed.add_field(name="\U0001f382",
                                 value="Good work on makin' it round the sun again without biting the dust, haha!"
                                       "Hopefully it wasn't too boring! \n"
                                       "Really though, thanks for being a part of our little posse. May your RNG"
                                       "be extra nice today and the year full of happiness and prosperity. "
                                       "Sending love from all of us here at GxG")
        channel = self.bot.get_channel(int(config[str(ctx.message.guild.id)]['general']))

        await channel.send(embed=birthday_embed)
        try:
            users[str(member.id)]["bdaystamp"] = str(dt.datetime.strftime(dt.datetime.utcnow(), "%Y-%m-%d %H:%M:%S"))
            users[str(member.id)]["experience"] += 350

        except KeyError:
            users[str(member.id)] = {}
            users[str(member.id)]["bdaystamp"] = str(dt.datetime.strftime(dt.datetime.utcnow(), "%Y-%m-%d %H:%M:%S"))
            users[str(member.id)]["experience"] = 350
            users[str(member.id)]["level"] = 1

        except UnboundLocalError:
            users = {}
            users[str(member.id)] = {}
            users[str(member.id)]["bdaystamp"] = str(dt.datetime.strftime(dt.datetime.utcnow(), "%Y-%m-%d %H:%M:%S"))
            users[str(member.id)]["experience"] = 350
            users[str(member.id)]["level"] = 1

        await member.add_roles(birthday_role)
        with open(f'assets/json/server/{str(ctx.guild.id)}/level.json', 'w') as f:
            json.dump(users, f)

    async def level_reset(self, server):
        # This is for the monthly reset of the data. It also gives all of the reward roles out
        # It also removes all of the roles from the top 5 as well.
        with open(f'assets/json/server/{str(server.id)}/level.json', 'r') as f:
            users = json.load(f)
        with open('assets/json/config.json', 'r') as f:
            config = json.load(f)
        exp_dict = {}
        thanks_dict = {}
        thanked_dict = {}
        exclusion_list = await self.exclusion_list_generator(server)

        top_exp_role = server.get_role(int(config[str(server.id)]['toptalker']))
        top_thanked_role = server.get_role(int(config[str(server.id)]['topthanks']))
        top_thanks_role = server.get_role(int(config[str(server.id)]['topthanker']))
        top_5_role = server.get_role(int(config[str(server.id)]['top5']))

        for key in users:
            try:
                exp_dict[key] = int(users[key]['experience'])
            except KeyError:
                pass
            try:
                thanked_dict[key] = int(users[key]['numberofthanks'])
            except KeyError:
                pass
            try:
                thanks_dict[key] = int(users[key]['thanker'])
            except KeyError:
                pass
            exp_dict_sorted = {k: exp_dict[k] for k in sorted(exp_dict, key=exp_dict.get, reverse=True)}
            thanked_dict_sorted = {k: thanked_dict[k] for k in
                                   sorted(thanked_dict, key=thanked_dict.get, reverse=True)}
            thanks_dict_sorted = {k: thanks_dict[k] for k in sorted(thanks_dict, key=thanks_dict.get, reverse=True)}
        i = 0
        top_exp = list(exp_dict_sorted.keys())[0]
        if int(top_exp) in exclusion_list:
            while int(top_exp) in exclusion_list:
                top_exp = list(exp_dict_sorted.keys())[i]
                i += 1
        exclusion_list.append(top_exp)
        t = 0
        top_thanked = list(thanked_dict_sorted)[0]
        if int(top_thanked) in exclusion_list:
            while int(top_thanked) in exclusion_list:
                top_thanked = list(thanked_dict_sorted.keys())[t]
                t += 1
        exclusion_list.append(top_thanked)
        j = 0
        top_thanks = list(thanks_dict_sorted)[0]
        if int(top_thanks) in exclusion_list:
            while int(top_thanks) in exclusion_list:
                top_thanks = list(thanked_dict_sorted.keys())[j]
                j += 1
        for member in top_exp_role.members:
            await member.remove_roles(top_exp_role)
        for member in top_thanked_role.members:
            await member.remove_roles(top_thanked_role)
        for member in top_thanks_role.members:
            await member.remove_roles(top_thanks_role)
        await server.get_member(user_id=int(top_exp)).add_roles(top_exp_role)
        await server.get_member(user_id=int(top_thanked)).add_roles(top_thanked_role)
        await server.get_member(user_id=int(top_thanks)).add_roles(top_thanks_role)
        for member in top_5_role.members:
            await member.remove_roles(top_5_role)
        for key in users:
            users[key]['experience'] = 0
            users[key]['level'] = 1
            users[key]['numberofthanks'] = 0
            users[key]['thanker'] = 0
        with open(f'assets/json/server/{str(server.id)}/level.json', 'w+') as f:
            json.dump(users, f)
        chan = self.bot.get_channel(config[str(server.id)]['botpost'])

    async def remove_birthday(self, server):
        with open(f'assets/json/server/{str(server.id)}/level.json', 'r') as f:
            users = json.load(f)
        with open('assets/json/config.json', 'r') as f:
            config = json.load(f)
        birthday_role = server.get_role(int(config[str(server.id)]['birthday']))
        if birthday_role.members:
            for member in birthday_role.members:
                try:
                    if dt.datetime.utcnow() >= dt.datetime.strptime(users[str(member.id)]['bdaystamp'],
                                                                    "%Y-%m-%d %H:%M:%S") + dt.timedelta(
                                                                    hours=18):
                        await member.remove_roles(birthday_role)
                        chan = self.bot.get_channel(int(config[str(server.id)]['botpost']))
                        await chan.send(f"Removed birthday role from {member.name}")
                except KeyError:
                    await member.remove_roles(birthday_role)
                    chan = self.bot.get_channel(int(config[str(server.id)]['botpost']))
                    await chan.send(f"No Timestamp. Removed birthday role from {member.name}")

    async def reset_timers(self, server):
        with open(f'assets/json/server/{str(server.id)}/level.json', 'r') as f:
            users = json.load(f)

        for key in users:
            users[key]['daycheck'] = 0
            users[key]['thankcheck'] = 0

        with open(f'assets/json/server/{str(server.id)}/level.json', 'w') as f:
            json.dump(users, f)

    """@commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is None and after.channel is not None:
            for channel in member.guild.channels:
                if channel.name == 'general':
                    await channel.send("Howdy")"""


def setup(bot):
    bot.add_cog(LevelCog(bot))
