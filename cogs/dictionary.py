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

				definition = ""
				while definition == "":
					for result in myod.dictionary.get("results"):
						lexicalEntries = result["lexicalEntries"][0]
						if lexicalEntries["lexicalCategory"]["text"].lower() == lexicalCategory.lower():
							definition = lexicalEntries["entries"][0]["senses"][0]["shortDefinitions"][0]
					
					if definition == "":
						# this wouldn't work so move on to the next entry
						definition = None

				if definition != None:
					options.append(
						discord.SelectOption(
							label = f"{lexicalCategory.lower()}: {', '.join(inflection_of)}",
							description=f'{definition}'
						)
					)

			super().__init__(placeholder='Select a definition...', min_values=1, max_values=1, options=options)

		async def callback(self, interaction: discord.Interaction):
			await interaction.response.defer()
			choice: str = self.values[0]
			lexicalCategory: str = choice.split(': ')[0]
			word: str = choice.split(': ')[1]

			# find out which entry it is
			myod = Oxford_Search(word)

			for result in myod.dictionary.get("results"):
				lexicalEntries: dict = result["lexicalEntries"][0]
				if lexicalEntries["lexicalCategory"]["text"].lower() == lexicalCategory.lower():
					entry: dict = lexicalEntries["entries"][0]
			
			index = 0

			embed = dictionary_embed(
				word = word,
				lexicalCategory = lexicalCategory,
				entry = entry,
				index = index,
			)

			self.view.word = word
			self.view.lexicalCategory = lexicalCategory
			self.view.entry = entry
			self.view.index = index
			
			all_buttons = self.view.children
			# get button
			left = discord.utils.get(all_buttons, custom_id="left")
			right = discord.utils.get(all_buttons, custom_id="right")
			if left == None and right == None:
				self.view.add_item(self.view.left)
				self.view.add_item(self.view.right)

			self.view.disable_buttons()
			
			await interaction.edit_original_response(embed=embed, view=self.view)

	class OdDropdownView(discord.ui.View):
		def __init__(self, OdDropdown, lemmas_results: list):
			super().__init__()

			# Adds the dropdown to our view object.
			self.add_item(OdDropdown(lemmas_results))
		
			self.word = None
			self.lexicalCategory = None
			self.entry = None
			self.index = None

			self.remove_item(self.left)
			self.remove_item(self.right)

		def disable_buttons(self):
			senses: list = self.entry["senses"]

			all_buttons = self.children

			leftbutton: discord.ui.Button = discord.utils.get(all_buttons, custom_id="left")
			rightbutton: discord.ui.Button = discord.utils.get(all_buttons, custom_id="right")

			if self.index == 0:
				leftbutton.disabled = True
			else:
				leftbutton.disabled = False
			
			if self.index + 1 == len(senses):
				rightbutton.disabled = True
			else:
				rightbutton.disabled = False

		def get_embed(self, index: int):
			embed = dictionary_embed(
				word=self.word,
				lexicalCategory=self.lexicalCategory,
				entry=self.entry,
				index=index
			)

			return embed

		@discord.ui.button(label='◄', style=discord.ButtonStyle.secondary, custom_id="left", row=2)
		async def left(self, interaction: discord.Interaction, button: discord.ui.Button):
			await interaction.response.defer()
			# assuming this button is active
			self.index -= 1
			embed = self.get_embed(self.index)
			self.disable_buttons()
			
			await interaction.edit_original_response(embed=embed, view=self)
		
		@discord.ui.button(label='►', style=discord.ButtonStyle.secondary, custom_id="right", row=2)
		async def right(self, interaction: discord.Interaction, button: discord.ui.Button):
			await interaction.response.defer()
			# assuming this button is active
			self.index += 1
			embed = self.get_embed(self.index)
			self.disable_buttons()
			
			await interaction.edit_original_response(embed=embed, view=self)

	@group.command(name="dictionary")
	async def dictionary(self, interaction: discord.Interaction, word: str, ephemeral: bool = True):
		"""
		Searches the Oxford Dictionary for a word."""
		await interaction.response.defer(ephemeral=ephemeral)

		embed = discord.Embed(
			title = f"Oxford Dictionary: {word.lower()}",
			description = "Please wait. This may take a while.",
			color = templates.colours["draw"]
		)

		await interaction.followup.send(embed=embed)

		odl = Oxford_Search_Lemmas(word)

		if odl.lemmas_code == 200:
			lemmas = odl.lemmas
			lemmas_results: list = lemmas.get("results") # list of dicts

			view = self.OdDropdownView(self.OdDropdown, lemmas_results)

			await interaction.edit_original_response(embed=None, view=view)
		else:
			embed = discord.Embed(
				title = f"'{word.lower()}' not found",
				description = "```\n" + f"Error {odl.lemmas_code}: {odl.lemmas['error']}```",
				colour = templates.colours["fail"]
			)
			await interaction.edit_original_response(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Dictionary(bot))