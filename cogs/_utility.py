import discord
from discord.ext import commands
from cogs._help import MyHelpCommand


class utility(commands.Cog):
	def __init__(self, bot) -> None:
		self.bot = bot
		''' help command stuff
		self._original_help_command = bot.help_command
		bot.help_command = MyHelpCommand()
		bot.help_command.cog = self
		'''

	'''
	def cog_unload(self):
		# for help cmd
		self.bot.help_command = self._original_help_command
	'''

	@commands.command(
		name='ping',
		help="""Displays the bot's latency.
			This means how fast the bot works. 
			It may differ based on what command you are using.

			**Latency Table**
			`00.00 - 20.00` = seamlessly fast
			`20.00 - 30.00` = average latency
			`30.00 - 50.00` = normally slow
			`50.00 - 70.00` = somewhat slow
			`70.00 and above` = heavy duty""",
		aliases=["latency", "pong"]
	)
	async def ping(self, ctx):
		latency = round(self.bot.latency * 1000, 2)
		embed = discord.Embed(
			title="🏓 Pong!",
			description=f'**`{latency}` ms**')
		await ctx.send(embed=embed)
	
	@commands.command(
		name="screenshot",
		help="""Creates a screenshot of the given url.
			
			Uses the [this](https://www.thum.io) api to create screenshots.
			
			Try passing [a google search](https://www.google.com/search?q=google+search) as the url.
			Or you can check [the bot status](https://stats.uptimerobot.com/n7ZkztG2WV/788342560).""",
		aliases=["ss", "sc", "shot", "screen", "print", "prt", "prtsc"]
	)
	async def screenshot(self, ctx, url: str = None):
		if url == None:
			u = "https://google.com/search?q=pass+a+url+argument"
		else:
			u = url
		await ctx.send(f"https://image.thum.io/get/noanimate/{u}")


async def setup(bot):
    await bot.add_cog(utility(bot))