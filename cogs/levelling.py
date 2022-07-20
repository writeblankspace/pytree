import discord
from discord import app_commands
from discord.ext import commands
from f.__index__ import *
from db.db import db

class Levelling(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.full_progress = "▰"
		self.empty_progress = "▱"
		self.zwnbs = "﻿" # zero-width no-break space

		# 1 message in 60 seconds
		self.cooldown = commands.CooldownMapping.from_cooldown(1.0, 60.0, commands.BucketType.user)
	
	@commands.Cog.listener('on_message')
	async def leveling_listener(self, message: discord.Message):
		guild = str(message.guild.id)
		author = str(message.author.id)
		if message.author.bot == False and message.author != self.bot.user:
			# cooldowns
			bucket = self.cooldown.get_bucket(message)
			retry_after = bucket.update_rate_limit()
			if retry_after:
				pass
			else: # you can do stuff!
				# check stuff first to avoid errors
				db.exists([guild, author, "xp"], True, 0)
				data = db.read()
				
				randxp = random.randint(3, 10)
				data[guild][author]["xp"] += randxp

				db.write(data)
				await message.channel.send(f"<@{author}> gained {randxp} xp!")
	
	

async def setup(bot):
	await bot.add_cog(Levelling(bot))