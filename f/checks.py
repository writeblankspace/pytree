from discord import app_commands, Interaction
from discord.app_commands import CheckFailure
from db.db import db
from f.__index__ import theme
import discord

currency = "⚇"

async def owner_only(interaction: Interaction):
    return await interaction.client.is_owner(interaction.user)

class TooBroke(CheckFailure):
	pass

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
						f"You'll need {amount - balance} more to run this command."]),
					color = theme.colours.red
				)
			raise TooBroke(embed)
		return True
	return app_commands.check(actual_check)

