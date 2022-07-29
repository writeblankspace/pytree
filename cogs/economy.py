import discord
from discord import app_commands
from discord.ext import commands

class Economy(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.currency = "coins"
	
	group = app_commands.Group(name="economy", description=f"Economy commands: earn coins, spend coins, and more")

async def setup(bot):
    await bot.add_cog(Economy(bot))