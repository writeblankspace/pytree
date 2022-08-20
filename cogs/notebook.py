import discord
from discord import app_commands
from discord.ext import commands
from db.db import db
from f.__index__ import *
import traceback
from db.sql import *

class Notebook(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
	
	group = app_commands.Group(name="nb", description="Notebook commands: view and edit your personal notes.")

	class EditModal(discord.ui.Modal, title="Edit page"):
		def __init__(self, interaction: discord.Interaction, index: int, embed: discord.Embed):
			self.title = f"Edit page {index + 1}"

			self.index = index
			self.interaction = interaction
			self.embed = embed

			super().__init__(title=self.title)


		notes = discord.ui.TextInput(
			label="Notes",
			style=discord.TextStyle.long,
			placeholder="Type anything here...",
			required=False,
			max_length=2000,
		)

		async def on_submit(self, interaction: discord.Interaction):
			guildid = interaction.guild.id
			userid = interaction.user.id

			row = await psql.db.fetchrow(
				"""--sql
				SELECT notebook FROM users
				WHERE userid = $1 AND guildid = $2;
				""",
				userid, guildid
			)

			notebook = psql.json_to_dict(row["notebook"])

			notebook["data"][self.index] = self.notes.value

			connection = await psql.db.acquire()
			async with connection.transaction():
				await psql.db.execute(
					"""--sql
					UPDATE users
					SET notebook = $1
					WHERE guildid = $2 AND userid = $3
					""",
					psql.dict_to_json(notebook), guildid, userid
				)
			await psql.db.release(connection)

			self.embed.__setattr__("description", self.notes.value)

			await interaction.response.edit_message(embed=self.embed)

		async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
			embed = discord.Embed(
				title = "Something went wrong...", 
				description = f"Please ping the developer.",
				colour = theme.colours.red
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

		async def on_timeout(self) -> None:
			for item in self.children:
				item.disabled = True

			await self.message.edit(view=self)
		
		async def notebook(self) -> list:
			row = await psql.db.fetchrow(
				"""--sql
				SELECT notebook FROM users
				WHERE guildid = $1 AND userid = $2
				""",
				self.guild.id, self.user.id
			)

			notebook = psql.json_to_dict(row["notebook"])["data"]

			return notebook

		async def disable_buttons(self):
			notebook: list = await self.notebook()

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

		async def get_embed(self, index: int):
			notebook: list = await self.notebook()

			embed = discord.Embed(
				title = f"{self.user.name}'s notebook",
				description = notebook[index],
				color = theme.colours.primary
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
					color = theme.colours.red
				)
				await interaction.response.send_message(embed=embed, ephemeral=True)
			else:
				# assuming this button is active
				self.index -= 1
				embed = await self.get_embed(self.index)
				await self.disable_buttons()
				await interaction.response.edit_message(embed=embed, view=self)
		
		@discord.ui.button(label="edit page", style=discord.ButtonStyle.primary, custom_id="edit")
		async def edit(self, interaction: discord.Interaction, button: discord.ui.Button):
			if interaction.user == self.user:

				row = await psql.db.fetchrow(
					"""--sql
					SELECT notebook FROM users
					WHERE guildid = $1 AND userid = $2
					""",
					self.guild.id, self.user.id
				)

				notebook: list = psql.json_to_dict(row["notebook"])["data"]

				modal = self.modal(
					interaction = interaction,
					index = self.index,
					embed = await self.get_embed(self.index)
				)

				modal.notes.default = notebook[self.index]

				await interaction.response.send_modal(modal)
			else:
				embed = discord.Embed(
					title = "Only the owner of the notebook can do this.",
					color = theme.colours.red
				)
				await interaction.response.send_message(embed=embed, ephemeral=True)
		
		@discord.ui.button(label="add page", style=discord.ButtonStyle.green, custom_id="new")
		async def new(self, interaction: discord.Interaction, button: discord.ui.Button):
			if interaction.user != self.user:
				embed = discord.Embed(
					title = "Only the owner of the notebook can do this.",
					color = theme.colours.red
				)
				await interaction.response.send_message(embed=embed, ephemeral=True)
			else:
				# add a new page after the current page
				row = await psql.db.fetchrow(
					"""--sql
					SELECT notebook FROM users
					WHERE guildid = $1 AND userid = $2
					""",
					self.guild.id, self.user.id
				)

				notebook: dict = psql.json_to_dict(row["notebook"])

				notebook["data"].insert(self.index + 1, "")

				notebook = psql.dict_to_json(notebook)

				connection = await psql.db.acquire()
				async with connection.transaction():
					await psql.db.execute(
						"""--sql
						UPDATE users
						SET notebook = $1
						WHERE guildid = $2 AND userid = $3
						""",
						notebook, self.guild.id, self.user.id
					)
				await psql.db.release(connection)

				self.index += 1
				embed = await self.get_embed(self.index)
				await self.disable_buttons()

				await interaction.response.edit_message(embed=embed, view=self)


		@discord.ui.button(label="delete page", style=discord.ButtonStyle.red, custom_id="delete")
		async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
			if interaction.user != self.user:
				embed = discord.Embed(
					title = "Only the owner of the notebook can do this.",
					color = theme.colours.red
				)
				await interaction.response.send_message(embed=embed, ephemeral=True)
			else:
				if len(await self.notebook()) == 1:
					embed = discord.Embed(
						title = "Your notebook must have at least one page.",
						color = theme.colours.red
					)
					await interaction.response.send_message(embed=embed, ephemeral=True)
				else:
					row = await psql.db.fetchrow(
						"""--sql
						SELECT notebook FROM users
						WHERE guildid = $1 AND userid = $2
						""",
						self.guild.id, self.user.id
					)

					notebook: dict = psql.json_to_dict(row["notebook"])

					notebook["data"].pop(self.index)

					notebook = psql.dict_to_json(notebook)

					connection = await psql.db.acquire()
					async with connection.transaction():
						await psql.db.execute(
							"""--sql
							UPDATE users
							SET notebook = $1
							WHERE guildid = $2 AND userid = $3
							""",
							notebook, self.guild.id, self.user.id
						)
					await psql.db.release(connection)

					if self.index != 0:
						self.index -= 1

					embed = await self.get_embed(self.index)
					await self.disable_buttons()

					await interaction.response.edit_message(embed=embed, view=self)

		@discord.ui.button(label="►", style=discord.ButtonStyle.secondary, custom_id="right")
		async def right(self, interaction: discord.Interaction, button: discord.ui.Button):
			if interaction.user != self.user:
				embed = discord.Embed(
					title = "Only the owner of the notebook can do this.",
					color = theme.colours.red
				)
				await interaction.response.send_message(embed=embed, ephemeral=True)
			else:
				# assuming this button is active
				self.index += 1
				embed = await self.get_embed(self.index)
				await self.disable_buttons()
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
		guildid = interaction.guild.id
		userid = user.id

		await psql.check_user(userid, guildid)

		row = await psql.db.fetchrow(
			"""--sql
			SELECT notebook FROM users
			WHERE guildid = $1 AND userid = $2
			""",
			guildid, userid
		)

		notebookdict: dict = psql.json_to_dict(row["notebook"])

		notebook: list = notebookdict["data"] # returns a list

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
			color = theme.colours.primary
		)
		embed.set_footer(
			text = f"page {currentpage + 1} of {len(notebook)}"
		)

		view = self.NBNav(interaction, currentpage, self.EditModal)

		await view.disable_buttons()

		view.message = await interaction.followup.send(embed=embed, view=view)

	class QuicknoteModal(discord.ui.Modal, title="Quick note"):
		def __init__(self, interaction: discord.Interaction):
			self.index = 0
			self.interaction = interaction

			super().__init__()


		notes = discord.ui.TextInput(
			label="Notes",
			style=discord.TextStyle.short,
			placeholder="Type anything here...",
			required=False,
			max_length=100,
		)

		async def on_submit(self, interaction: discord.Interaction):
			row = await psql.db.fetchrow(
				"""--sql
				SELECT notebook FROM users
				WHERE guildid = $1 AND userid = $2
				""",
				interaction.guild.id, interaction.user.id
			)

			notebook: dict = psql.json_to_dict(row["notebook"])

			result = notebook["data"][self.index] + "\n" + self.notes.value

			if len(result) > 2000:
				embed = discord.Embed(
					title = "Your note is too long",
					description = "```\n" + f"{self.notes.value}```",
					color = theme.colours.red
				)
				await interaction.response.send_message(embed=embed, ephemeral=True)
			else:
				notebook["data"][self.index] = result

				notebook = psql.dict_to_json(notebook)

				connection = await psql.db.acquire()
				async with connection.transaction():
					await psql.db.execute(
						"""--sql
						UPDATE users
						SET notebook = $1
						WHERE guildid = $2 AND userid = $3
						""",
						notebook, interaction.guild.id, interaction.user.id
					)
				await psql.db.release(connection)

				embed = discord.Embed(
					title = "Quick note saved!",
					description = "```\n" + f"{self.notes.value}```",
					color = theme.colours.green
				)

				await interaction.response.send_message(embed=embed, ephemeral=True)

		async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
			embed = discord.Embed(
				title = "Something went wrong...", 
				description = f"Please ping the developer.",
				colour = theme.colours.red
			)
			await interaction.response.send_message(embed=embed, ephemeral=True)

			# Make sure we know what the error actually is
			traceback.print_tb(error.__traceback__)

	@group.command(name="quick")
	async def quick(self, interaction: discord.Interaction):
		"""
		Creates a quick note on the first page of your notebook. """
		user = interaction.user
		guildid = interaction.guild.id
		userid = user.id

		await psql.check_user(userid, guildid)

		row = await psql.db.fetchrow(
			"""--sql
			SELECT notebook FROM users
			WHERE guildid = $1 AND userid = $2
			""",
			guildid, userid
		)

		notebookdict: dict = psql.json_to_dict(row["notebook"])
		notebook: list = notebookdict["data"] # returns a list

		modal = self.QuicknoteModal(interaction)
		modal.content = notebook[0]

		await interaction.response.send_modal(self.QuicknoteModal(interaction))

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Notebook(bot))