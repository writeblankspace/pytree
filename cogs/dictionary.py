from turtle import color
import discord
from discord import app_commands
from discord.ext import commands
from pyparsing import col
from f.__index__ import *
from f.githubissues import make_github_issue
from f.dictionary import *
import traceback
import asyncio

class Dictionary(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
	
	group = app_commands.Group(name="search", description="Search commands: search the web from the bot")

	class OdDropdown(discord.ui.Select):
		def __init__(self, lemmas_results: list):
			self.lemmas_results = lemmas_results

			options = []

			# pick the first result
			result: dict = self.lemmas_results[0]
			lexicalEntries: list = result["lexicalEntries"]

			for entry in lexicalEntries:
				og_inflection_of: list = entry["inflectionOf"]
				inflection_of: list = []

				for i in og_inflection_of:
					inflection_of.append(i["text"])
				
				language = entry["language"]
				lexicalCategory = entry["lexicalCategory"]["text"]

				myod = Oxford_Search(inflection_of[0], language)
				definition = myod.dictionary.get("results")[0]["lexicalEntries"][0]["entries"][0]["senses"][0]["shortDefinitions"][0]

				options.append(
					discord.SelectOption(
						label = f"{lexicalCategory.lower()}: {', '.join(inflection_of)}",
						description=f'{definition}'
					)
				)

			# The placeholder is what will be shown when no option is chosen
			# The min and max values indicate we can only pick one of the three options
			# The options parameter defines the dropdown options. We defined this above
			super().__init__(placeholder='Select a definition...', min_values=1, max_values=1, options=options)

		async def callback(self, interaction: discord.Interaction):
			# Use the interaction object to send a response message containing
			# the user's favourite colour or choice. The self object refers to the
			# Select object, and the values attribute gets a list of the user's
			# selected options. We only want the first one.
			await interaction.response.send_message(f'{self.values[0]}')


	class OdDropdownView(discord.ui.View):
		def __init__(self, OdDropdown, lemmas_results: list):
			super().__init__()

			# Adds the dropdown to our view object.
			self.add_item(OdDropdown(lemmas_results))

	@group.command(name="dictionary")
	async def dictionary(self, interaction: discord.Interaction, word: str, ephemeral: bool = True):
		"""
		Searches the Oxford Dictionary for a word."""
		await interaction.response.defer(ephemeral=ephemeral)

		od = Oxford_Search(word)

		if od.lemmas_code == 200:
			lemmas = od.lemmas
			lemmas_results: list = lemmas.get("results") # list of dicts

			view = self.OdDropdownView(self.OdDropdown, lemmas_results)

			await interaction.followup.send(view=view)
		else:
			embed = discord.Embed(
				title = f"{word.lower().capitalize()}",
				description = "```\n" + f"Error {od.lemmas_code}: {od.lemmas['error']}```",
				colour = templates.colours["fail"]
			)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Dictionary(bot))