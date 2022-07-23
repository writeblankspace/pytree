# initiating bot
import asyncio
import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands
from f.alive import keep_alive
from f.templates import templates
from f.checks import *
import random
import typing
import logging

logging.basicConfig(level=logging.INFO)


# get .env secrets
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
OWNERS = os.getenv('OWNERS').split(", ")

# import cogs
initial_extensions = [
	"jishaku",
	"cogs._utility",
	"cogs.levelling"
]

# rich presence
activity = discord.Activity(
	# TODO change the status every so often
	name="nothingness",
	type=discord.ActivityType.watching
)

# Discord Intents settings
intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.message_content = True

bot = commands.Bot(
	command_prefix=["/"],
	activity=activity,
	status=discord.Status.idle,
	afk=False,
	intents=intents,
	strip_after_prefix=True,
	owner_ids=[690173341104865310, 722669121535475742],
	case_insensitive=True
)


@bot.event
async def on_ready():
	# print the bot's status
	channel = bot.get_channel(893372556848005180)
	randcode = random.randint(1000000, 9999999)
	print(f'{bot.user} has connected to Discord! [{randcode}]')
	print(f'Successfully logged in and booted...!')

	embed = discord.Embed(
		title=f"Connected!",
		description=f"`{randcode}`",
		color=templates.colours["success"]
	)

	await channel.send(embed=embed)

@bot.tree.command(name="dump")
@app_commands.describe(
	content = "the content to dump into the channel",
	attachments = "the attachments to dump into the channel"
	)
@app_commands.check(owner_only)
async def dump(interaction: discord.Interaction, content: str = None, attachments: discord.Attachment = None) -> None:
	"""
	[RESTRICTED] Dumps the given content to the dump channel."""
	await interaction.response.defer(ephemeral=True)
	# ^ gives you 15 minutes extra to respond
	# setting ephemeral here is required to send an ephemeral follow up

	# dump channel here
	channel = bot.get_channel(838335898755530762)
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

# run the bot
keep_alive()

async def main():
	async with bot:
		# load extensions
		for extension in initial_extensions:
			await bot.load_extension(extension)
			print(f"📥 {extension}")
		# start the bot
		await bot.start(TOKEN)

asyncio.run(main())