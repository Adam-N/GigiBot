import asyncio

from discord.ext import commands
import random


class GamesCog(commands.Cog, name='games'):
    """Contains Games"""

    def __init__(self, bot):
        self.bot = bot
        self.cards = []
        self.card_values = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'Ace', 'King', 'Queen', 'Jack']
        self.face_cards = ['King', 'Queen', 'Jack']
        self.suit_values = ['Spade', 'Heart', 'Club', 'Diamond']
        self.card_emojies = {'Spade': '\U00002660\U0000fe0f', 'Heart': '\U00002665\U0000fe0f',
                             'Club': '\U00002663\U0000fe0f', 'Diamond': '\U00002666\U0000fe0f'}
        self.hit_emoji = '\U0001f1ed'
        self.stay_emoji = '\U0001f1f8'

    @commands.command(aliases=['bljk', 'black_jack'], name='blackjack')
    async def blackjack(self, ctx):
        """Generates a set of random numbers."""
        game = True
        dealer_cards = await self.deal()
        player_cards = await self.deal()
        dealer_total = 0
        player_total = 0
        dealer_card_string = ""
        player_card_string = ""

        for list in dealer_cards:
            for element in list:
                if element in self.card_values:
                    if element == 'Ace':
                        dealer_total += 1
                    elif element in self.face_cards:
                        dealer_total += 10
                    elif element < 11:
                        dealer_total += element
                if element in self.card_values:
                    dealer_card_string += str(element)
                if element in self.card_emojies.keys():
                    emoji = self.card_emojies[element]
                    dealer_card_string += emoji
                    dealer_card_string += " "

        for list in player_cards:
            for element in list:
                if element in self.card_values:
                    if element == 'Ace':
                        player_total += 1
                    elif element in self.face_cards:
                        player_total += 10
                    elif element < 11:
                        player_total += element
                if element in self.card_values:
                    player_card_string += str(element)
                if element in self.card_emojies.keys():
                    emoji = self.card_emojies[element]
                    player_card_string += emoji
                    player_card_string += " "

        dealer_message = await ctx.send(f'`Dealer Cards: {dealer_card_string}, score {dealer_total}`')
        player_message = await ctx.send(f'`Player Cards: {player_card_string}, score {player_total}`')

        dealer_message_id = dealer_message.id
        player_message_id = player_message.id

        await player_message.add_reaction(self.hit_emoji)
        await player_message.add_reaction(self.stay_emoji)
        while game == True:
            def check(reaction, user):
                if str(reaction.emoji) == self.hit_emoji and not user.bot:
                    return user == ctx.author and str(reaction.emoji) == self.hit_emoji
                if str(reaction.emoji) == self.stay_emoji and not user.bot:
                    return user == ctx.author and str(reaction.emoji) == self.hit_emoji

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send('Timed out. Try again!')
                game = False
            else:
                await player_message.remove_reaction(reaction, ctx.author)
                await ctx.send('👍')

    async def deal(self):
        card_1 = await self.get_card()
        self.cards.append(card_1)
        card_2 = await self.get_card()
        self.cards.append(card_2)
        dealt = [card_1, card_2]
        return dealt

    async def get_card(self):
        card = [random.choice(self.card_values), random.choice(self.suit_values)]
        if self.cards:
            while card in self.cards:
                card = [random.choice(self.card_values), random.choice(self.suit_values)]
        return card


def setup(bot):
    bot.add_cog(GamesCog(bot))
