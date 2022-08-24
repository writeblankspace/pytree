import discord
from discord import app_commands
from discord.ext import commands
from f.checks import *
from f.__index__ import *
from db.db import db
from cogs.levelling import Levelling
import time
from db.sql import *
import traceback


class Admin(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
	
	group = app_commands.Group(name="admin", description="restricted commands that can only be used by the bot owner")

	@group.command(name="dump")
	@app_commands.describe(
		content = "the content to dump into the channel",
		attachments = "the attachments to dump into the channel"
		)
	@owner_only()
	async def dump(self, interaction: discord.Interaction, content: str = None, attachments: discord.Attachment = None) -> None:
		"""
		[RESTRICTED] Dumps the given content to the dump channel."""
		await interaction.response.defer(ephemeral=True)
		# ^ gives you 15 minutes extra to respond
		# setting ephemeral here is required to send an ephemeral follow up

		# dump channel here
		channel = self.bot.get_channel(838335898755530762)
		links = []
		attachment = attachments 
		# if I emove this and name attachments just attachment, the bot breaks and doesn't send the attachment
		# I thought the programmers in r/ProgrammerHumor were joking but nooo wth this useless line of code is important?
		if content != None:
			# send dump to channel
			link = await channel.send(content)
			# get the message link
			links.append(link.jump_url)
		if attachment != None:
			# send file to channel
			print(attachment)
			link = await channel.send(file=await attachment.to_file(use_cached=True))
			links.append(link.jump_url)
		
		description = []
		i = 1
		for link in links:
			description.append(f"[Jump to Dump ({i})]({link})")
			i += 1
		description = "\n".join(description)

		embed = discord.Embed(
			title='Successfully dumped!',
			description=description,
			color=theme.colours.green
		)
		# send message, delete after 5 seconds
		await interaction.followup.send(embed=embed)

	@group.command(name="archivemonth")
	@owner_only()
	@app_commands.describe(
		date = "the archive's id in the format YYYY/MM"
	)
	async def archivemonth(self, interaction: discord.Interaction, date: str) -> None:
		"""
		[RESTRICTED] Archives the members' trees to their forest """
		await interaction.response.defer(ephemeral=False)

		# this command archives all the trees and puts it in the members' forests
		# the trees are archived into the archive channel to make the image links permanent

		archivechannel = self.bot.get_channel(1001804054965518436)

		levellingfuncs = Levelling(self.bot)
		find_next_level = levellingfuncs.find_next_level
		findtree = levellingfuncs.findtree

		await archivechannel.send(f"**Archiving trees for {date}**")

		rows: list = await psql.db.fetch(
			"""--sql
			SELECT userid, guildid, forest, xp FROM users
			"""
		)

		for row in rows:
			row = dict(row)
			userid: int = row['userid']
			guildid: int = row['guildid']
			forest: dict = psql.json_to_dict(row['forest'])
			xp: int = row['xp']

			level = find_next_level(xp).currentlevel
			tree = findtree(level)

			# get timestamp now
			timestamp = time.time()
			# round the time
			timestamp = round(timestamp)
			# make it a discord timestamp
			timestamp = f"<t:{timestamp}:R>"

			# get the user's tree
			f = discord.File(f"trees/default/{tree}.png", filename=f"{userid}'s_tree.png")
			message = await archivechannel.send(f"{userid}'s tree\n**{date}** {timestamp}", file=f)

			# get the attachment links
			attachments = message.attachments
			url = attachments[0].url
			
			# update the database
			forest[f"{date}"] = {}
			forest[f"{date}"]["tree"] = url
			forest[f"{date}"]["xp"] = xp
			forest[f"{date}"]["level"] = level

			# add the forest
			# reset the xp and equipped
			connection = await psql.db.acquire()
			async with connection.transaction():
				await psql.db.execute(
					"""--sql
					UPDATE users
					SET forest = $1, xp = 0, equipped = ''
					""",
					psql.dict_to_json(forest)
				)
			await psql.db.release(connection)
		
		embed = discord.Embed(
			title = f"Archived {date} for {len(rows)} members.",
			color = theme.colours.green
		)

		await interaction.followup.send(embed=embed)

	class SQLview(discord.ui.View):
		def __init__(self, user: discord.User, query: str, rows: list, bot: commands.Bot):
			super().__init__()

			self.rows = rows
			self.query = query
			self.user = user
			self.index = 0
			self.current_column = 0
			self.bot = bot
		
		def disable_buttons(self):
			all_buttons = self.children

			leftbutton: discord.ui.Button = discord.utils.get(all_buttons, custom_id="left")
			rightbutton: discord.ui.Button = discord.utils.get(all_buttons, custom_id="right")
			upbutton: discord.ui.Button = discord.utils.get(all_buttons, custom_id="up")
			downbutton: discord.ui.Button = discord.utils.get(all_buttons, custom_id="down")

			if self.index == 0:
				leftbutton.disabled = True
			else:
				leftbutton.disabled = False
			
			if self.index + 1 >= len(self.rows):
				rightbutton.disabled = True
			else:
				rightbutton.disabled = False
			
			if self.current_column == 0:
				upbutton.disabled = True
			else:
				upbutton.disabled = False
			
			if self.current_column + 1 >= len(self.rows[self.index]):
				downbutton.disabled = True
			else:
				downbutton.disabled = False
		
		async def update_rows(self):
			rows: list = await psql.db.fetch(self.query)
			self.rows = rows
		
		def generate_embed(self):
			row = self.rows[self.index] # Record object

			specifics = []
			specifics.append(("userid", row.get('userid')))
			specifics.append(("guildid", row.get('guildid')))

			specifics_str = []

			for specific in specifics:
				if specific[1] is not None:
					if specific[0] == "userid":
						easyname = "*user*"
						user = self.bot.get_user(specific[1])
						easyval = f"'{user.name}#{user.discriminator}'"
					elif specific[0] == "guildid":
						easyname = "*guild*"
						easyval = f"'{self.bot.get_guild(specific[1]).name}'"
					else:
						easyname = specific[0]
						easyval = specific[1]
					
					specifics_str.append(f"{easyname} = {easyval}")

			if specifics_str != []:	
				specifics_str = "`WHERE " + " AND ".join(specifics_str) + "`\n"
			else:
				specifics_str = ""

			embed = discord.Embed(
				title = f"`{self.query.replace(';', '')}`",
				color = theme.colours.primary
			)

			keys = row.keys()

			columns_str = []

			i = 0

			for key in keys:
				# shorten value to 25 characters
				value = row[key]
				if len(str(value)) > 25:
					value = value[:22] + "..."

				if value in [None, ""]:
					gray = ansimd.ansi(color=ansimd.color.gray)
					value = f"{gray}[None: {type(value)}]{ansimd.normal()}"
				
				if i == self.current_column:
					arrowansi = ansimd.ansi(
						format = ansimd.format.bold,
						color = ansimd.color.yellow
					)
					ansi = ansimd.ansi(
						format = ansimd.format.bold,
						color = ansimd.color.cyan
					)
					keystr = f"{arrowansi}> {ansi}{key}"
				else:
					ansi = ansimd.ansi(
						color = ansimd.color.cyan
					)
					keystr = f"  {ansi}{key}"
				
				n = ansimd.normal()

				columns_str.append(f"{keystr}: {n}{value}")

				i += 1
			
			columns_str = "\n".join(columns_str)
			
			if columns_str != []:
				embed.description = f"{specifics_str}```ansi\n{columns_str}```"
			else:
				embed.description = specifics_str
			
			embed.set_footer(
				text = f"record {self.index + 1} of {len(self.rows)}"
			) 
			
			return embed

		class Edit(discord.ui.Modal, title='Edit'):
			def __init__(self, interaction: discord.Interaction, record_key, current_column_name, when_done):
				self.record_key = record_key
				self.current_column_name = current_column_name
				self.interaction = interaction
				self.when_done = when_done

				super().__init__()
			
			tablename = discord.ui.TextInput(
				label="table name",
				placeholder="SELECT * FROM ___"
			)

			value = discord.ui.TextInput(
				label='value'
			)

			async def on_submit(self, interaction: discord.Interaction):
				tablename = self.tablename.value
				value = self.value.value

				connection = await psql.db.acquire()
				async with connection.transaction():
					await psql.db.execute(
						f"""--sql
						UPDATE {tablename}
						SET {self.current_column_name} = {value}
						WHERE {self.record_key[0]} = {self.record_key[1]};
						"""
					)
				await psql.db.release(connection)

				r = await self.when_done()
				await interaction.response.edit_message(embed=r[0], view=r[1])

			async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
				embed = discord.Embed(
					title = "Something went wrong...", 
					description = f"Please ping the developer.",
					colour = theme.colours.red
				)
				await interaction.response.send_message(embed=embed, ephemeral=True)

				# Make sure we know what the error actually is
				traceback.print_tb(error.__traceback__)


		@discord.ui.button(label="edit", style=discord.ButtonStyle.secondary, custom_id="edit", row=0)
		async def edit(self, interaction: discord.Interaction, button: discord.ui.Button):
			row = self.rows[self.index]
			keys = list(row.keys())
			key = keys[self.current_column]

			if "userid" in keys:
				record_key = ("userid", row["userid"])
			elif "guildid" in keys:
				record_key = ("guildid", row["guildid"])
			else:
				record_key = ("id", row["id"])

			async def when_done():
				await self.update_rows()
				embed = self.generate_embed()
				self.disable_buttons()

				return (embed, self)

			modal = self.Edit(interaction, record_key, key, when_done)
			
			modal.title = f"Edit record {key}"
			value = row[key]
			if value not in [None, '']:
				modal.value.default = row[key]
			
			await interaction.response.send_modal(modal)

		# up button
		@discord.ui.button(label="▲", style=discord.ButtonStyle.primary, custom_id="up", row=0)
		async def up(self, interaction: discord.Interaction, button: discord.ui.Button):
			self.current_column -= 1

			embed = self.generate_embed()
			self.disable_buttons()
			
			await interaction.response.edit_message(embed=embed, view=self)

		@discord.ui.button(label='◄', style=discord.ButtonStyle.primary, custom_id="left", row=1)
		async def left(self, interaction: discord.Interaction, button: discord.ui.Button):
			self.index -= 1;
			
			embed = self.generate_embed()
			self.disable_buttons()
			
			await interaction.response.edit_message(embed=embed, view=self)
		
		# down button
		@discord.ui.button(label="▼", style=discord.ButtonStyle.primary, custom_id="down", row=1)
		async def down(self, interaction: discord.Interaction, button: discord.ui.Button):
			self.current_column += 1

			embed = self.generate_embed()
			self.disable_buttons()
			
			await interaction.response.edit_message(embed=embed, view=self)

		@discord.ui.button(label='►', style=discord.ButtonStyle.primary, custom_id="right", row=1)
		async def right(self, interaction: discord.Interaction, button: discord.ui.Button):
			self.index += 1;
			
			embed = self.generate_embed()
			self.disable_buttons()
			
			await interaction.response.edit_message(embed=embed, view=self)

	@group.command(name="sql")
	@owner_only()
	@app_commands.describe(
		query = "the query to run"
	)
	async def sql(self, interaction: discord.Interaction, query: str) -> None:
		"""
		[RESTRICTED] Runs the given query on the database."""
		await interaction.response.defer(ephemeral=True)

		# run the query
		rows: list = await psql.db.fetch(query)

		view = self.SQLview(interaction.user, query, rows, self.bot)
		view.disable_buttons()
		embed = view.generate_embed()

		await interaction.followup.send(embed=embed, view=view)
	
	@sql.autocomplete("query")
	async def sql_autocomplete(self, interaction: discord.Interaction, current: str):
		return [
			app_commands.Choice(
				name=f'SELECT * FROM users ORDER BY userid;', 
				value=f'SELECT * FROM users ORDER BY userid;'
			),
			app_commands.Choice(
				name='SELECT * FROM guilds ORDER BY guildid;', 
				value='SELECT * FROM guilds ORDER BY guildid;'
			)
		]

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Admin(bot))