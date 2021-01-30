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
        self.remove_birthday.start()

    @commands.Cog.listener()
    async def on_message(self, message):
        with open(f'assets/json/config.json', 'r') as f:
            config = json.load(f)
        if str(message.channel.id) in config[str(message.guild.id)]['bot_channel'] or 'bot' in message.channel.name:
            return
        if not message.author.bot:
            if os.path.isfile(f'assets/json/server/{str(message.guild.id)}/level.json'):
                with open(f'assets/json/server/{str(message.guild.id)}/level.json', 'r') as f:
                    users = json.load(f)
                # This is checking to see if you sent a message that recieved xp in the last 30 s.
                try:
                    old_time = dt.datetime.strptime(users[message.author.id]['timestamp'],
                                                    "%Y-%m-%d %H:%M:%S")
                    current_time = dt.datetime.utcnow() - dt.timedelta(seconds=30)
                    current_time_string = dt.datetime.strftime(current_time, "%Y-%m-%d %H:%M:%S")
                    current_time_format = dt.datetime.strptime(str(current_time_string), "%Y-%m-%d %H:%M:%S")
                    if old_time >= current_time_format:
                        return
                # Needs the key error, if they haven't recieved any xp by chatting it will throw it
                except KeyError:
                    pass

                await self.update_data(users, message.author)
                await self.add_experience(users, message.author,
                                          random.randint(15, 35))
                await self.level_up(users, message.author, message.channel)
                users[str(message.author.id)]['timestamp'] = str(
                    dt.datetime.strftime(dt.datetime.utcnow(), "%Y-%m-%d %H:%M:%S"))

                # Opens JSON
                with open(f'assets/json/server/{str(message.guild.id)}/level.json', 'w') as f:
                    json.dump(users, f)
            elif not os.path.isfile(f'server/{str(message.guild.id)}/level.json'):
                return

    # This creates the user in the dict Users.
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

    # Adds the experience for the user.
    async def add_experience(self, users, user, exp):
        users[str(user.id)]['experience'] = int(
            users[str(user.id)]['experience'] + (exp + (users[str(user.id)]['level'] * 4)))

    # Checks to see if a user levels up.
    async def level_up(self, users, user, channel):
        experience = users[str(user.id)]['experience']
        lvl_start = users[str(user.id)]['level']
        lvl_end = float((round((sqrt(50 + 50 * experience) - 625) / 2, 2)))
        if lvl_end < 1:
            lvl_end = 1
        users[str(user.id)]['level'] = lvl_end
        top_5_dict = {}
        top_5 = []
        exclusion_list = await self.exlusion_list_generator(user)

        top_5_role = discord.utils.get(user.guild.roles, name="Top 5")

        # This is taking all of the users experience into a single dict.
        for key in users:
            top_5_dict[key] = users[str(user.id)]["experience"]

        # This sorts the dict by the values from highest to lowest.
        top_5_dict_sorted = {k: top_5_dict[k] for k in sorted(top_5_dict, key=top_5_dict.get, reverse=True)}

        # This is checking to see if people who are listed in the top 5 are part of the exclusion list.
        # The exclusion list includes staff, and people who have monthly award roles.
        if len(top_5_dict_sorted) >= 5:
            i = 0
            while len(top_5) < 5:
                if int(list(top_5_dict_sorted.keys())[i]) in exclusion_list:
                    i += 1
                    continue
                top_5.append(list(top_5_dict_sorted.keys())[i])
                i += 1

        # This checks
        if top_5_role.members:
            current_top_5 = list(top_5_role.members)
            member_id = []
            for member in current_top_5:
                member_id.append(member.id)

                if set(member_id) != set(list(top_5_dict_sorted)):
                    for member in current_top_5:
                        if member.id not in top_5:
                            await member.remove_roles(top_5_role)

                for member in top_5:
                    user = channel.guild.get_member(user_id=int(member))
                    await user.add_roles(top_5_role)

        if lvl_end > (int(lvl_start) + 1):
            # await channel.send(f'{user.mention} has leveled up to Level {int(lvl_end)}')
            users[str(user.id)]['level'] = lvl_end
            role = discord.utils.get(user.guild.roles, name=f"Level {int(lvl_end)}")
            # await user.add_roles(role)

    @commands.command(aliases=['rank', 'lvl'])
    async def level(self, ctx, member: discord.Member = None):
        """This tells you what your current level and experience are. It also has other various traits it tracks"""
        if member is None:
            member = ctx.message.author
        if member.bot:
            return
        try:
            with open(f'assets/json/server/{str(ctx.guild.id)}/level.json', 'r') as f:
                users = json.load(f)
            lvl = users[str(member.id)]['level']
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

    @commands.command(aliases=["create", "make"], hidden=True)
    @commands.is_owner()
    async def create_json(self, ctx):
        """Creates the JSON file for the level system"""
        try:
            if os.path.isfile(f'assets/json/server/{str(ctx.guild.id)}/level.json'):
                await ctx.channel.send('File already exists.')
                return

            elif not os.path.isfile(f'assets/json/server/{str(ctx.guild.id)}/level.json'):
                users = {}
                users[str(ctx.author.id)] = {}
                users[str(ctx.author.id)]['experience'] = 0
                users[str(ctx.author.id)]['level'] = 1
                users[str(ctx.author.id)]['timestamp'] = str(dt.datetime.strftime(
                    dt.datetime.utcnow(), "%Y-%m-%d %H:%M:%S"))

                with open(f'assets/server/{ctx.guild.id}/level.json', 'w+') as f:
                    json.dump(users, f)
                await ctx.channel.send('File Created')
                return
        except:
            await ctx.channel.send('Something went wrong, the file was not created')

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

            # Adds experience
            users[str(member.id)]['experience'] = users[str(member.id)]['experience'] + number
            await self.level_up(users, member, ctx.channel)

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
                old_time = dt.datetime.strptime(
                    users[str(ctx.message.author.id)]['thankstamp'],
                    "%Y-%m-%d %H:%M:%S")
                current_time = dt.datetime.utcnow() + dt.timedelta(seconds=86400)
                current_time_string = dt.datetime.strftime(current_time, "%Y-%m-%d %H:%M:%S")
                current_time_format = dt.datetime.strptime(str(current_time_string), "%Y-%m-%d %H:%M:%S")
                time_again = old_time + dt.timedelta(seconds=86400)

                if old_time <= current_time_format:
                    day_delay_embed = discord.Embed(title="\U0001f550 You have to wait more than 24 hours to thank "
                                                          "someone again \U0001f550")
                    day_delay_embed.set_footer(text='Time until you can thank again ')
                    day_delay_embed.timestamp = time_again

                    await ctx.send(embed=day_delay_embed)
                    return

            except KeyError:
                pass

            # Gives the person thanked XP based on their level.
            if users[str(thankee.id)]['level'] <= 10:
                experience = 50 + users[str(thankee.id)]['level'] ** 2
            elif users[str(thankee.id)]['level'] > 10:
                experience = 150 + users[str(thankee.id)]['level'] ** 1.5
            else:
                experience = 50

            # Puts the experience into the Dict.
            users[str(thankee.id)]['experience'] += experience

            # Updates data and checks for leveling up.
            await self.update_data(users, thankee)
            await self.update_data(users, ctx.message.author)

            # Adds timestamp to be chacked against
            users[str(ctx.author.id)]['thankstamp'] = str(
                dt.datetime.strftime(dt.datetime.utcnow(), "%Y-%m-%d %H:%M:%S"))

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

            # Sends information to check if the person thanked levels up
            await self.level_up(users, thankee, ctx.channel)

            # Writes it back to the JSON file and sends an Embed.
            with open(f'server/{str(ctx.guild.id)}/level.json', 'w') as f:
                json.dump(users, f)

            thank_embed = discord.Embed(
                title=f'\U0001f49d {ctx.author.name} has '
                f'thanked {thankee.name} \U0001f49d', colour=discord.Colour.gold())
            await ctx.channel.send(embed=thank_embed)

    @commands.command(aliases=['topthank', 'topthanks', 'thankleaders', 'thankleader', 'thankleaderboard'])
    async def top_thanks(self, ctx):
        """Gives the leaderboard for number of thanks recieved!"""
        if not os.path.isfile(f'server/{str(ctx.guild.id)}/level.json'):
            return

        if os.path.isfile(f'assets/json/server/{str(ctx.guild.id)}/level.json'):
            with open(f'assets/json/server / {str(ctx.guild.id)} / level.json', 'r') as f:
                users = json.load(f)

        thank_dict = {}
        user = []
        # Adds user ids to a list.
        for key in users:
            user.append(key)

        # Uses the list to generate a dict
        for key in user:
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
            member_list.append(ctx.guild.get_member(user_id=int(key)).name)
            number_list.append(str(i))
            thank_list.append(str(thank_dict_sorted[key]))
            i += 1
            if i > 15:
                break

        member_list_for_embed = "\n".join(member_list)
        number_list_for_embed = "\n".join(number_list)
        thank_list_for_embed = "\n".join(thank_list)

        thank_embed = discord.Embed(title="Thank Leaderboard")
        thank_embed.add_field(name="Position", value=f"{number_list_for_embed}", inline=True)
        thank_embed.add_field(name="Name:", value=f"{member_list_for_embed}", inline=True)
        thank_embed.add_field(name="Number of thanks:", value=f"{thank_list_for_embed}", inline=True)
        await ctx.channel.send(embed=thank_embed)

    @commands.command(aliases=['toplevel', 'leaderboard', 'expleader', 'top'])
    async def top_level(self, ctx):
        """Gives the leaderboard for people with the highest level in the server."""
        if not os.path.isfile(f'server/{str(ctx.guild.id)}/level.json'):
            return
        if os.path.isfile(f'server/{str(ctx.guild.id)}/level.json'):
            with open(f'server/{str(ctx.guild.id)}/level.json', 'r') as f:
                users = json.load(f)

        thank_dict = {}
        user = []

        # Creates a list for the users and uses that list to create a smaller dict with just their user id
        # and their experience.
        for key in users:
            user.append(key)
        for key in user:
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
            member_list.append(ctx.guild.get_member(user_id=int(key)).name)
            number_list.append(str(i))
            experience_list.append(str(exp_dict_sorted[key]))
            i += 1
            if i > 15:
                break

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

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reset(self, ctx):
        # This is for the monthly reset of the data. It also gives all of the reward roles out
        # It also removes all of the roles from the top 5 as well.

        async with ctx.message.channel.typing():
            with open('assets/json/config.json', 'r') as f:
                config = json.load(f)

            with open(f'assets/json/server/{str(ctx.guild.id)}/level.json', 'r') as f:
                users = json.load(f)

            # Initializes various lists and dicts.
            exp_dict = {}
            thanks_dict = {}
            thanked_dict = {}
            exclusion_list = await self.exlusion_list_generator(ctx.message.author)

            # Initializes the various role variables.
            top_exp_role = ctx.message.guild.get_role(int(config[str(ctx.message.guild.id)]['toptalker']))
            top_thanked_role = ctx.message.guild.get_role(int(config[str(ctx.message.guild.id)]['topthanks']))
            top_thanks_role = ctx.message.guild.get_role(int(config[str(ctx.message.guild.id)]['topthanker']))
            top_5_role = ctx.message.guild.get_role(int(config[str(ctx.message.guild.id)]['top5']))

            # Iterates over the dictionary from the JSON file.
            # each section is caught in a try except block just in case they don't have
            # any of the information in their profile.
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

                # Sorts the dicts from the highest value to the lowest value.
                exp_dict_sorted = {k: exp_dict[k] for k in sorted(exp_dict, key=exp_dict.get, reverse=True)}
                thanked_dict_sorted = {k: thanked_dict[k] for k in
                                       sorted(thanked_dict, key=thanked_dict.get, reverse=True)}
                thanks_dict_sorted = {k: thanks_dict[k] for k in sorted(thanks_dict, key=thanks_dict.get, reverse=True)}

            # This sections checks each sorted dict, and compares it against the exclusion list.
            # When the person with the highest score in each group that isn't on the list is found
            # it is stored in the corresponding variable.
            i = 0
            top_exp = list(exp_dict_sorted.keys())[0]
            if int(top_exp) in exclusion_list:
                while int(top_exp) in exclusion_list:
                    top_exp = list(exp_dict_sorted.keys())[i]
                    i += 1

            t = 0
            top_thanked = list(thanked_dict_sorted)[0]
            if int(top_thanked) in exclusion_list:
                while int(top_thanked) in exclusion_list:
                    top_thanked = list(thanked_dict_sorted.keys())[t]
                    t += 1

            j = 0
            top_thanks = list(thanks_dict_sorted)[0]
            if int(top_thanks) in exclusion_list:
                while int(top_thanks) in exclusion_list:
                    top_thanks = list(thanked_dict_sorted.keys())[j]
                    j += 1

            # Removes reward roles from previous months winners.
            for member in top_exp_role.members:
                await member.remove_roles(top_exp_role)
            for member in top_thanked_role.members:
                await member.remove_roles(top_thanked_role)
            for member in top_thanks_role.members:
                await member.remove_roles(top_thanks_role)

            # Adds the reward roles to the people with the highest score in each section.
            await ctx.message.guild.get_member(user_id=int(top_exp)).add_roles(top_exp_role)
            await ctx.message.guild.get_member(user_id=int(top_thanked)).add_roles(top_thanked_role)
            await ctx.message.guild.get_member(user_id=int(top_thanks)).add_roles(top_thanks_role)

            # Removes top 5 role
            for member in top_5_role.members:
                await member.remove_roles(top_5_role)

            # Resets all the information for all the users.
            for key in users:
                users[key]['experience'] = 0
                users[key]['level'] = 1
                users[key]['numberofthanks'] = 0
                users[key]['thanker'] = 0

            # Writes to the JSON
            with open(f'assets/json/server/{str(ctx.guild.id)}/level.json', 'w+') as f:
                json.dump(users, f)

            await ctx.send("Reset is Complete.")

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

        # checks the current time against the day stamp to see if it has been 24 hours or not.
        try:
            if dt.datetime.utcnow() <= dt.datetime.strptime(
                    users[str(ctx.author.id)]['daystamp'],
                    "%Y-%m-%d %H:%M:%S") + dt.timedelta(hours=24):
                day_delay_embed = discord.Embed(title="\U0001f550 You have to wait more than 24 hours to use your "
                                                      "daily again \U0001f550")
                day_delay_embed.set_footer(text='Time until you can use your daily bonus again ')
                day_delay_embed.timestamp = dt.datetime.strptime(users[str(ctx.author.id)]['daystamp'],
                                                                 "%Y-%m-%d %H:%M:%S") + dt.timedelta(hours=24)

                await ctx.send(embed=day_delay_embed)
                return

        except KeyError:
            pass

        # Gives a bonus if the daily is being given to someone else.
        bonus = 1
        if member.id != ctx.author.id:
            bonus = random.randint(2, 4)

        # tries to add one to the daycount, if it doesn't exist it will create the value.
        try:
            users[str(ctx.author.id)]['daycount'] += 1
        except KeyError:
            users[str(ctx.author.id)]['daycount'] = 1

        # gives experience to the member or updates their data and then gives experience.
        try:
            users[str(member.id)]["experience"] += ((60 * users[str(ctx.author.id)]['daycount']) / 2) * bonus
        except KeyError:
            await self.update_data(users, member)
            users[str(member.id)]["experience"] = ((60 * users[str(ctx.author.id)]['daycount']) / 2) * bonus

        # If you have been over 36 hours doing your daily it resets your streak.
        try:
            if dt.datetime.utcnow() > dt.datetime.strptime(users[str(ctx.author.id)]['daystamp'], "%Y-%m-%d %H:%M:%S") + \
                    dt.timedelta(hours=36):
                users[str(ctx.author.id)]["daycount"] = 1
                day_embed = discord.Embed(title="You claimed your daily XP bonus!", description="You missed the bonus "
                                                                                                "window. Your streak has "
                                                                                                "been reset to 1")
        except KeyError:
            pass

        # if you are at a streak of 5 you get a bonus.
        if users[str(ctx.author.id)]["daycount"] == 5:
            users[str(ctx.author.id)]["daycount"] = 1
            users[str(member.id)]["experience"] += 75
            day_embed = discord.Embed(title="You claimed your daily XP bonus!", description="\U00002728 Today is your "
                                                                                            "fifth day "
                                                                                            "in a row, you got even "
                                                                                            "more experience! ")

        # For streaks between 1 and 5.
        elif 5 > users[str(ctx.author.id)]["daycount"]:
            day_embed = discord.Embed(title="You claimed your daily XP bonus!",
                                      description=f"You are on day {users[str(ctx.author.id)]['daycount']}. Keep it up "
                                      f"to get to day 5!  ")

        # creates the time stamp.
        users[str(ctx.author.id)]["daystamp"] = str(
            dt.datetime.strftime(dt.datetime.utcnow(), "%Y-%m-%d %H:%M:%S"))

        # Adds a field to the embed for the friend bonus.
        if member.id != ctx.author.id:
            day_embed.add_field(name='Friend Bonus!', value=f"You gave your friend {bonus} times the amount of xp!")
        day_embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/532380077896237061/800924153053970476'
                                    '/terry_coin.png')
        await ctx.send(embed=day_embed)

        with open(f'assets/json/server/{str(ctx.guild.id)}/level.json', 'w') as f:
            json.dump(users, f)

    async def exlusion_list_generator(self, user):

        with open('assets/json/config.json', 'r') as f:
            config = json.load(f)

        # List and roles initialization
        exclusion_list = []
        ringleader_role = user.guild.get_role(int(config[str(user.guild.id)]['ringleader']))
        mod_role = user.guild.get_role(int(config[str(user.guild.id)]['mod']))
        top_exp_role = user.guild.get_role(int(config[str(user.guild.id)]['toptalker']))
        top_thanked_role = user.guild.get_role(int(config[str(user.guild.id)]['topthanks']))
        top_thanks_role = user.guild.get_role(int(config[str(user.guild.id)]['topthanker']))

        # For each group this iterates over the members in the role to add to the exclusion list.
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

    @commands.command()
    async def birthday(self, ctx, member: discord.Member):
        """Wish a user a happy birthday!"""
        with open(f'assets/json/server/{str(ctx.guild.id)}/level.json', 'r+') as f:
            users = json.load(f)
        # Time check to see if it has been a year since the command has been used for a user.
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
        # Gets t
        he_role = discord.utils.get(ctx.message.guild.roles, name='He/Him')
        she_role = discord.utils.get(ctx.message.guild.roles, name='She/Her')
        they_role = discord.utils.get(ctx.message.guild.roles, name='They/Them')
        birthday_role = discord.utils.get(ctx.guild.roles, name="Happy Birthday!")

        # checks if the member has one or another of the gender roles.
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
                                 value="Good work on makin it round the sun again without biting the dust, haha!"
                                       "Hopefully it wasn't too boring! \n"
                                       "Really though, thanks for being a part of our little posse. May your RNG"
                                       "be extra nice today and the year full of happiness and prosperity. "
                                       "Sending love from all of us here at GxG")
        await ctx.send(embed=birthday_embed)

        # Giving bonus experience and adding the timestamp.
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

    @tasks.loop(hours=8)
    async def remove_birthday(self):
        for server in self.bot.guilds:
            with open(f'assets/json/server/{str(server.id)}/level', 'r') as f:
                users = json.load(f)
            with open('assets/json/config.json', 'r') as f:
                config = json.load(f)
            # Checks every 8 hours to see if a birthday role has bee

            birthday_role = discord.utils.get(server.roles, name="Happy Birthday!")

            if birthday_role.members:
                for member in birthday_role.members:

                    if dt.datetime.utcnow() >= dt.datetime.strptime(users[str(member.id)]['bdaystamp'],
                                                                    "%Y-%m-%d %H:%M:%S") + dt.timedelta(
                                                                    hours=23):
                        await member.remove_roles(birthday_role)
                        chan = self.bot.get_channel(config[str(server.id)]['botpost'])
                        await chan.send(f"Removed birthday role from {member.name}")


def setup(bot):
    bot.add_cog(LevelCog(bot))
