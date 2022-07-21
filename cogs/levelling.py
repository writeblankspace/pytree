import discord
from discord import app_commands
from discord.ext import commands
from f.__index__ import *
from db.db import db

class Levelling(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.full_progress = "▰"
		self.empty_progress = "▱"
		self.zwnbs = "﻿" # zero-width no-break space

		# 1 message in 60 seconds
		self.cooldown = commands.CooldownMapping.from_cooldown(1.0, 1.0, commands.BucketType.user)

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
		guild = str(message.guild.id)
		author = str(message.author.id)
		if message.author.bot == False and message.author != self.bot.user:
			# cooldowns
			bucket = self.cooldown.get_bucket(message)
			retry_after = bucket.update_rate_limit()
			if retry_after: # rate-limited
				pass
			else: # you can do stuff!
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

				# for testing: see yourself level up
				# await message.reply(f"<@{author}> gained {randxp} xp!\n**level {currentlevel}:** {data[guild][author]['xp']}/{xp_needed}")
	
	group = app_commands.Group(name="levelling", description="Levelling commands")

	@group.command(name="rank")
	@app_commands.describe(
		member = "the member whose rank you'd like to view",
		ephemeral = "whether or not others should see the bot's reply"
	)
	async def rank(self, interaction: discord.Interaction, member: discord.User = None, ephemeral: bool = False) -> None:
		"""
		View your rank in the server. """
		if member == None:
			member = interaction.user
		else:
			member = member

		if member.bot == False:
			await interaction.response.defer(ephemeral=ephemeral)

			guild = str(interaction.guild.id)
			author = str(member.id)

			# avoid errors by checking if it exists
			db.exists([guild, author, "xp"], True, 0)

			data = db.read()

			nextlevel = self.find_next_level(data[guild][author]["xp"])
			xp_needed = nextlevel.xp_needed
			prev_xp_needed = nextlevel.prev_xp_needed
			currentxp = data[guild][author]['xp']
			currentlevel = nextlevel.currentlevel

			# create a progressbar!
			progressbar = ""

			# calculate the progress
			progress = (currentxp - prev_xp_needed) / (xp_needed - prev_xp_needed)
			# make it a percentage, eg 71.3%
			progress = progress * 100
			# divide it by 10 to make it x/10, eg 7.13
			progress = progress / 10
			# round it to the nearest integer, eg 7
			progress = round(progress)

			# create the progressbar
			progressbar += self.full_progress * progress
			progressbar += self.empty_progress * (10 - progress)

			# put a zero-width no-break space after every character
			# this will make it better for small screens
			progressbar = progressbar.replace("", self.zwnbs)

			embed = discord.Embed(
				# `▰▰▰▰▰▰▰▱▱▱`` 70/100 xp
				description = f"""{progressbar} {currentxp - prev_xp_needed}/{xp_needed - prev_xp_needed} xp""", 
			)

			embed.set_author(
				# taylorswift#1989 | level 13 | #1
				name = f"{member.name}#{member.discriminator} | lvl {currentlevel} | #13", 
				icon_url = member.avatar.url
			)

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
			
			f = discord.File(f"trees/default/{tree}.png", filename=f"{tree}.png")
			embed.set_thumbnail(url=f"attachment://{tree}.png")

			await interaction.followup.send(file=f, embed=embed)

			f""" **level {currentlevel}:** {currentxp}/{xp_needed}") """
		else:
			await interaction.response.defer(ephemeral=True)

			embed = discord.Embed(
				title = "You can't rank bots!", 
				colour = templates.colours["fail"]
			)
			await interaction.followup.send(embed=embed)



async def setup(bot):
	await bot.add_cog(Levelling(bot))