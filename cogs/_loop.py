from discord.ext import tasks, commands
from datetime import datetime
import json

class Loops(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.channel = bot.get_channel(1004294903536291870)
		self.mention = "<@&802815961979420732>"
		self.timechecker.start()

	def cog_unload(self):
		self.timechecker.cancel()

	@tasks.loop(seconds=60.0)
	async def timechecker(self):
		current_datetime = datetime.now()
		hour = current_datetime.hour
		minute = current_datetime.minute
		time = f"{hour}:{minute}"

		with open("f/stuff/reminders.json", "r") as f:
			reminders = json.load(f)

		# check if time is in reminders
		if time in reminders.keys():
			await self.channel.send(f"**{time}** {self.mention}" + "\n" + reminders[time])
	
	@timechecker.before_loop
	async def before_timechecker(self):
		await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
	await bot.add_cog(Loops(bot))