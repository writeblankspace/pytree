import discord
from discord import app_commands
from discord.ext import commands

class utility(commands.Cog):
	def __init__(self, bot) -> None:
		self.bot = bot

	@app_commands.command(name='ping')
	async def ping(self, interaction: discord.Interaction):
		"""
		Displays the bot's latency. This is the time it takes for the bot to respond to a message. """
		await interaction.response.defer(ephemeral=True)

		latency = round(self.bot.latency * 1000, 2)
		embed = discord.Embed(
			title="🏓 Pong!",
			description=f'**`{latency}` ms**')

		await interaction.followup.send(embed=embed)
	
	@app_commands.command(name="screenshot")
	@app_commands.describe(
		url="the url of the website you want to screenshot. Must start with 'http://' or 'https://'"
	)
	async def screenshot(self, interaction: discord.Interaction, url: str):
		"""
		Creates a screenshot of the given url. """
		await interaction.response.defer(ephemeral=True)
		screenshot = f"https://image.thum.io/get/noanimate/{url}"
		await interaction.followup.send(f"**This may take a while to load.**\n{screenshot}")
	
	@screenshot.autocomplete("url")
	async def screenshot_autocomplete(self, interaction: discord.Interaction, current: str):
		return [
			app_commands.Choice(
				name='https://www.google.com/search?q=google+search', 
				value='https://www.google.com/search?q=google+search'
			),
			app_commands.Choice(
				name='https://discord.com', 
				value='https://discord.com'
			),
			app_commands.Choice(
				name="https://github.com/writeblankspace/pytree",
				value="https://github.com/writeblankspace/pytree"
			)
		]


async def setup(bot):
    await bot.add_cog(utility(bot))