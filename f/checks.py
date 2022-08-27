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

async def enough_money_actual_check(interaction: Interaction, amount: int):
		await psql.check_user(
			interaction.user.id, interaction.guild.id
		)

		row = await psql.db.fetchrow(
			"""--sql
			SELECT balance FROM users
			WHERE userid = $1 AND guildid = $2;
			""",
			interaction.user.id, interaction.guild.id
		)

		balance = row["balance"]

		if balance < amount:
			embed = discord.Embed(
					title = f"You don't have enough money to do that.",
					description = "\n".join([f"You only have {balance} {currency}.",
						f"You'll need {amount - balance} {currency} more to run this command."]),
					color = theme.colours.red
				)
			raise CustomError(embed)
		return True

def has_enough_money(amount: int):
	async def actual_check(interaction: Interaction):
		return await enough_money_actual_check(interaction, amount)
	return app_commands.check(actual_check)

