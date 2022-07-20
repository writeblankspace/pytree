import discord
from discord import app_commands
from discord.ext import commands

class Levelling(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		# 1 message in 60 seconds
		self.cooldown = commands.CooldownMapping.from_cooldown(1.0, 60.0, commands.BucketType.user)
	
	@commands.Cog.listener('on_message')
	async def foo(self, message: discord.Message):
		# cooldowns
		bucket = self.cooldown.get_bucket(message)
		retry_after = bucket.update_rate_limit()
		if retry_after:
			# you're rate limited
			# helpful message here
			pass
		# you're not rate limited

async def setup(bot):
	await bot.add_cog(Levelling(bot))