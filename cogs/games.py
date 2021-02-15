from discord.ext import commands
import random


class GamesCog(commands.Cog, name='games'):
    """Contains Games"""

    def __init__(self, bot):
        self.bot = bot
        self.cards = []
        self.card_values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 'Ace', 'King', 'Queen', 'Jack']
        self.suit_values = ['Spade', 'Heart', 'Club', 'Diamond']

    @commands.command(aliases=['bljk', 'black_jack'], name='blackjack')
    async def blackjack(self, ctx):
        """Generates a set of random numbers."""
        print(1)
        card = await self.get_card()
        print(card)
        self.cards.append(card)
        print(self.cards)
        ctx.send(self.cards)

    async def get_card(self):
        value = None
        suit = None
        card = []
        while card not in self.cards:
            value = random.choice(self.card_values)
            suit = random.choice(self.suit_values)
            card = [value, suit]
        return card


def setup(bot):
    bot.add_cog(GamesCog(bot))
