import discord
from discord import app_commands
from discord.ext import commands
from f.__index__ import *
from db.db import db
from PIL import *
import os
from io import BytesIO
from db.sql import *

class Levelling(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

		self.full_progress = "▰"
		self.empty_progress = "▱"
		self.zwnbs = "﻿" # zero-width no-break space

		# 1 message in 60 seconds
		self.cooldown = commands.CooldownMapping.from_cooldown(1.0, 60.0, commands.BucketType.user)

	def find_next_level(self, xp):
		"""
		Finds the next level and the xp needed for that level using the user's current xp 
		
		`self.currentlevel` is the current level of the user

		`self.xp_needed` is the xp needed for the next level
		
		`self.prev_xp_needed` is the xp needed for the previous level """
		i = 1 # level
		xp_needed = 0 # xp needed to reach next level
		# find next level and xp needed
		xp_needed = (50 * i**2) + (25 * i) # so no weird stuff
		# lvl 1 = 75 xp to level 2
		# lvl 2 = 250 xp to level 3

		while xp > xp_needed:
			# find xp for next level
			xp_needed = (50 * i**2) + (25 * i)
			# iterate
			i += 1
			# when xp is less than xp needed, we have found the next level

		class NextLevel:
			def __init__(self, currentlevel: int, xp_needed: int):
				self.currentlevel = currentlevel
				self.xp_needed = xp_needed
				self.prev_xp_needed = (50 * (currentlevel - 1) **2) - (25 * (currentlevel - 1))
		
		return NextLevel(i - 1, xp_needed)
	
	def xp_for_level(self, level: int):
		"""
		Returns the xp needed to reach the given level """
		return (50 * level**2) + (25 * level)
	
	def findtree(self, level :int):
		"""
		Find out what tree you get for the given level """
		if level < 5:
			tree = "1"
		elif level < 10:
			tree = "2"
		elif level < 15:
			tree = "3"
		elif level < 20:
			tree = "4"
		elif level < 25:
			tree = "5"
		elif level < 30:
			tree = "6"
		elif level >= 30:
			tree = "7"
		
		return tree
	
	@commands.Cog.listener('on_message')
	async def leveling_listener(self, message: discord.Message):
		userid = message.author.id

		if message.author.bot == False and message.author != self.bot.user:
			# cooldowns
			bucket = self.cooldown.get_bucket(message)
			retry_after = bucket.update_rate_limit()
			if retry_after: # rate-limited
				pass
			else: # you can do stuff!
				if message.guild == None:
					# it's useless with ephemeral messages
					# and spams my terminal
					return

				guildid = message.guild.id

				# check stuff first to avoid errors
				await psql.check_user(userid, guildid)

				row = await psql.db.fetchrow(
					"""--sql
					SELECT xp, balance, equipped FROM users
					WHERE userid = $1 AND guildid = $2
					""",
					userid, guildid
				)

				xp = row['xp']
				balance = row['balance']
				equipped = psql.commasplit(row['equipped'])
				

				nextlevel = self.find_next_level(xp)

				xp_needed = nextlevel.xp_needed
				currentlevel = nextlevel.currentlevel

				multi = calc_multi(equipped, xp).xp_multi

				randxp = random.randint(15, 40)
				# 13 easter egg
				if xp % 13 == 0:
					randxp += 13
				# xp gained
				xp += randxp * multi

				if xp > xp_needed:
					currentlevel += 1
					balance += currentlevel * 5
					await message.reply(f"{message.author.mention} has leveled up to level {currentlevel}!")

				connection = await psql.db.acquire()
				async with connection.transaction():
					await psql.db.execute(
						"""--sql
						UPDATE users
						SET xp = xp + $1, balance = balance + $2
						WHERE userid = $3 AND guildid = $4
						""",
						randxp * multi, currentlevel * 5,
						userid, guildid
					)
				await psql.db.release(connection)
	
	group = app_commands.Group(name="lvl", description="Levelling commands: level up as you chat")

	@group.command(name="rank")
	@app_commands.describe(
		member = "the member whose rank you'd like to view",
		ephemeral = "whether or not others should see the bot's reply"
	)
	async def rank(self, interaction: discord.Interaction, member: discord.User = None, ephemeral: bool = True) -> None:
		"""
		Views a user's rank. """
		if member == None:
			member = interaction.user
		else:
			member = member

		if member.bot == False:
			await interaction.response.defer(ephemeral=ephemeral)

			guildid = interaction.guild.id
			userid = member.id

			# avoid errors by checking if it exists
			await psql.check_user(userid, guildid)

			row = await psql.db.fetchrow(
				"""--sql
				SELECT xp FROM users
				WHERE userid = $1 AND guildid = $2
				""",
				userid, guildid
			)

			xp = row['xp']

			# just get some data yeah
			nextlevel = self.find_next_level(xp)
			xp_needed = nextlevel.xp_needed
			prev_xp_needed = nextlevel.prev_xp_needed
			currentxp = xp
			currentlevel = nextlevel.currentlevel

			# calculate the progress, eg 0.713
			if (xp_needed - prev_xp_needed) > 0:
				progress = (currentxp - prev_xp_needed) / (xp_needed - prev_xp_needed)
			else:
				progress = 1
			# make it a percentage, eg 71.3%
			progress *= 100
			progresspercent = progress

			# get a tree thumbnail!
			# find out what tree you get
			tree = self.findtree(currentlevel)
			
			# truncate xp needed to fit in the embed
			currentxp_embed = (currentxp - prev_xp_needed)
			xp_needed_embed = (xp_needed - prev_xp_needed)
			if currentxp_embed >= 10000:
				currentxp_embed = f"{round(currentxp_embed / 1000)}k"
			if xp_needed_embed >= 10000:
				xp_needed_embed = f"{round(xp_needed_embed / 1000)}k"
			
			if currentxp_embed <= 0:
				currentxp_embed = 0
			
			# get the rank
			lb = self.LeaderboardView(self.bot, self.find_next_level, interaction.guild)
			await lb.generate_leaderboard(interaction.guild)
			leaderboard = lb.leaderboard

			# get the author's index in the list of dicts
			"""
			```py
			[
				{
					"member": discord.User,
					"xp": int
					"level": int
				}, {}, {} # etc
			] 
			```"""
			index = leaderboard.index({
				"member": member,
				"xp": currentxp,
				"level": currentlevel
			})
			index += 1


			# python pillow
			rankcardimg = rankcard(
				pfpurl = member.avatar.url,
				username = member.name,
				discrim = member.discriminator,
				other = f"lvl {currentlevel} | {currentxp_embed}/{xp_needed_embed} xp | #{index}",
				treenumber = tree,
				color = (181, 128, 91),
				progress = round(progresspercent)
			)

			# save the image to buffer
			# basically like a 'file' that isn't physically there
			buffer = BytesIO()
			rankcardimg.save(buffer, "png")
			buffer.seek(0)

			rankcardfile = discord.File(fp=buffer, filename="rankcard.png")

			await interaction.followup.send(files=[rankcardfile])

		else:
			await interaction.response.defer(ephemeral=True)

			embed = discord.Embed(
				title = "You can't rank bots!", 
				colour = theme.colours.red
			)
			await interaction.followup.send(embed=embed)
	
	# leaderboard
	class LeaderboardView(discord.ui.View):
		"""
		Buttons for the /leaderboard command """

		def __init__(self, bot: commands.Bot, find_next_level, guild: discord.Guild, users_per_page: int = 5):
			# if you want to see top 1-10, then 1
			# top 11-20, then 11
			# and so on
			self.bot = bot
			self.leaderboard = []
			self.leaderboard_index = 0
			self.find_next_level = find_next_level
			self.guild = guild
			self.max_per_page = users_per_page

			# gonna dump stuff here
			# ◁ ▷

			super().__init__() 
			# apparently I must do this or stuff breaks
		
		def disable_buttons(self):
			max_per_page = self.max_per_page
			# update the buttons
			all_buttons = self.children

			leftbutton = discord.utils.get(all_buttons, custom_id="left")
			rightbutton = discord.utils.get(all_buttons, custom_id="right")

			if self.leaderboard_index - max_per_page < 0:
				leftbutton.disabled = True
			else:
				leftbutton.disabled = False
			
			if self.leaderboard_index + max_per_page >= len(self.leaderboard):
				rightbutton.disabled = True
			else:
				rightbutton.disabled = False
		
		async def on_timeout(self) -> None:
			for item in self.children:
				item.disabled = True

			await self.message.edit(view=self)

		async def generate_leaderboard(self, guild: discord.Guild) -> list:
			"""
			Gives a list of the leaderboard.
			
			`guild` is the server to get the leaderboard for 
			
			Returns a list of dicts, each dict containing the member, xp, and level.

			```py
			[
				{
					"member": discord.User,
					"xp": int
					"level": int
				}, {}, {} # etc
			] 
			```"""

			# get the data
			rows = await psql.db.fetch(
				"""--sql
				SELECT userid, xp FROM users
				WHERE guildid = $1;
				""",
				guild.id
			)

			for row in rows:
				# get the user's level
				userid = row['userid']
				member = guild.get_member(userid)
				if member is not None:
					xp = row["xp"]
					level = self.find_next_level(xp).currentlevel

					# add the user to the leaderboard
					self.leaderboard.append(
						{
							"member": guild.get_member(userid),
							"xp": xp,
							"level": level
						}
					)
			
			# sort the users by most xp to least xp
			# I have no idea how to use lambda, but GitHub copilot said to use it
			# I think this lambda basically returns the xp of the dict, x being the dict
			self.leaderboard.sort(key=lambda x: x["xp"], reverse=True)

			return self.leaderboard

		def get_leaderboard_embed(self, guild: discord.Guild, startindex: int) -> discord.Embed:
			"""
			Returns an embed of the leaderboard.

			`guild` is the server to get the leaderboard for
			
			`startindex` is the index where the leaderboard should start, eg 0 would show top 1; 10 would show top 11 """

			# list slicing to get the users
			leaderboard = self.leaderboard[startindex:startindex + self.max_per_page]

			# I love list slicing but I can never remember how

			# make the description
			description_list = []

			rank = startindex + 1

			for user in leaderboard:
				# get the user's data
				member = user["member"]
				xp = user["xp"]
				level = user["level"]

				# get the tree
				if level < 5:
					tree = "<:tree1:999346190439174174>"
				elif level < 10:
					tree = "<:tree2:999346195833036831>"
				elif level < 15:
					tree = "<:tree3:999346201814114435>"
				elif level < 20:
					tree = "<:tree4:999346213067444315>"
				elif level < 25:
					tree = "<:tree5:999346218683601026>"
				elif level < 30:
					tree = "<:tree6:999346225159606322>"
				elif level >= 30:
					tree = "<:tree7:999346230889033748>"

				# make the description
				description_list.append(
					f"**`#{rank}`** | {member.mention} | lvl {level}"
				)

				rank += 1
			
			description = "\n".join(description_list)


			# make the embed
			embed = discord.Embed(
				title = f"{guild.name}'s leaderboard",
				description = description,
				color = theme.colours.primary
			)

			return embed

		
		# Define the actual button
		@discord.ui.button(
			label='◄',
			style=discord.ButtonStyle.secondary,
			custom_id='left',
			disabled=True
			)
		async def left(self, interaction: discord.Interaction, button: discord.ui.Button):
			# which part of the leaderboard to see
			max_per_page = self.max_per_page
			guild = interaction.guild

			# eg your index is 10 and max_per_page is 10
			# so make index -10 so 0
			self.leaderboard_index -= max_per_page

			# get the leaderboard
			embed = self.get_leaderboard_embed(
				guild = guild,
				startindex = self.leaderboard_index
			)

			# update the buttons
			self.disable_buttons()

			# Make sure to update the message with our updated selves
			await interaction.response.edit_message(embed=embed, view=self)
		
		@discord.ui.button(
			label='top users',
			style=discord.ButtonStyle.secondary,
			custom_id='top',
			disabled=False
			)
		async def top(self, interaction: discord.Interaction, button: discord.ui.Button):
			# which part of the leaderboard to see
			max_per_page = self.max_per_page
			guild = interaction.guild

			# eg your index is 10 and max_per_page is 10
			# so make index -10 so 0
			self.leaderboard_index = 0

			# get the leaderboard
			embed = self.get_leaderboard_embed(
				guild = guild,
				startindex = self.leaderboard_index
			)

			# update the buttons
			self.disable_buttons()

			# Make sure to update the message with our updated selves
			await interaction.response.edit_message(embed=embed, view=self)
		
		# right button now
		@discord.ui.button(
			label='►',
			style=discord.ButtonStyle.secondary,
			custom_id='right',
			disabled=False
			)
		async def right(self, interaction: discord.Interaction, button: discord.ui.Button):
			# which part of the leaderboard to see
			max_per_page = self.max_per_page
			guild = interaction.guild

			# eg your index is 10 and max_per_page is 10
			# so make index +10 so 20
			self.leaderboard_index += max_per_page

			# get the leaderboard
			embed = self.get_leaderboard_embed(
				guild = guild,
				startindex = self.leaderboard_index
			)

			# update the buttons
			self.disable_buttons()


			# Make sure to update the message with our updated selves
			await interaction.response.edit_message(embed=embed, view=self)

	@group.command(name="leaderboard")
	@app_commands.describe(
		ephemeral = "whether or not others should see the bot's reply",
		usersperpage = "the number of users to show per page"
	)
	async def leaderboard(self, interaction: discord.Interaction, ephemeral: bool = True, usersperpage: int = 5) -> None:
		"""
		Views the levelling leaderboard. """
		await interaction.response.defer(ephemeral=ephemeral)

		lb = self.LeaderboardView(self.bot, self.find_next_level, interaction.guild, usersperpage)

		await lb.generate_leaderboard(interaction.guild)

		embed = lb.get_leaderboard_embed(
			guild = interaction.guild,
			startindex = 0
		)

		# disable some buttons
		all_buttons = lb.children

		rightbutton = discord.utils.get(all_buttons, custom_id="right")

		if lb.max_per_page >= len(lb.leaderboard):
			rightbutton.disabled = True

		lb.message = await interaction.followup.send(
			embed = embed,
			view = lb
		)

	# forest
	class ForestDropdown(discord.ui.Select):
		def __init__(self, show_tree, treekeys: list, forest: dict, member: discord.User, ephemeral: bool = True):
			# Set the options that will be presented inside the dropdown
			self.show_tree = show_tree
			self.treekeys = treekeys
			self.forest = forest
			self.member = member
			self.ephemeral = ephemeral

			options = []

			for treekey in treekeys:
				options.append(
					discord.SelectOption(
						label=treekey,
					)
				)

			# dropdown settings
			super().__init__(
				placeholder='Choose a tree to view...', 
				min_values=1, 
				max_values=1, 
				options=options
			)

		async def callback(self, interaction: discord.Interaction):
			# self.values is a list of the selected options
			# get the selected tree
			treekey = self.values[0]
			embed = self.show_tree(treekey)
			await interaction.response.edit_message(
				embed = embed
			)
	
	class ForestDropdownView(discord.ui.View):
		def __init__(self, ForestDropdown, show_tree, treekeys: list, forest: dict, member: discord.User, ephemeral: bool = True):
			super().__init__()

			# Adds the dropdown to our view object.
			self.add_item(
				ForestDropdown(
					show_tree = show_tree,
					treekeys = treekeys,
					forest = forest,
					member = member,
					ephemeral = ephemeral
				)
			)
		
		async def on_timeout(self) -> None:
			for item in self.children:
				item.disabled = True

			await self.message.edit(view=self)

	@group.command(name="forest")
	@app_commands.describe(
		ephemeral = "whether or not others should see the bot's reply",
		member = "the member to view the forest of"
	)
	async def forest(self, interaction: discord.Interaction, ephemeral: bool = True, member: discord.User = None) -> None:
		"""
		Views a user's forest. """

		if member == None:
			member = interaction.user
		else:
			member = member

		if member.bot == False:
			await interaction.response.defer(ephemeral=ephemeral)

			guildid = interaction.guild.id
			userid = member.id

			# check if it exists to get rid of errors
			await psql.check_user(userid, guildid)

			row = await psql.db.fetchrow(
				"""--sql
				SELECT forest FROM users
				WHERE userid = $1 AND guildid = $2
				""",
				userid, guildid
			)

			forest = row['forest'] # this is in json
			forest: dict = psql.json_to_dict(forest)

			""" 
			forest = {
				f"{date}": {
					"tree": url
					"xp": xp
					"level": level
				}
			} """

			# sort the forest dict alphabetically by the date
			# find keys of forest
			keys = list(forest.keys())
			# sort the keys
			keys.sort()

			if len(keys) == 0:
				embed = discord.Embed(
					title = f"There aren't any trees in {member.name}'s forest yet!", 
					colour = theme.colours.red
				)
				await interaction.followup.send(embed=embed)
				return

			def show_tree(date: int) -> discord.Embed:
				currenttree = forest[date]
				tree = currenttree["tree"]
				xp = currenttree["xp"]
				level = currenttree["level"]

				embed = discord.Embed(
					title = f"{member.name}'s tree for {date}",
					description = f"level {level} | {xp} xp",
					color = theme.colours.primary
				)

				embed.set_image(url=tree)

				return embed
			
			if len(keys) == 1:
				description = "There is 1 tree in this forest."
			else:
				description = f"There are {len(keys)} trees in this forest."
			
			embed = discord.Embed(
				title = f"{member.name}'s forest",
				description = description,
				colour = theme.colours.primary
			)
			view = self.ForestDropdownView(
				ForestDropdown = self.ForestDropdown,
				show_tree = show_tree,
				treekeys = keys,
				forest = forest,
				member = member,
				ephemeral = ephemeral
			)

			view.message = await interaction.followup.send(embed=embed, view=view)
		else:
			# imagine viewing a bot's forest
			await interaction.response.defer(ephemeral=True)

			embed = discord.Embed(
				title = "Bots don't have forests!", 
				colour = theme.colours.red
			)
			await interaction.followup.send(embed=embed)



async def setup(bot: commands.Bot):
	await bot.add_cog(Levelling(bot))