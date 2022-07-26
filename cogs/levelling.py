import discord
from discord import app_commands
from discord.ext import commands
from f.__index__ import *
from db.db import db
from PIL import *
import os
from io import BytesIO

class Levelling(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.full_progress = "▰"
		self.empty_progress = "▱"
		self.zwnbs = "﻿" # zero-width no-break space

		# 1 message in 60 seconds
		self.cooldown = commands.CooldownMapping.from_cooldown(1.0, 20.0, commands.BucketType.user)

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
	
	@commands.Cog.listener('on_message')
	async def leveling_listener(self, message: discord.Message):
		author = str(message.author.id)

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

				guild = str(message.guild.id)

				# check stuff first to avoid errors
				db.exists([guild, author, "xp"], True, 0)
				data = db.read()
				

				nextlevel = self.find_next_level(data[guild][author]["xp"])

				xp_needed = nextlevel.xp_needed
				currentlevel = nextlevel.currentlevel

				randxp = random.randint(15, 40)
				data[guild][author]["xp"] += randxp

				if data[guild][author]["xp"] >= xp_needed:
					currentlevel += 1
					await message.reply(f"{message.author.mention} has leveled up to level {currentlevel}!")

				db.write(data)
	
	group = app_commands.Group(name="levels", description="Levelling commands")

	@group.command(name="rank")
	@app_commands.describe(
		member = "the member whose rank you'd like to view",
		ephemeral = "whether or not others should see the bot's reply"
	)
	async def rank(self, interaction: discord.Interaction, member: discord.User = None, ephemeral: bool = True) -> None:
		"""
		View your rank in the server. """
		if member == None:
			member = interaction.user
		else:
			member = member

		if member.bot == False:
			await interaction.response.defer(ephemeral=ephemeral)

			guild = str(interaction.guild.id)
			userid = str(member.id)

			# avoid errors by checking if it exists
			db.exists([guild, userid, "xp"], True, 0)

			data = db.read()

			# just get some data yeah
			nextlevel = self.find_next_level(data[guild][userid]["xp"])
			xp_needed = nextlevel.xp_needed
			prev_xp_needed = nextlevel.prev_xp_needed
			currentxp = data[guild][userid]['xp']
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
			if currentlevel < 5:
				tree = "1"
			elif currentlevel < 10:
				tree = "2"
			elif currentlevel < 15:
				tree = "3"
			elif currentlevel < 20:
				tree = "4"
			elif currentlevel < 25:
				tree = "5"
			elif currentlevel < 30:
				tree = "6"
			elif currentlevel >= 30:
				tree = "7"
			
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
			lb = self.LeaderboardView(self.find_next_level, interaction.guild)
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
				color = (88, 101, 242),
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
				colour = templates.colours["fail"]
			)
			await interaction.followup.send(embed=embed)
	
	# leaderboard button
	class LeaderboardView(discord.ui.View):
		"""
		Buttons for the /leaderboard command """

		def __init__(self, find_next_level, guild: discord.Guild, users_per_page: int = 5):
			# if you want to see top 1-10, then 1
			# top 11-20, then 11
			# and so on
			self.leaderboard = []
			self.leaderboard_index = 0
			self.find_next_level = find_next_level
			self.guild = guild
			self.max_per_page = users_per_page

			# generate the leaderboard
			self.generate_leaderboard(self.guild)
			# gonna dump stuff here
			# ◁ ▷

			super().__init__() 
			# apparently I must do this or stuff breaks

		def generate_leaderboard(self, guild: discord.Guild) -> list:
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
			data = db.read()
			guilddata = data[str(guild.id)]

			for user in guilddata:
				# get the user's data
				userdata = guilddata[user]
				# get the user's level
				xp = userdata["xp"]
				level = self.find_next_level(xp).currentlevel

				# add the user to the leaderboard
				self.leaderboard.append(
					{
						"member": guild.get_member(int(user)),
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

		lb = self.LeaderboardView(self.find_next_level, interaction.guild, usersperpage)

		embed = lb.get_leaderboard_embed(
			guild = interaction.guild,
			startindex = 0
		)

		# disable some buttons
		all_buttons = lb.children

		rightbutton = discord.utils.get(all_buttons, custom_id="right")

		if lb.max_per_page > len(lb.leaderboard):
			rightbutton.disabled = True

		await interaction.followup.send(
			embed = embed,
			view = lb
		)





async def setup(bot):
	await bot.add_cog(Levelling(bot))