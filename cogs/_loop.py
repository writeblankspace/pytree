from discord.ext import tasks, commands
from datetime import datetime
import discord
import json
from db.db import db
import random

class Loops(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.status.start()

	def cog_unload(self):
		self.status.cancel()

	@tasks.loop(seconds=60.0)
	async def status(self):
		# change status
		data = db.read()
		statuslist = data["status"]
		if len(statuslist) != 0:
			# pick random from statuslist
			statusname = random.choice(statuslist)

			# rich presence
			activity = discord.Activity(
				name=statusname,
				type=discord.ActivityType.watching
			)
		else:
			activity = None
		await self.bot.change_presence(activity=activity)
	
	@status.before_loop
	async def before_status(self):
		await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
	await bot.add_cog(Loops(bot))