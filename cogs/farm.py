import discord
from discord import app_commands
from discord.ext import commands
from db.sql import *
from f.__index__ import *

class Farm(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
	
	group = app_commands.Group(
		name = "farm",
		description = "Farm commands: plant crops and harvest them for cash... or lose everything in a blight"
	)

	@group.command(name="stats")
	async def stats(self, interaction: discord.Interaction) -> None:
		"""
		Gets the stats of the server's farm"""
		guildid = interaction.guild.id
		userid = interaction.user.id

		await psql.check_guild(guildid)
		await psql.check_user(userid, guildid)

		

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Farm(bot))