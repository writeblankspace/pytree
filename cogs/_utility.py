from turtle import color
import discord
from discord import app_commands
from discord.ext import commands
from pyparsing import col
from f.__index__ import *
from f.githubissues import make_github_issue
import traceback
import asyncio

class utility(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
		self.ctx_menu = app_commands.ContextMenu(
			name='Vote delete',
			callback=self.votedelete,
		)
		self.bot.tree.add_command(self.ctx_menu)
	
	async def cog_unload(self) -> None:
		self.bot.tree.remove_command(self.ctx_menu.name, type=self.ctx_menu.type)

	group = app_commands.Group(name="utility", description="Miscellaneous commands: various useful commands that don't fit anywhere else")

	@group.command(name='ping')
	async def ping(self, interaction: discord.Interaction):
		"""
		Displays the bot's latency. This is the time it takes for the bot to respond to a message. """
		await interaction.response.defer(ephemeral=True)

		latency = round(self.bot.latency * 1000, 2)

		if latency > 500:
			colour = theme.colours.red
		elif latency > 100:
			colour = theme.colours.secondary
		else:
			colour = theme.colours.green

		embed = discord.Embed(
			title="🏓 Pong!",
			description=f'**`{latency}` ms**',
			color=colour
		)

		await interaction.followup.send(embed=embed)
	
	@group.command(name="screenshot")
	@app_commands.describe(
		url="the url of the website you want to screenshot. Must start with 'http://' or 'https://'"
	)
	async def screenshot(self, interaction: discord.Interaction, url: str):
		"""
		Creates a screenshot of the given url. """
		await interaction.response.defer(ephemeral=True)
		screenshot = f"https://image.thum.io/get/width/1200/noanimate/{url}"
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
				colour = theme.colours.green
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
		
	@app_commands.command(name="issue")
	async def issue(self, interaction: discord.Interaction):
		"""
		Creates an issue on GitHub. You can add suggestions and bug reports."""
		await interaction.response.send_modal(self.Issue())

	class VoteDeleteView(discord.ui.View):
		def __init__(self, embed: discord.Embed):
			self.upvotes = 0
			self.downvotes = 0
			self.embed = embed

			self.upvoters = []
			self.downvoters = []

			super().__init__()

		@discord.ui.button(label='delete [0]', style=discord.ButtonStyle.red)
		async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
			title = self.embed.title
			total_votes = self.upvotes - self.downvotes

			if interaction.user.id in self.upvoters:
				# undo the vote
				self.upvotes -= 1
				self.upvoters.remove(interaction.user.id)
			elif interaction.user.id in self.downvoters:
				# undo the vote
				self.downvotes -= 1
				self.downvoters.remove(interaction.user.id)
				# then add the vote
				self.upvotes += 1
				self.upvoters.append(interaction.user.id)
			else:
				# not in either list
				self.upvotes += 1
				self.upvoters.append(interaction.user.id)
			
			new_total_votes = self.upvotes - self.downvotes

			title = title.replace(f"[{total_votes}]", f"[{new_total_votes}]")

			self.delete.label = f'delete [{self.upvotes}]'
			self.keep.label = f'keep [{self.downvotes}]'

			self.embed.__setattr__("title", title)
			await interaction.response.edit_message(embed=self.embed, view=self)
		
		@discord.ui.button(label='keep [0]', style=discord.ButtonStyle.green)
		async def keep(self, interaction: discord.Interaction, button: discord.ui.Button):
			title = self.embed.title
			total_votes = self.upvotes - self.downvotes

			if interaction.user.id in self.downvoters:
				# undo the vote
				self.downvotes -= 1
				self.downvoters.remove(interaction.user.id)
			elif interaction.user.id in self.upvoters:
				# undo the vote
				self.upvotes -= 1
				self.upvoters.remove(interaction.user.id)
				# then add the vote
				self.downvotes += 1
				self.downvoters.append(interaction.user.id)
			else:
				# not in either list
				self.downvotes += 1
				self.downvoters.append(interaction.user.id)
			
			new_total_votes = self.upvotes - self.downvotes

			title = title.replace(f"[{total_votes}]", f"[{new_total_votes}]")

			self.delete.label = f'delete [{self.upvotes}]'
			self.keep.label = f'keep [{self.downvotes}]'

			self.embed.__setattr__("title", title)
			await interaction.response.edit_message(embed=self.embed, view=self)

	async def votedelete(self, interaction: discord.Interaction, message: discord.Message):
		"""
		Vote-deletes a message."""
		await interaction.response.defer(ephemeral=True)
		embed = discord.Embed(
			title = f"{theme.loader} Vote-delete [0]",
			description = "Vote on whether or not to delete this message.\nA total of 3 votes is required to delete the message within 10 seconds.",
			colour = theme.colours.red
		)
		embed.set_footer(
			text = f"invoked by {interaction.user.name}"
		)

		view = self.VoteDeleteView(embed)

		confirmation = discord.Embed(
			title = f"Started vote-delete!",
			colour = theme.colours.green
		)

		await interaction.followup.send(embed=confirmation)

		mymessage = await message.reply(embed=embed, view=view)

		await asyncio.sleep(10)

		view.delete.disabled = True
		view.keep.disabled = True

		if view.upvotes - view.downvotes >= 3:
			view.embed.__setattr__("description", "Message was deleted.")
			await mymessage.edit(embed=view.embed, view=view)
			await message.delete()
		else:
			view.embed.__setattr__("description", "Message was not deleted.")
			embed.__setattr__("colour", theme.colours.secondary)
			await mymessage.edit(embed=view.embed, view=view)
		await asyncio.sleep(3)
		await mymessage.delete()


async def setup(bot: commands.Bot):
	await bot.add_cog(utility(bot))