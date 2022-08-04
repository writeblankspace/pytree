from discord.ext import tasks, commands
from datetime import datetime
import discord
import json
from db.db import db
import random

class Loops(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.mention = "<@&802815961979420732>"
		self.timechecker.start()

	def cog_unload(self):
		self.timechecker.cancel()

	@tasks.loop(seconds=60.0)
	async def timechecker(self):
		# change status
		data = db.read()
		statuslist = data["status"]
		if len(statuslist) != 0:
			# pick random from statuslist
			statusname = random.choice(statuslist)

			# rich presence
			activity = discord.Activity(
				# TODO change the status every so often
				name=statusname,
				type=discord.ActivityType.watching
			)
		else:
			activity = None
		await self.bot.change_presence(activity=activity)

		# reminders
		current_datetime = datetime.now()
		hour = current_datetime.hour
		minute = current_datetime.minute
		time = f"{hour}:{minute}"

		channel = self.bot.get_channel(1004294903536291870)

		with open("f/stuff/reminders.json", "r") as f:
			reminders = json.load(f)

		# check if time is in reminders
		if time in reminders.keys():
			await channel.send(f"{reminders[time]}")
	
	@timechecker.before_loop
	async def before_timechecker(self):
		await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
	await bot.add_cog(Loops(bot))