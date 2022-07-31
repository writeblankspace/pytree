import discord
from discord import app_commands
from discord.ext import commands
from f.stuff.shopitems import shopitems
from f.__index__ import *
from db.db import db

class Economy(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.currency = "⭔"
		self.shopitems = shopitems
	
	group = app_commands.Group(name="economy", description=f"Economy commands: earn coins, spend coins, and more")

	# some of the economy commands will be in other cogs
	# levels: levelling up gives you some $$$
	# admin: archivemonth also removes equipped products

	@group.command(name="stats")
	@app_commands.describe(
		member = "the member to get the stats of"
	)
	async def stats(
		self,
		interaction: discord.Interaction,
		member: discord.User = None,
		ephemeral: bool = True
		) -> None:
		"""
		Gets the balance and inventory of a user. """

		if member == None:
			member = interaction.user
		else:
			member = member
		
		if member.bot:
			await interaction.response.defer(ephemeral=True)

			embed = discord.Embed(
				title = "You can't rank bots!", 
				colour = templates.colours["fail"]
			)
			await interaction.followup.send(embed=embed)
		else:
			await interaction.response.defer(ephemeral=ephemeral)
			guildid = str(interaction.guild.id)
			memberid = str(member.id)

			# do the checks to avoid errors
			db.exists([guildid, memberid, "$$$"], True, 0)
			db.exists([guildid, memberid, "xp"], True, 0)
			db.exists([guildid, memberid, "inventory"], True, [])
			db.exists([guildid, memberid, "equipped"], True, [])

			data = db.read()

			coins = data[guildid][memberid]["$$$"]
			xp = data[guildid][memberid]["xp"]
			inventorylist = data[guildid][memberid]["inventory"]
			equippedlist = data[guildid][memberid]["equipped"]

			# sort lists alphabetically
			inventorylist.sort()
			equippedlist.sort()

			# get the kill and xp multipliers
			multi = calc_multi(equippedlist, xp)
			kill_multi = multi.kill_multi
			xp_multi = multi.xp_multi

			newline = "\n"

			general = [
				f"balance:: {coins} {self.currency}",
				f"hunting multiplier:: {kill_multi - 1}",
				f"xp multiplier:: {xp_multi - 1}"
			]
			general = "\n".join(general)
			

			if len(equippedlist) == 0:
				equippedlist.append("[There are no equipped items.]")
			if len(inventorylist) == 0:
				inventorylist.append("[This inventory is empty.]")

			embed = discord.Embed(
				title = f"{member.name}'s stats",
				description = f"```asciidoc{newline}{general}```",
			)

			embed.add_field(
				name = "Equipped items",
				value = f"```{newline}{', '.join(equippedlist)}```"
			)
			embed.add_field(
				name = "Inventory",
				value = f"```{newline}{', '.join(inventorylist)}```"
			)
			await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Economy(bot))