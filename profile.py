import json
import time
import discord
from discord.ext import commands
from discord import File

from PIL import Image, ImageDraw, ImageFont
import io


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden= True)
    @commands.is_owner()
    @commands.guild_only()
    async def build_profiles(self, ctx):
        """Run the first time. Sets up the profiles for the server."""
        users = {}

        for member in ctx.guild.members:
            users[str(member.id)] = {}

        # Writes to the JSON
        with open('profiles.json', 'w') as f:
            json.dump(users, f)

        await ctx.send("Done")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Creates the users profile in the JSON.
        with open('profiles.json', 'r') as f:
            users = json.load(f)

        users[str(member.id)] = {}

        with open('profiles.json', 'w') as f:
            json.dump(users, f)

    @commands.command()
    async def set(self, ctx, system: str, *name: str):
        """Use to set your usernames for game system. Playstation, Xbox, Steam, Uplay supported."""

        # Makes sure that the system variable is consistent.
        system = system.upper()
        name_joined = " ".join(name)

        # checks to see if the system is one of the available systems.
        if system == 'PS' or system == 'XB' or system == 'STEAM' or system == 'UPLAY' or system == 'STEAMURL':
            if system == 'STEAM' or system == 'UPLAY':
                system = system.capitalize()

            # Makes sure the Char limits are respected for each system.
            if system == 'PS' and len(name_joined) > 16:
                await ctx.send('PSN names must not exceed 16 characters')
                return

            if system == 'XB' and len(name_joined) > 16:
                await ctx.send('GamerTags must not exceed 15 characters')
                return

            if system == 'Steam' and len(name_joined) > 32:
                await ctx.send('Steam usernames must not exceed 32 characters')
                return

            if system == 'Uplay' and len(name_joined) > 15:
                await ctx.send('Uplay usernames must not exceed 12 characters')
                return

            # Opens the json.
            with open('profiles.json', 'r') as f:
                users = json.load(f)

            # Tries to add the username to the dict. If it doesn't exist it creates the nested dict.
            try:
                users[str(ctx.author.id)][system] = name_joined
            except KeyError:
                users[str(ctx.author.id)] = {}
                users[str(ctx.author.id)][system] = name_joined

            with open('profiles.json', 'w') as f:
                json.dump(users, f)

            await ctx.send(f"Successfully added your {system} ID: {name_joined}")

        else:
            await ctx.send(
                f"You need to properly format your command. Options are: PS, XB, Steam, or Uplay. You used {system}")
            return

    @commands.command()
    async def wanted(self, ctx, *text):
        """Sets the custom text on your profile card."""
        text_joined = " ".join(text)

        if len(text_joined) > 35:
            await ctx.send('Your wanted text must be smaller than 35 characters long.')
            return

        with open('profiles.json', 'r') as f:
            users = json.load(f)

        users[str(ctx.author.id)]['wantedtext'] = text_joined

        with open('profiles.json', 'w') as f:
            json.dump(users, f)

        await ctx.send(f'Successfully added the wanted text to your profile card')

    @commands.command()
    async def get(self, ctx, system: str, member: discord.Member = None):
        """Retrieves the username for the system provided."""
        if member is None:
            member = ctx.author

        # Makes sure the system is consistent.
        system = system.upper()

        if system == 'PS' or system == 'XB' or system == 'STEAM' or system == 'UPLAY':

            if system == 'STEAM' or system == 'UPLAY':
                system = system.capitalize()

            with open('profiles.json', 'r') as f:
                users = json.load(f)

            # Checks for the username for that system. If not it sends an error message.
            try:
                if users[str(member.id)]:
                    username = users[str(member.id)][system]
            except KeyError:

                if member == ctx.author:
                    await ctx.send(
                        f'You do not appear to have a profile, or do not have that system registered.'
                        f' System provided was {system}.')
                elif member != ctx.author:
                    await ctx.send(
                        f'{member.name} does not have a profile for that system. System provided was {system}')
                return
            # Sends the user name for that system.
            await ctx.send(f'{member.name}\'s username for {system} is {username}')

        # Sends an error message if you do not use a compatible system.
        else:
            await ctx.send(f'You must choose from, PS, XB, Steam or Uplay. You used {system}')

    @commands.command()
    async def delete(self, ctx, system):
        """Deletes your profile for a system. Also used to delete your custom wanted text."""

        with open('profiles.json', 'r') as f:
            users = json.load(f)

        # Standardizes the system as uppercase.
        system = system.upper()

        # Creates empty dict to use later.
        user = {}

        if system == 'WANTED':
            system = 'wantedtext'

        if system == 'STEAM' or system == 'UPLAY':
            system = system.capitalize()

        # Uses the empty dict created to put in the users information
        try:
            if users[str(ctx.author.id)][system]:
                for key in users[str(ctx.author.id)]:
                    user[key] = users[str(ctx.author.id)][key]

                system_name = list(user)

                # Searches for the system to delete and deletes it from the dict.
                for item in system_name:
                    if item == system:
                        del user[item]

                # puts the dict back into the larger one.
                users[str(ctx.author.id)] = user

                with open('profiles.json', 'w') as f:
                    json.dump(users, f)

                if system == 'wantedtext':
                    await ctx.send(f'Successfully deleted the wanted text from your profile card')

                else:
                    await ctx.send(f'Successfully deleted your profile for {system}')

        except KeyError:
            await ctx.send(f'It appears you do not have profile for that system. '
                           f'Make sure you typed it in properly. You used {system}')

    @commands.command(aliases=['Profile'])
    async def profile(self, ctx, member: discord.Member = None):
        """Is a text based profile. Includes a steam url."""
        if member is None:
            member = ctx.author
        # Empty dict to use later.
        profile = {}

        # Sends typing to the channel
        async with ctx.message.channel.typing():
            with open('profiles.json', 'r') as f:
                users = json.load(f)

            # checks to see if the user has a profile
            try:
                for key in users[str(member.id)]:
                    # Skips wanted text.
                    if key == 'wantedtext':
                        continue
                    profile[key] = users[str(member.id)][key]

            # Sends error message if the user profile isn't set up yet.
            except KeyError:
                await ctx.send('It appears you haven\'t set up your profile yet! Please use the `set` command')
                return
            # Creates embed
            profile_embed = discord.Embed(title="GoldxGuns Profile", description=f"{member.name}'s profile:")

            # Iterates through the profile dict and puts it into the embed.
            for key in profile:
                if key == 'PS':
                    system = "Playstation"
                if key == 'XB':
                    system = 'Xbox'
                if key == 'Steam':
                    system = 'Steam'
                if key == 'Uplay':
                    system = 'Uplay'
                if key == 'STEAMURL':
                    system = 'Steam URL'

                profile_embed.add_field(name=str(system), value=str(profile[key]))

            await ctx.send(embed=profile_embed)

    @commands.command(aliases=['canvas','pcard', 'profilecard'])
    async def card(self, ctx, member: discord.Member = None):
        """Shows your server profile card."""
        if member is None:
            member = ctx.author
        async with ctx.message.channel.typing():

            avatar_size = 128

            # Open image and create a copy to edit.
            background_image = Image.open("lower_res_card.png")
            background_image = background_image.convert('RGBA')
            image = background_image.copy()

            with open('profiles.json', 'r') as f:
                profiles = json.load(f)

            with open('level.json', 'r') as f:
                users = json.load(f)

            pfp_x0 = 35  # left marign for profile picture
            pfp_y0 = 105  # top marign for profile picture

            draw = ImageDraw.Draw(image)  # create new object for drawing after changing original `image`

            # Puts the user names on to the card in the correct spot.
            for key in profiles[str(member.id)]:
                text = f'{profiles[str(member.id)][key]}'
                size = 18

                # If the user names are too long it reduces the size.
                if len(text) >= 10:
                    size = 16
                if len(text) >= 16:
                    size = 14
                # creates more lines for longer usernames.
                if 20 < len(text):
                    first_line = text[:16]
                    second_line = text[17:]
                    text = first_line + "\n" + second_line

                font = ImageFont.truetype('libel_suit.ttf', size)

                if key == "PS":
                    x = 220
                    y = 188

                if key == "Uplay":
                    x = 338
                    y = 228

                if key == "XB":
                    x = 338
                    y = 188

                if key == "Steam":
                    x = 220
                    y = 228

                # Skips the wanted text and url for steam.
                if key == 'wantedtext' or key == 'STEAMURL':
                    continue

                # Draws the text onto the picture.
                draw.text((x, y), text, fill=(0, 0, 0), font=font)

            wanted_font = ImageFont.truetype('NASHVILL.ttf', 20)
            level_font = ImageFont.truetype('HELLDORA.ttf', 23)
            level_text = str(int(users[str(member.id)]['level']))
            bounty_text = f'{int(users[str(member.id)]["experience"]): ,}'

            # Checks if the user has custom wanted text. Uses a default if no custom text.
            try:
                wanted_text = profiles[str(member.id)]['wantedtext']

            except KeyError:
                wanted_text = 'Shootin, lootin and rootin tootin degeneracy'

            # Draws wanted text, level and experience.
            draw.text((12, 276), wanted_text, fill=(0, 0, 0), font=wanted_font)
            draw.text((245, 102), level_text, fill=(0, 0, 0), font=level_font)
            draw.text((260, 126), bounty_text, fill=(0, 0, 0), font=level_font)

            # Draws a rectangle around the profile picture.
            draw.rectangle(((pfp_x0 - 5, pfp_y0 - 5), (pfp_x0 + avatar_size + 4), (pfp_y0 + avatar_size + 4)),
                           fill=None, outline=(0, 0, 0), width=5)

            # Uses a default avatar and shifts it down if there is no profile picture.
            if member.avatar is None:
                avatar_image = Image.open("gigi_avatar.png")
                pfp_y0 += 10

            # if the member has a profile picture.
            elif member.avatar:
                avatar_asset = member.avatar_url_as(format='png', size=avatar_size)

                # read JPG from server to buffer (file-like object)
                buffer_avatar = io.BytesIO()
                await avatar_asset.save(buffer_avatar)
                buffer_avatar.seek(0)

                # read JPG from buffer to Image
                avatar_image = Image.open(buffer_avatar)

            # resize profile picture
            avatar_image = avatar_image.resize((avatar_size, avatar_size))

            avatar_image = avatar_image.convert('RGBA')

            # Pastes the profile picture onto the card.
            image.paste(avatar_image, (pfp_x0, pfp_y0), avatar_image)

            # create buffer
            buffer_output = io.BytesIO()

            # save PNG in buffer
            image.save(buffer_output, format='PNG')

            # move to beginning of buffer so `send()` it will read from beginning
            buffer_output.seek(0)

            # send image
            await ctx.send(file=File(buffer_output, 'myimage.png'))


def setup(bot):
    bot.add_cog(Profile(bot))
