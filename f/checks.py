from discord import app_commands, Interaction
from discord.app_commands import CheckFailure
from db.db import db
from db.sql import *
from f.__index__ import theme
import discord

currency = "⚇"

class CustomError(CheckFailure):
	pass

def owner_only():
	async def actual_check(interaction: Interaction):
		is_owner =  await interaction.client.is_owner(interaction.user)
		if not is_owner:
			embed = discord.Embed(
				title = "Restricted Command", 
				description = "This command is restricted to the bot owner only.",
				colour = theme.colours.red
			)
			raise CustomError(embed)
		return True
	return app_commands.check(actual_check)

def has_enough_money(amount: int):
	async def actual_check(interaction: Interaction):
		
		guildid = str(interaction.guild.id)
		userid = str(interaction.user.id)
		db.exists([guildid, userid, "$$$"], True, 0)
		data = db.read()

		balance = data[guildid][userid]["$$$"]

		if balance < amount:
			embed = discord.Embed(
					title = f"You don't have enough money to do that.",
					description = "\n".join([f"You only have {balance} {currency}.",
						f"You'll need {amount - balance} {currency} more to run this command."]),
					color = theme.colours.red
				)
			raise CustomError(embed)
		return True
	return app_commands.check(actual_check)

