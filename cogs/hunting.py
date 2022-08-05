import discord
from discord import app_commands
from discord.ext import commands
from f.calcmulti import calc_multi
from f.stuff.shopitems import shopitems

class Hunting(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
		self.currency = "⚇"
	
	"""
	multi = calc_multi(equippedlist, xp)
			kill_multi = multi.kill_multi
			xp_multi = multi.xp_multi """
	
	group = app_commands.Group(name="bugs", description="Bug-hunting commands: hunt bugs to earm xp and money.")



async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Hunting(bot))