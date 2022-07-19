import discord
from discord import app_commands
from discord.ext import commands
from f.__index__ import *
from f.githubissues import make_github_issue
import traceback

class utility(commands.Cog):
	def __init__(self, bot) -> None:
		self.bot = bot

	group = app_commands.Group(name="utility", description="Miscellaneous commands")

	@group.command(name='ping')
	async def ping(self, interaction: discord.Interaction):
		"""
		Displays the bot's latency. This is the time it takes for the bot to respond to a message. """
		await interaction.response.defer(ephemeral=True)

		latency = round(self.bot.latency * 1000, 2)
		embed = discord.Embed(
			title="🏓 Pong!",
			description=f'**`{latency}` ms**')

		await interaction.followup.send(embed=embed)
	
	@group.command(name="screenshot")
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

	class Issue(discord.ui.Modal, title='Issue'):
		# Our modal classes MUST subclass `discord.ui.Modal`,
		# but the title can be whatever you want.

		issuetitle = discord.ui.TextInput(
			label='Issue title',
			style=discord.TextStyle.short,
			placeholder="What is the issue about?",
		)

		body = discord.ui.TextInput(
			label='Issue body',
			style=discord.TextStyle.long,
			placeholder='Explain the issue in detail',
			required=False,
		)

		async def on_submit(self, interaction: discord.Interaction):

			make_github_issue(
				title=f"[{interaction.user.name}] {self.issuetitle.value}",
				body=f"{self.body.value}\n\n---\nSent through the bot by {interaction.user.id}",
			)

			embed = discord.Embed(
				title = "Issue submitted!", 
				description = f"**Title:** {self.issuetitle.value}\n**Body:** {self.body.value}",
				colour = templates.colours["success"]
			)
			await interaction.response.send_message(embed=embed, ephemeral=True)

		async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
			embed = discord.Embed(
				title = "Something went wrong...", 
				description = f"Please ping the developer.",
				colour = templates.colours["fail"]
			)
			await interaction.response.send_message(embed=embed, ephemeral=True)

			# Make sure we know what the error actually is
			traceback.print_tb(error.__traceback__)
		
	@app_commands.command(name="issue")
	async def issue(self, interaction: discord.Interaction):
		"""
		Creates an issue on GitHub. You can add suggestions and bug reports."""
		await interaction.response.send_modal(self.Issue())

async def setup(bot):
    await bot.add_cog(utility(bot))