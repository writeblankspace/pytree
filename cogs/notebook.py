import discord
from discord import app_commands
from discord.ext import commands
from db.db import db
from f.__index__ import *
import traceback

class Notebook(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
		self.intropage = "\n".join([
			"Welcome to your new notebook! You can use this to keep track of your personal notes.\n",
			"`/notebook open` lets you open your notebook. You can edit your notes by clicking on the buttons below. You can also delete pages and add new ones.\n",
			"`/notebook note` is for quick note-taking. All quick notes go into the first page of your notebook.\n",
			"**Quick notes:**",
			"- try it out by typing `/notebook note`"
		])
	
	group = app_commands.Group(name="notebook", description="Notebook commands: view and edit your personal notes.")

	class EditModal(discord.ui.Modal, title="Edit page"):
		def __init__(self, interaction: discord.Interaction, index: int, embed: discord.Embed):
			self.title = f"Edit page {index + 1}"

			self.index = index
			self.interaction = interaction
			self.embed = embed
		
			data = db.read()
			guildid = str(interaction.guild.id)
			userid = str(interaction.user.id)
			content = data[guildid][userid]["notebook"][index]

			super().__init__(title=self.title)
			self.notes.default = content


		notes = discord.ui.TextInput(
			label="Notes",
			style=discord.TextStyle.long,
			placeholder="Type anything here...",
			required=False,
			max_length=2000,
		)

		async def on_submit(self, interaction: discord.Interaction):
			data = db.read()
			guildid = str(interaction.guild.id)
			userid = str(interaction.user.id)
			data[guildid][userid]["notebook"][self.index] = self.notes.value

			db.write(data)

			self.embed.__setattr__("description", self.notes.value)

			await interaction.response.edit_message(embed=self.embed)

		async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
			embed = discord.Embed(
				title = "Something went wrong...", 
				description = f"Please ping the developer.",
				colour = templates.colours["fail"]
			)
			await interaction.response.send_message(embed=embed, ephemeral=True)

			# Make sure we know what the error actually is
			traceback.print_tb(error.__traceback__)

	class NBNav(discord.ui.View):
		def __init__(self, interaction: discord.Interaction, index: int, modal):
			self.interaction = interaction
			self.user = interaction.user
			self.guild = interaction.guild
			self.index = index
			self.modal = modal
		
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
		
		@discord.ui.button(label="edit page", style=discord.ButtonStyle.primary, custom_id="edit")
		async def edit(self, interaction: discord.Interaction, button: discord.ui.Button):
			if interaction.user == self.user:
				await interaction.response.send_modal(self.modal(
					interaction = interaction,
					index = self.index,
					embed = self.get_embed(self.index)
				))
			else:
				embed = discord.Embed(
					title = "Only the owner of the notebook can do this.",
					color = templates.colours["fail"]
				)
				await interaction.response.send_message(embed=embed, ephemeral=True)
		
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
		
		@discord.ui.button(label="add a new page", style=discord.ButtonStyle.green, custom_id="new", row=2)
		async def new(self, interaction: discord.Interaction, button: discord.ui.Button):
			if interaction.user != self.user:
				embed = discord.Embed(
					title = "Only the owner of the notebook can do this.",
					color = templates.colours["fail"]
				)
				await interaction.response.send_message(embed=embed, ephemeral=True)
			else:
				# add a new page after the current page
				data = db.read()
				guildid = str(self.guild.id)
				userid = str(self.user.id)

				data[guildid][userid]["notebook"].insert(self.index + 1, "")
				db.write(data)

				self.index += 1
				embed = self.get_embed(self.index)
				self.disable_buttons()

				await interaction.response.edit_message(embed=embed, view=self)


		@discord.ui.button(label="delete page", style=discord.ButtonStyle.red, custom_id="delete", row=2)
		async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
			if interaction.user != self.user:
				embed = discord.Embed(
					title = "Only the owner of the notebook can do this.",
					color = templates.colours["fail"]
				)
				await interaction.response.send_message(embed=embed, ephemeral=True)
			else:
				if len(self.notebook()) == 1:
					embed = discord.Embed(
						title = "Your notebook must have at least one page.",
						color = templates.colours["fail"]
					)
					await interaction.response.send_message(embed=embed, ephemeral=True)
				else:
					data = db.read()
					guildid = str(self.guild.id)
					userid = str(self.user.id)

					data[guildid][userid]["notebook"].pop(self.index)

					db.write(data)

					if self.index != 0:
						self.index -= 1

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

		db.exists([guildid, userid, "notebook"], True, [self.intropage])
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

		view = self.NBNav(interaction, currentpage, self.EditModal)

		await interaction.followup.send(embed=embed, view=view)

	class QuicknoteModal(discord.ui.Modal, title="Quick note"):
		def __init__(self, interaction: discord.Interaction):
			self.index = 0
			self.interaction = interaction
		
			data = db.read()
			guildid = str(interaction.guild.id)
			userid = str(interaction.user.id)
			self.content = data[guildid][userid]["notebook"][0]

			super().__init__()


		notes = discord.ui.TextInput(
			label="Notes",
			style=discord.TextStyle.short,
			placeholder="Type anything here...",
			required=False,
			max_length=100,
		)

		async def on_submit(self, interaction: discord.Interaction):
			data = db.read()
			guildid = str(interaction.guild.id)
			userid = str(interaction.user.id)

			result = data[guildid][userid]["notebook"][self.index] + "\n" + self.notes.value

			if len(result) > 2000:
				embed = discord.Embed(
					title = "Your note is too long",
					description = "```\n" + f"{self.notes.value}```",
					color = templates.colours["fail"]
				)
				await interaction.response.send_message(embed=embed, ephemeral=True)
			else:
				data[guildid][userid]["notebook"][self.index] = result

				db.write(data)

				embed = discord.Embed(
					title = "Quick note saved!",
					description = "```\n" + f"{self.notes.value}```",
					color = templates.colours["success"]
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

	@group.command(name="quick")
	async def quick(self, interaction: discord.Interaction):
		"""
		Creates a quick note on the first page of your notebook. """
		user = interaction.user
		guildid = str(interaction.guild.id)
		userid = str(user.id)

		db.exists([guildid, userid, "notebook"], True, [self.intropage])

		await interaction.response.send_modal(self.QuicknoteModal(interaction))

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Notebook(bot))