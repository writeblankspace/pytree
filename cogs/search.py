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

class Search(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
	
	group = app_commands.Group(name="search", description="Search commands: search the web from the bot")

	class OdDropdown(discord.ui.Select):
		def __init__(self, dictionary: dict):
			self.dictionary = dictionary

			options = []

			meanings: list = dictionary["meanings"] # list of dicts
			word: str = dictionary["word"]

			i = 1
			for meaning in meanings:
				part_of_speech = meaning["partOfSpeech"]
				definitions = meaning["definitions"]
				definition = definitions[0]["definition"]

				count = len(definitions)
				if count > 1:
					count = f"({count} results) "
				else:
					count = f"({count} result) "

				description = f"{count}{definition}"
				# make the definition < 100 characters
				if len(description) > 100:
					# get first 97 characters
					description = definition[:97] + "..."
				
				options.append(
					discord.SelectOption(
						label = f"[{i}] [{part_of_speech.lower()}] {word}",
						description=description
					)
				)
				i += 1

			super().__init__(placeholder='Select a definition...', min_values=1, max_values=1, options=options)

		async def callback(self, interaction: discord.Interaction):
			await interaction.response.defer()
			choice: str = self.values[0]

			# [1] [part_of_speech] word
			# get the index
			meaning_index = int(choice.split("]")[0].split("[")[1]) - 1
			# get the part of speech 
			part_of_speech = choice.split("]")[1].split("[")[1]
			# get what's after the brackets
			word: str = choice.split('] ')[2]

			# get the embed
			embed = dictionary_embed(
				dictionary = self.dictionary,
				meaning_index = meaning_index,
				definition_index = 0
			)
			
			all_buttons = self.view.children
			# get button
			left = discord.utils.get(all_buttons, custom_id="left")
			right = discord.utils.get(all_buttons, custom_id="right")
			if left == None and right == None:
				self.view.add_item(self.view.left)
				self.view.add_item(self.view.right)
			
			self.view.meaning_index = meaning_index
			# get the meaning
			meanings: list = self.dictionary["meanings"]
			
			# find the meaning where the part of speech is the same as the one we are looking for
			meaning: dict = meanings[meaning_index]

			self.view.senses = meaning["definitions"]
			self.view.index = 0

			self.view.disable_buttons()
			
			await interaction.edit_original_response(embed=embed, view=self.view)

	class OdDropdownView(discord.ui.View):
		def __init__(self, OdDropdown, dictionary: dict):
			super().__init__()

			# Adds the dropdown to our view object.
			self.add_item(OdDropdown(dictionary))

			# the entire result
			self.dictionary: dict = dictionary
			# part of speech
			self.meaning_index: int = None
			# the different definitions in one part of speech
			self.senses: list = None
			# the index of the current sense
			self.index: int = None

			self.remove_item(self.left)
			self.remove_item(self.right)

		def disable_buttons(self):
			senses: list = self.senses

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
				dictionary = self.dictionary,
				meaning_index = self.meaning_index,
				definition_index = index,
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
	@app_commands.describe(
		word = "the word to look up",
		ephemeral = "whether or not others should see the bot's reply"
	)
	async def dictionary(self, interaction: discord.Interaction, word: str, ephemeral: bool = True):
		"""
		Searches the dictionary for a word."""
		await interaction.response.defer(ephemeral=ephemeral)

		embed = discord.Embed(
			title = f"{theme.loader} Dictionary: {word.lower()}",
			description = f"Please wait. This may take a while.",
			color = theme.colours.secondary
		)

		await interaction.followup.send(embed=embed)

		results: tuple = search_dictionary(word)

		# get first item in the result tuple
		dictionary: dict = results[0]
		code: int = results[1]

		if code == 200:
			view = self.OdDropdownView(self.OdDropdown, dictionary)

			await interaction.edit_original_response(embed=None, view=view)
		else:
			embed = discord.Embed(
				title = dictionary["title"],
				description = f"{dictionary['message']}\n{dictionary['resolution']}",
				colour = theme.colours.red
			)
			await interaction.edit_original_response(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Search(bot))