import discord
from discord import app_commands
from discord.ext import commands
from f.checks import *
from f.__index__ import *

class Admin(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
	
	group = app_commands.Group(name="admin", description="restricted commands that can only be used by the bot owner")

	@group.command(name="dump")
	@app_commands.describe(
		content = "the content to dump into the channel",
		attachments = "the attachments to dump into the channel"
		)
	@app_commands.check(owner_only)
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
			color=templates.colours["success"]
		)
		# send message, delete after 5 seconds
		await interaction.followup.send(embed=embed)

	@dump.error
	async def owneronly_error(
		interaction: Interaction,
		error: app_commands.AppCommandError
	):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(
				title = "Restricted Command", 
				description = "This command is restricted to the bot owner only.",
				colour = templates.colours["fail"]
			)
			await interaction.response.send_message(embed=embed, ephemeral=True)
			return

		raise error

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Admin(bot))