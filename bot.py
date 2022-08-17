# initiating bot
import asyncio
import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands
from f.alive import keep_alive
from f.templates import theme
import random
import typing
import logging
import asyncpg
from colorama import Fore, Back, Style, init
from db.sql import *

init(autoreset=True)
logging.basicConfig(level=logging.INFO)


# get .env secrets
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
OWNERS = os.getenv('OWNERS').split(", ")

# import cogs
initial_extensions = [
	"jishaku",
	"cogs._errors",
	"cogs._utility",
	"cogs._admin",
	"cogs._loop",
	"cogs.search",
	"cogs.levelling",
	"cogs.economy",
	"cogs.starboard",
	"cogs.notebook",
	"cogs.minigames"
]

# Discord Intents settings
intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.message_content = True

bot = commands.Bot(
	command_prefix=["$ "],
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
	b = Style.BRIGHT
	g = Fore.GREEN
	w = Fore.WHITE
	print(f'{b}{g}✅ {bot.user}{w} has connected to Discord! [{randcode}]')
	print(f'{b}{g}✅ SUCCESS: {w}logged in and booted...!')

	embed = discord.Embed(
		title=f"Connected!",
		description=f"`{randcode}`",
		color=theme.colours.green
	)

	await channel.send(embed=embed)


# run the bot
keep_alive()

async def main():
	async with bot:
		b = Style.BRIGHT
		g = Fore.GREEN
		w = Fore.WHITE

		# load extensions
		for extension in initial_extensions:
			await bot.load_extension(extension)
			print(f"{b}📥 {extension}")

		print(f"{b}{g}✅ SUCCESS: {w}{len(initial_extensions)} extensions loaded")

		await psql.init_db()
		print(f"{b}{g}✅ SUCCESS: {w}Database initialized")

		# start the bot
		await bot.start(TOKEN)

asyncio.run(main())