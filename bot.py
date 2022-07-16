# initiating bot
import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from f.alive import keep_alive
import random

# get .env secrets
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
OWNERS = os.getenv('OWNERS').split(", ")

# import cogs
initial_extensions = [
	"jishaku",
	"cogs._err",
	"cogs._misc",
	"cogs._utility",
	"cogs.crons",
	"cogs.starboard",
	"cogs.accounts",
	"cogs.levels"
]

# rich presence
activity = discord.Activity(
	# TODO change the status every so often
	name="If the story's over, why am I still writing pages?",
	type=discord.ActivityType.listening
)

# Discord Intents settings
intents = discord.Intents.default()
intents.members = True
intents.presences = True

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

# load extensions
if __name__ == '__main__':
	for extension in initial_extensions:
		bot.load_extension(extension)
		print(f"📥 {extension}")


@bot.event
async def on_ready():
	# print the bot's status
	channel = bot.get_channel(893372556848005180)
	randcode = random.randint(1000000, 9999999)
	print(f'{bot.user} has connected to Discord! [{randcode}]')
	print(f'Successfully logged in and booted...!')

	# log channel
	await channel.send(f"------- `restart {randcode}` -------")
	# say it's connected
	await channel.send(f"`{randcode}` Connected!")
	# end it
	await channel.send(f"------- `success {randcode}` -------")

@bot.command(
	name='dump',  # name of command, like !help
	hidden=True,  # hide this command
	help="""Dumps some stuff into the dump. Only usable by owners"""
)
@commands.is_owner()
async def dump(ctx, *, content=None):
	# dump channel here
	channel = bot.get_channel(838335898755530762)
	attachment = ctx.message.attachments
	await ctx.message.delete()
	if content != None:
		# send dump to channel
		link = await channel.send(content)
		# get the message link
		link = link.jump_url
	for i in attachment:
		# send file to channel
		await channel.send(file=await i.to_file(use_cached=True))

	embed = discord.Embed(
		title='Successfully dumped!',
		description=f'[Jump to Dump]({link})'
	)
	# send message, delete after 5 seconds
	await ctx.send(embed=embed, delete_after=5)

# run the bot
keep_alive()
bot.run(TOKEN)