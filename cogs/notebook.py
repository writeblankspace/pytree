import discord
from discord import app_commands
from discord.ext import commands
from db.db import db
from f.__index__ import *

class Notebook(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
	
	group = app_commands.Group(name="notebook", description="Notebook commands: view and edit your personal notes.", guild_ids=[802774740825276426])


	class NBNav(discord.ui.View):
		def __init__(self, interaction: discord.Interaction, index: int):
			self.interaction = interaction
			self.user = interaction.user
			self.guild = interaction.guild
			self.index = index
		
			super().__init__()

			self.disable_buttons() # disable the buttons if necessary
		
		def notebook(self) -> list:
			guildid = str(self.guild.id)
			userid = str(self.user.id)
			db.exists([guildid, userid, "notebook"], True, [])
			data = db.read()

			notebook: list = data[guildid][userid]["notebook"]

			return notebook

		def disable_buttons(self):
			notebook: list = self.notebook()

			all_buttons = self.children

			leftbutton: discord.ui.Button = discord.utils.get(all_buttons, custom_id="left")
			rightbutton: discord.ui.Button = discord.utils.get(all_buttons, custom_id="right")

			if self.index == 0:
				leftbutton.disabled = True
			else:
				leftbutton.disabled = False
			
			if self.index + 1 == len(notebook):
				rightbutton.disabled = True
			else:
				rightbutton.disabled = False

		def get_embed(self, index: int):
			notebook: list = self.notebook()

			embed = discord.Embed(
				title = f"{self.user.name}'s notebook",
				description = notebook[index],
			)
			embed.set_footer(
				text = f"page {index + 1} of {len(notebook)}"
			)

			return embed

		@discord.ui.button(label='◄', style=discord.ButtonStyle.secondary, custom_id="left")
		async def left(self, interaction: discord.Interaction, button: discord.ui.Button):
			if interaction.user != self.user:
				embed = discord.Embed(
					title = "Only the owner of the notebook can do this.",
					color = templates.colours["fail"]
				)
				await interaction.response.send_message(embed=embed, ephemeral=True)
			else:
				# assuming this button is active
				self.index -= 1
				embed = self.get_embed(self.index)
				self.disable_buttons()
				await interaction.response.edit_message(embed=embed, view=self)
		
		@discord.ui.button(label="►", style=discord.ButtonStyle.secondary, custom_id="right")
		async def right(self, interaction: discord.Interaction, button: discord.ui.Button):
			if interaction.user != self.user:
				embed = discord.Embed(
					title = "Only the owner of the notebook can do this.",
					color = templates.colours["fail"]
				)
				await interaction.response.send_message(embed=embed, ephemeral=True)
			else:
				# assuming this button is active
				self.index += 1
				embed = self.get_embed(self.index)
				self.disable_buttons()
				await interaction.response.edit_message(embed=embed, view=self)
			
	@group.command(name="open")
	@app_commands.describe(
		index = "the index of the page you want to open",
		ephemeral = "whether or not others should see the bot's reply"
	)
	async def open(self, interaction: discord.Interaction, index: int = 1, ephemeral: bool = True):
		"""
		Opens your notebook to view and edit it."""
		await interaction.response.defer(ephemeral=ephemeral)
		user = interaction.user
		guildid = str(interaction.guild.id)
		userid = str(user.id)

		intropage = "\n".join([
			"Welcome to your new notebook! You can use this to keep track of your personal notes.\n",
			"`/notebook open` lets you open your notebook. You can edit your notes by clicking on the buttons below. You can also delete pages and add new ones.\n",
			"`/notebook note` is for quick note-taking. All quick notes go into the first page of your notebook.\n",
			"**Quick notes:**",
			"- try it out by typing `/notebook note`"
		])

		db.exists([guildid, userid, "notebook"], True, [intropage])
		data = db.read()

		notebook: list = data[guildid][userid]["notebook"] # returns a list

		currentpage = index - 1
		# currentpage is the page we're currently on
		# 0 = page 1
		# 1 = page 2 etc

		if currentpage > len(notebook) - 1:
			currentpage = len(notebook) - 1

		# each item in this list is a page
		embed = discord.Embed(
			title = f"{user.name}'s notebook",
			description = notebook[currentpage],
		)
		embed.set_footer(
			text = f"page {currentpage + 1} of {len(notebook)}"
		)

		view = self.NBNav(interaction, currentpage)

		await interaction.followup.send(embed=embed, view=view)


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Notebook(bot))