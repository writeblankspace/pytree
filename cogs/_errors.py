from discord import Interaction, app_commands
import discord
from discord.app_commands import AppCommandError
from discord.ext import commands
from f.__index__ import *


class Errors(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		bot.tree.on_error = self.on_app_command_error

	# the global error handler
	async def on_app_command_error(self, interaction: Interaction,error: AppCommandError):
		if isinstance(error, CustomError):
			embed = error.args[0]
			await interaction.response.send_message(embed=embed, ephemeral=True)
		else:
			# default error handler
			await app_commands.CommandTree.on_error(self.bot.tree, interaction, error) 

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Errors(bot))