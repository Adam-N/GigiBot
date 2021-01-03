import os
import random
import datetime as dt
from math import sqrt
import discord
from discord.ext import commands
import json


class LevelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            if os.path.isfile('level.json'):
                with open('level.json', 'r') as f:
                    users = json.load(f)
                # This is checking to see if you sent a message that recieved xp in the last 30 s.
                try:
                    old_time = dt.datetime.strptime(users[str(message.guild.id)][str(message.author.id)]['timestamp'],
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
                                          random.randint(50, 100))
                await self.level_up(users, message.author, message.channel)
                users[str(message.author.id)]['timestamp'] = str(
                    dt.datetime.strftime(dt.datetime.utcnow(), "%Y-%m-%d %H:%M:%S"))

                with open('level.json', 'w') as f:
                    json.dump(users, f)
            elif not os.path.isfile('level.json'):
                return

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

    async def add_experience(self, users, user, exp):
        users[str(user.id)]['experience'] = int(
            users[str(user.id)]['experience'] + (exp + (users[str(user.id)]['level'] * 4)))

    async def level_up(self, users, user, channel):
        experience = users[str(user.id)]['experience']
        lvl_start = users[str(user.id)]['level']
        lvl_end = float((round((sqrt(625 + 100 * experience) - 25) / 20, 2)))
        if lvl_end < 1:
            lvl_end = 1
        users[str(user.id)]['level'] = lvl_end
        top_5_dict = {}
        top_5 = []
        exclusion_list = await self.exlusion_list_generator(user)

        top_5_role = discord.utils.get(user.guild.roles, name="Top 5")

        for key in users:
            top_5_dict[key] = users[str(user.id)]["experience"]

        top_5_dict_sorted = {k: top_5_dict[k] for k in sorted(top_5_dict, key=top_5_dict.get, reverse=True)}

        i = 0
        while len(top_5) < 5:
            if int(list(top_5_dict_sorted.keys())[i]) in exclusion_list:
                i += 1
                continue
            top_5.append(list(top_5_dict_sorted.keys())[i])
            i += 1

        current_top_5 = list(top_5_role.members)
        for member in current_top_5:
            if str(member.id) not in top_5:
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
    async def level(self, ctx):
        try:
            user = ctx.message.author
            with open('level.json', 'r') as f:
                users = json.load(f)
            lvl = users[str(user.id)]['level']
            exp = users[str(user.id)]['experience']
            embed = discord.Embed(title='Level {}'.format(int(lvl)), description=f"{exp} XP ",
                                  color=ctx.author.top_role.colour)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
            try:
                thanks = users[str(user.id)]['numberofthanks']
                embed.add_field(name="Number of thanks this month:", value=f"{thanks}")
            except KeyError:
                pass
            try:
                all_time_thanks = users[str(user.id)]['alltimethanks']
                embed.add_field(name="Number of thanks all time:", value=f"{all_time_thanks}")
            except KeyError:
                pass
            try:
                thanker = users[str(user.id)]["thanker"]
                embed.add_field(name="Number of times you thanked someone:", value=f'{thanker}')
            except KeyError:
                pass
            try:
                thanker_alltime = users[str(user.id)]["thankeralltime"]
                embed.add_field(name="Number of times you thank someone (all-time):", value=f'{thanker_alltime}')
            except KeyError:
                pass
            embed.set_thumbnail(url=user.avatar_url)
            await ctx.send(embed=embed)
        except:
            await ctx.send("Something seems to have gone wrong.")

    @commands.command(aliases=["create", "make"])
    async def create_json(self, ctx):
        try:
            if os.path.isfile('level.json'):
                await ctx.channel.send('File already exists.')
                return

            elif not os.path.isfile('level.json'):
                users = {}
                users[str(ctx.author.id)] = {}
                users[str(ctx.author.id)]['experience'] = 0
                users[str(ctx.author.id)]['level'] = 1
                users[str(ctx.author.id)]['timestamp'] = str(dt.datetime.strftime(
                    dt.datetime.utcnow(), "%Y-%m-%d %H:%M:%S"))

                with open('level.json', 'w+') as f:
                    json.dump(users, f)
                await ctx.channel.send('File Created')
                return
        except:
            await ctx.channel.send('Something went wrong, the file was not created')

    @commands.command()
    async def add_xp(self, ctx, number: int):

        if os.path.isfile('level.json'):
            with open('level.json', 'r') as f:
                users = json.load(f)
            users[str(ctx.author.id)]['experience'] = users[str(ctx.author.id)]['experience'] + number
            await self.level_up(users, ctx.author, ctx.channel)

            with open('level.json', 'w+') as f:
                json.dump(users, f)
            await ctx.channel.send('XP Added')
            return
        elif not os.path.isfile('level.json'):
            await ctx.channel.send("File Doesn't Exist")

    @commands.command(aliases=['thanks', 'thankyou'])
    async def thank(self, ctx, thankee: discord.Member):
        if thankee.bot:
            return
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
        if os.path.isfile('level.json'):
            with open('level.json', 'r') as f:
                users = json.load(f)
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
            if users[str(thankee.id)]['level'] <= 10:
                experience = 50 + users[str(thankee.id)]['level'] ** 2
            elif users[str(thankee.id)]['level'] > 10:
                experience = 150 + users[str(thankee.id)]['level'] ** 1.5
            else:
                experience = 50

            users[str(thankee.id)]['experience'] += experience
            await self.update_data(users, thankee)
            await self.level_up(users, thankee, ctx.channel)

            await self.update_data(users, ctx.message.author)
            users[str(ctx.author.id)]['thankstamp'] = str(
                dt.datetime.strftime(dt.datetime.utcnow(), "%Y-%m-%d %H:%M:%S"))

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
                users[str(ctx.author.id)]['thanker'] += 1
            try:
                if users[str(ctx.author.id)]['thankeralltime']:
                    users[str(ctx.author.id)]['thankeralltime'] += 1
            except KeyError:
                users[str(ctx.author.id)]['thankeralltime'] = 1

            with open('level.json', 'w+') as f:
                json.dump(users, f)
            thank_embed = discord.Embed(
                title=f'\U0001f49d {ctx.author.name} has '
                f'thanked {thankee.name} \U0001f49d', colour=discord.Colour.gold())
            await ctx.channel.send(embed=thank_embed)

    @commands.command(aliases=['topthank', 'topthanks', 'thankleaders', 'thankleader', 'thankleaderboard'])
    async def top_thanks(self, ctx):
        if not os.path.isfile('level.json'):
            return
        if os.path.isfile('level.json'):
            with open('level.json', 'r') as f:
                users = json.load(f)

        thank_dict = {}
        user = []
        for key in users:
            user.append(key)
        for key in user:
            try:
                thank_dict[key] = users[key]['numberofthanks']
            except KeyError:
                continue

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

        number_list_for_embed = '\n'
        member_list_for_embed = '\n'
        thank_list_for_embed = '\n'
        member_list_for_embed = member_list_for_embed.join(member_list)
        number_list_for_embed = number_list_for_embed.join(number_list)
        thank_list_for_embed = thank_list_for_embed.join(thank_list)

        thank_embed = discord.Embed(title="Thank Leaderboard")
        thank_embed.add_field(name="Position", value=f"{number_list_for_embed}", inline=True)
        thank_embed.add_field(name="Name:", value=f"{member_list_for_embed}", inline=True)
        thank_embed.add_field(name="Number of thanks:", value=f"{thank_list_for_embed}", inline=True)
        await ctx.channel.send(embed=thank_embed)

    @commands.command(aliases=['toplevel', 'leaderboard', 'expleader', 'top'])
    async def top_level(self, ctx):
        if not os.path.isfile('level.json'):
            return
        if os.path.isfile('level.json'):
            with open('level.json', 'r') as f:
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

    @commands.command()
    @commands.is_owner()
    async def reset(self, ctx):
        async with ctx.message.channel.typing():
            with open('level.json', 'r') as f:
                users = json.load(f)
            exp_dict = {}
            thanks_dict = {}
            thanked_dict = {}
            exclusion_list = await self.exlusion_list_generator(ctx.message.author)

            top_exp_role = discord.utils.get(ctx.message.guild.roles, name="Most Wanted")
            top_thanked_role = discord.utils.get(ctx.message.guild.roles, name="Most Helpful")
            top_thanks_role = discord.utils.get(ctx.message.guild.roles, name="Most Thankful")
            top_5_role = discord.utils.get(ctx.message.guild.roles, name="Top 5")

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
                thanked_dict_sorted = {k: thanked_dict[k] for k in sorted(thanked_dict, key=thanked_dict.get, reverse=True)}
                thanks_dict_sorted = {k: thanks_dict[k] for k in sorted(thanks_dict, key=thanks_dict.get, reverse=True)}

            i = 1
            top_exp = list(exp_dict_sorted.keys())[0]
            if int(top_exp) in exclusion_list:
                while int(top_exp) in exclusion_list:
                    top_exp = list(exp_dict_sorted.keys())[i]
                    i += 1

            t = 1
            top_thanked = list(thanked_dict_sorted)[0]
            print(top_thanked)
            if int(top_thanked) in exclusion_list:
                while int(top_thanked) in exclusion_list:
                    top_thanked = list(thanked_dict_sorted.keys())[t]
                    t += 1

            j = 1
            top_thanks = list(thanks_dict_sorted)[0]
            if int(top_thanks) in exclusion_list:
                while int(top_thanks) in exclusion_list:
                    print(j)
                    top_thanked = list(thanked_dict_sorted.keys())[j]
                    j += 1

            for member in top_exp_role.members:
                await member.remove_roles(top_exp_role)
            for member in top_thanked_role.members:
                await member.remove_roles(top_thanked_role)
            for member in top_thanks_role.members:
                await member.remove_roles(top_thanks_role)

            await ctx.message.guild.get_member(user_id=int(top_exp)).add_roles(top_exp_role)
            await ctx.message.guild.get_member(user_id=int(top_thanked)).add_roles(top_thanked_role)
            await ctx.message.guild.get_member(user_id=int(top_thanks)).add_roles(top_thanks_role)

            for member in top_5_role.members:
                await member.remove_roles(top_5_role)

            for key in users:
                users[key]['experience'] = 0
                users[key]['level'] = 1
                users[key]['numberofthanks'] = 0
                users[key]['thanker'] = 0

            with open('level.json', 'w+') as f:
                json.dump(users, f)

            await ctx.send("Reset is Complete")

    @commands.command()
    @commands.is_owner()
    async def generate(self, ctx):
        x = ctx.message.guild.members
        users = {}

        if not os.path.isfile('level.json'):
            for member in x:
                if not member.bot:
                    exp = random.randint(150, 2000)
                    users[str(member.id)] = {}
                    users[str(member.id)]['experience'] = exp
                    users[str(member.id)]['level'] = (sqrt(625 + 100 * exp) - 25) / 20
                    users[str(member.id)]['timestamp'] = str(dt.datetime.strftime(
                        dt.datetime.utcnow(), "%Y-%m-%d %H:%M:%S"))
                    users[str(member.id)]['numberofthanks'] = random.randint(1, 20)
                    users[str(member.id)]['thanker'] = random.randint(5, 30)
                    users[str(member.id)]['thankeralltime'] = random.randint(30, 90)
                    users[str(member.id)]['alltimethanks'] = random.randint(40, 90)

                    with open('level.json', 'w+') as f:
                        json.dump(users, f)
            await ctx.channel.send('File Created')

    async def exlusion_list_generator(self, user):
        exclusion_list = []
        ringleader_role = discord.utils.get(user.guild.roles, name="Ringleaders/Officer")
        mod_role = discord.utils.get(user.guild.roles, name="Enforcers/Moderator")
        top_exp_role = discord.utils.get(user.guild.roles, name="Most Wanted")
        top_thanked_role = discord.utils.get(user.guild.roles, name="Most Helpful")
        top_thanks_role = discord.utils.get(user.guild.roles, name="Most Thankful")

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


def setup(bot):
    bot.add_cog(LevelCog(bot))
