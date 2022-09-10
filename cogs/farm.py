import discord
from discord import app_commands
from discord.ext import tasks, commands
from db.sql import *
from f.__index__ import *

class Farm(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot

		# farm funcs
		self.ff = self.FF()
		self.farmloop.start(
			guilds = [
				(743128328390836325, 743128328705409078)#,
				#(999340987392462878, 1018175324283994122)
			]
		)
	
	group = app_commands.Group(
		name = "farm",
		description = "Farm commands: plant crops and harvest them for cash... or lose everything in a blight"
	)

	class FF():
		def __init__(self):
			# users
			self.watering_users = []
			self.strengthening_users = []
			self.weeding_users = []
			# every bot restart, this resets
		
		def get_bloom_chance(self):
			# 5400
			watering = len(self.watering_users)
			if watering <= 0:
				watering = 1
			return int(100 * (0.95 ** watering))
		
		async def get_bloom_strength(self, guildid):
			strength = await self.get_blight_strength(guildid)
			strength *= float(random.randint(1, 7)) * 0.0001
			strength += 1
			return round(strength, 3)

		def get_strengthened_percentage(self) -> int:
			total_users = len(
				self.watering_users + \
					self.strengthening_users + \
						self.weeding_users
			)
			if total_users <= 0:
				return 0

			strengthening = self.strengthening_users

			if strengthening <= 0:
				return 0

			percent = len(strengthening) / (total_users * 100)
		
			return int(percent)
		
		async def get_blight_strength(self, guildid: int) -> int:
			weeding = len(self.weeding_users)

			row = await psql.db.fetchrow(
				"""--sql
				SELECT blight_strength FROM guilds
				WHERE guildid = $1;
				""", 
				guildid
			)

			blight_strength = row["blight_strength"]

			return int(blight_strength * (1.10 ** weeding))

		async def get_blight_chance(self, guildid: int) -> int:
			# 500000 
			strength = await self.get_blight_strength(guildid)
			return int(500 - strength)
		
		async def reset(self, guildid: int, blight: bool = False):
			strengthened = self.get_strengthened_percentage()

			self.watering_users = []
			self.strengthening_users = []
			self.weeding_users = []

			if blight:
				connection = await psql.db.acquire()
				async with connection.transaction():
					await psql.db.execute(
						"""--sql
						UPDATE users
						SET planted = planted - ((planted / 100) * $1)
						WHERE guildid = $2;
						""",
						strengthened, guildid
					)

					await psql.db.execute(
						"""--sql
						UPDATE guilds
						SET blight_strength = 0
						WHERE guildid = $1;
						""",
						guildid
					)
				await psql.db.release(connection)


	# variable list:
	# - bloom_chance
	# - strengthened_crops
	# - blight_strength
	# - blight_chance

	def cog_unload(self):
		self.farmloop.cancel()

	@tasks.loop(seconds=1)
	async def farmloop(self, guilds: list):
		connection = await psql.db.acquire()
		async with connection.transaction():
			for guild in guilds:
				await psql.check_guild(guild[0])
				# make sure all defaults are done
				# and channel id's are set
				await psql.db.execute(
					f"""--sql
					UPDATE guilds
					SET farmid = $1
					WHERE farmid IS NULL AND guildid = $2;
					""",
					guild[1], guild[0]
				)
		await psql.db.release(connection)

		ff = self.ff

		for guild in guilds:
			guilddata = guild
			guildid = guilddata[0]
			guild: discord.Guild = self.bot.get_guild(guildid)
			channelid = guilddata[1]
			channel: discord.TextChannel = self.bot.get_channel(channelid)

			bloom_chance = ff.get_bloom_chance()
			bloom_strength = await ff.get_bloom_strength(guildid)
			strengthened_percentage = ff.get_strengthened_percentage()

			connection = await psql.db.acquire()
			async with connection.transaction():
				await psql.db.execute(
					"""--sql
					UPDATE guilds
					SET blight_strength = blight_strength + 1
					WHERE guildid = $1;
					""",
					guildid
				)
			await psql.db.release(connection)

			blight_strength = await ff.get_blight_strength(guildid)
			blight_chance = await ff.get_blight_chance(guildid)

			# farm stuff
			with open('farm.x.txt', 'w') as f:
				f.write(f"bloom_chance = {bloom_chance}\nbloom_strength = {bloom_strength}\nstrengthened_percentage = {strengthened_percentage}\nblight_strength = {blight_strength}\nblight_chance = {blight_chance}\n\n***\n")

			if blight_chance <= 0:
				blight_chance = 1

			is_blight = random.randint(1, blight_chance)

			if is_blight == 1:
				# OMG BLIGHT
				embed = discord.Embed(
					title = "The Blight",
					color = theme.colours.red
				)

				planted = await psql.db.fetchrow(
					"""--sql
					SELECT SUM(planted)
					FROM users
					WHERE guildid = $1 and planted > 0;""",
					guildid
				)

				users = await psql.db.fetchrow(
					"""--sql
					SELECT COUNT(userid)
					FROM users
					WHERE guildid = $1 and planted > 0;""",
					guildid
				)

				planted = planted[0]
				if planted == None:
					planted = 0

				users = users[0]
				embed.description = f"With a strength of {blight_strength}, the Blight wiped out **{planted} crops** from {users} farmers."

				await ff.reset(guildid, blight = True)

				await channel.send(embed=embed)

				for guildb in guilds:
					if guildb[0] != guildid:
						myembed = embed
						myembed.title = f"Blight in server {guild.name}"
						embed.set_footer(
							text = "This does not affect this server, but all actions are available again."
						)
						channelb = self.bot.get_channel(guildb[1])
						await channelb.send(embed=embed)

			else:
				# blooms are allowed now!
				is_bloom = random.randint(1, bloom_chance)
				if is_bloom == 1:
					connection = await psql.db.acquire()
					async with connection.transaction():
						await psql.db.execute(
							"""--sql
							UPDATE users
							SET planted = planted * $1
							WHERE guildid = $2;
							""",
							bloom_strength, guildid
						)
					await psql.db.release(connection)

					embed = discord.Embed(
						title = "The Bloom",
						color = theme.colours.green
					)

					embed.description = f"All crops have grown by **{bloom_strength}**."
					await channel.send(embed=embed)
	
	@farmloop.before_loop
	async def before_farmloop(self):
		await self.bot.wait_until_ready()
	

	@group.command(name="stats")
	async def stats(self, interaction: discord.Interaction) -> None:
		"""
		Gets the stats of the server's farm"""
		guildid = interaction.guild.id
		userid = interaction.user.id

		await psql.check_guild(guildid)
		await psql.check_user(userid, guildid)

		

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Farm(bot))