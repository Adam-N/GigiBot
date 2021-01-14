import json
import urllib.request

import discord
from discord.ext import commands
from discord import File

from PIL import Image, ImageDraw, ImageFont
import io


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    @commands.guild_only()
    async def build_profiles(self, ctx):
        users = {}

        for member in ctx.guild.members:
            users[str(member.id)] = {}

        # Writes to the JSON
        with open('profiles.json', 'w') as f:
            json.dump(users, f)

        await ctx.send("Done")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        with open('profiles.json', 'r') as f:
            users = json.load(f)

        users[str(member.id)] = {}

        with open('profiles.json', 'w') as f:
            json.dump(users, f)

    @commands.command()
    async def set(self, ctx, system: str, name: str):

        system = system.upper()
        print(system)

        if system == 'PS' or system == 'XB' or system == 'PC':
            with open('profiles.json', 'r') as f:
                users = json.load(f)
            try:
                users[str(ctx.author.id)][system] = name
                print(users)
            except KeyError:
                users[str(ctx.author.id)] = {}
                users[str(ctx.author.id)][system] = name

            with open('profiles.json', 'w') as f:
                json.dump(users, f)

        else:
            await ctx.send('You need to properly format your system. Options are: PS, XB, or PC')
            return

    @commands.command()
    async def get(self, ctx,system: str, member: discord.Member = None):
        if member is None:
            member = ctx.author


    @commands.command()
    async def profile(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        profile = {}

        with open('profiles.json', 'r') as f:
            users = json.load(f)
        try:
            for key in users[str(member.id)]:
                profile[key] = users[str(member.id)][key]
        except KeyError:
            ctx.send('It appears you haven\'t set up your profile yet! Please use the `?create` command')
            return

        profile_embed = discord.Embed(title="GoldxGuns Profile", description=f"{member.name}'s profile:")
        for key in profile:
            profile_embed.add_field(name=str(key), value=str(profile[key]))

        await ctx.send(embed=profile_embed)

"""

        
        # read background image only once
url = 'https://i.imgur.com/FizDC6y.png'
response = urllib.request.urlopen(url)
background_image = Image.open(response)  # it doesn't need `io.Bytes` because it `response` has method `read()`
background_image = background_image.convert('RGBA')  # add channel ALPHA to draw transparent rectangle


    @commands.command(name='canvas')
    async def canvas(self, ctx):
        AVATAR_SIZE = 128

        # --- duplicate image ----

        image = background_image.copy()

        image_width, image_height = image.size

        # --- draw on image ---

        # create object for drawing

        # draw = ImageDraw.Draw(image)

        # draw red rectangle with alpha channel on new image (with the same size as original image)

        rect_x0 = 20  # left marign
        rect_y0 = 20  # top marign

        rect_x1 = image_width - 20  # right margin
        rect_y1 = 20 + AVATAR_SIZE - 1  # top margin + size of avatar

        rect_width = rect_x1 - rect_x0
        rect_height = rect_y1 - rect_y0

        rectangle_image = Image.new('RGBA', (image_width, image_height))
        rectangle_draw = ImageDraw.Draw(rectangle_image)

        rectangle_draw.rectangle((rect_x0, rect_y0, rect_x1, rect_y1), fill=(255, 0, 0, 128))

        # put rectangle on original image

        image = Image.alpha_composite(image, rectangle_image)

        # create object for drawing

        draw = ImageDraw.Draw(image)  # create new object for drawing after changing original `image`

        # draw text in center

        text = f'Hello {ctx.author.name}'

        font = ImageFont.truetype('arial.ttf', 30)

        text_width, text_height = draw.textsize(text, font=font)
        x = (rect_width - text_width - AVATAR_SIZE) // 2  # skip avatar when center text
        y = (rect_height - text_height) // 2

        x += rect_x0 + AVATAR_SIZE  # skip avatar when center text
        y += rect_y0

        draw.text((x, y), text, fill=(0, 0, 255, 255), font=font)

        # --- avatar ---

        # get URL to avatar
        # sometimes `size=` doesn't gives me image in expected size so later I use `resize()`
        avatar_asset = ctx.author.avatar_url_as(format='jpg', size=AVATAR_SIZE)

        # read JPG from server to buffer (file-like object)
        buffer_avatar = io.BytesIO()
        await avatar_asset.save(buffer_avatar)
        buffer_avatar.seek(0)

        # read JPG from buffer to Image
        avatar_image = Image.open(buffer_avatar)

        # resize it
        avatar_image = avatar_image.resize((AVATAR_SIZE, AVATAR_SIZE))  #

        image.paste(avatar_image, (rect_x0, rect_y0))

        # --- sending image ---

        # create buffer
        buffer_output = io.BytesIO()

        # save PNG in buffer
        image.save(buffer_output, format='PNG')

        # move to beginning of buffer so `send()` it will read from beginning
        buffer_output.seek(0)

        # send image
        await ctx.send(file=File(buffer_output, 'myimage.png'))"""


def setup(bot):
    bot.add_cog(Profile(bot))
