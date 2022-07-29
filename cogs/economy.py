import discord
from discord import app_commands
from discord.ext import commands
from f.stuff.shopitems import shopitems

class Economy(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.currency = "coins"
		self.shopitems = shopitems
	
	group = app_commands.Group(name="economy", description=f"Economy commands: earn coins, spend coins, and more")

	# some of the economy commands will be in levelling.py

async def setup(bot):
    await bot.add_cog(Economy(bot))