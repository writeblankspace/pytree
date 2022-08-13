import discord
from discord import app_commands
from discord.ext import commands
from f.checks import *
from f.__index__ import *
from db.db import db
from cogs.levelling import Levelling
import time


class Admin(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
	
	group = app_commands.Group(name="admin", description="restricted commands that can only be used by the bot owner")

	@group.command(name="dump")
	@app_commands.describe(
		content = "the content to dump into the channel",
		attachments = "the attachments to dump into the channel"
		)
	@owner_only()
	async def dump(self, interaction: discord.Interaction, content: str = None, attachments: discord.Attachment = None) -> None:
		"""
		[RESTRICTED] Dumps the given content to the dump channel."""
		await interaction.response.defer(ephemeral=True)
		# ^ gives you 15 minutes extra to respond
		# setting ephemeral here is required to send an ephemeral follow up

		# dump channel here
		channel = self.bot.get_channel(838335898755530762)
		links = []
		attachment = attachments 
		# if I emove this and name attachments just attachment, the bot breaks and doesn't send the attachment
		# I thought the programmers in r/ProgrammerHumor were joking but nooo wth this useless line of code is important?
		if content != None:
			# send dump to channel
			link = await channel.send(content)
			# get the message link
			links.append(link.jump_url)
		if attachment != None:
			# send file to channel
			print(attachment)
			link = await channel.send(file=await attachment.to_file(use_cached=True))
			links.append(link.jump_url)
		
		description = []
		i = 1
		for link in links:
			description.append(f"[Jump to Dump ({i})]({link})")
			i += 1
		description = "\n".join(description)

		embed = discord.Embed(
			title='Successfully dumped!',
			description=description,
			color=theme.colours.green
		)
		# send message, delete after 5 seconds
		await interaction.followup.send(embed=embed)

	@group.command(name="archivemonth")
	@owner_only()
	@app_commands.describe(
		date = "the archive's id in the format YYYY/MM"
	)
	async def archivemonth(self, interaction: Interaction, date: str) -> None:
		"""
		[RESTRICTED] Archives the members' trees to their forest """
		await interaction.response.defer(ephemeral=False)

		# this command archives all the trees and puts it in the members' forests
		# the trees are archived into the archive channel to make the image links permanent

		archivechannel = self.bot.get_channel(1001804054965518436)
		guild = str(interaction.guild.id)

		# get rid of errors
		dbexists = db.exists([guild], False)
		if not dbexists:
			return
		
		data = db.read()

		levellingfuncs = Levelling(self.bot)
		find_next_level = levellingfuncs.find_next_level
		findtree = levellingfuncs.findtree

		await archivechannel.send(f"**Archiving trees for {date}**")
		
		# get all the trees
		keys = data[guild].keys()

		for key in keys:
			userid = str(key)

			db.exists([guild, userid, "forest", date], True, {})
			data = db.read()

			user = data[guild][userid]

			xp = user["xp"]
			level = find_next_level(xp).currentlevel
			tree = findtree(level)

			# get timestamp now
			timestamp = time.time()
			# round the time
			timestamp = round(timestamp)
			# make it a discord timestamp
			timestamp = f"<t:{timestamp}:R>"

			# get the user's tree
			f = discord.File(f"trees/default/{tree}.png", filename=f"{userid}'s_tree.png")
			message = await archivechannel.send(f"{userid}'s tree\n**{date}** {timestamp}", file=f)

			# get the attachment links
			attachments = message.attachments
			url = attachments[0].url
			
			# update the database
			data[guild][userid]["forest"][f"{date}"]["tree"] = url
			data[guild][userid]["forest"][f"{date}"]["xp"] = xp
			data[guild][userid]["forest"][f"{date}"]["level"] = level

			# reset the user's xp
			data[guild][userid]["xp"] = 0
			# unequip everything
			data[guild][userid]["equipped"] = []

			db.write(data)
		
		embed = discord.Embed(
			title = f"Archived {date} for {len(keys)} members.",
			color = theme.colours.green
		)

		await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Admin(bot))