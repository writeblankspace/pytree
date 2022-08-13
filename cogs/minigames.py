import discord
from discord import app_commands
from discord.ext import commands
from f.calcmulti import calc_multi
from f.stuff.shopitems import shopitems
from db.db import db
import asyncio
from f.__index__ import *
import random


class Minigames(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
		self.currency = "⚇"

	group = app_commands.Group(
		name="minigames", description="Mingame commands: gain money by playing minigames")

	class BugHunt(discord.ui.View):
		def __init__(self, init_user: discord.User, multi: int, embed: discord.Embed):
			self.init_user = init_user
			self.multi = multi

			self.embed = embed

			self.users = [init_user.id]
			self.bugs_killed = 0

			super().__init__()
		
		async def on_timeout(self) -> None:
			for item in self.children:
				item.disabled = True

			await self.message.edit(view=self)

		def use_item(self, interaction: discord.Interaction, itemname: str):
			item = shopitems[itemname]
			kill_multi = item["kill_multi"]

			user = interaction.user
			guildid = str(interaction.guild.id)
			userid = str(user.id)

			db.exists([guildid, userid, "inventory"], True, [])
			data = db.read()

			class Result():
				def __init__(self, success, embed):
					self.success = success
					self.embed = embed

			inventory = data[guildid][userid]["inventory"]

			if itemname in inventory:
				# it's in there so
				# remove "bug spray" from the list
				data[guildid][userid]["inventory"].remove(itemname)
				db.write(data)

				self.bugs_killed += kill_multi
				if user.id not in self.users:
					self.users.append(user.id)

				# edit the message
				description = self.embed.description
				# find everything between the "```"s
				logs = description.split("```")[1]
				newlogs = logs + "\n" + \
					f"{user.name}:: used {itemname} [+{kill_multi}]"
				description = description.replace(logs, newlogs)

				self.embed.__setattr__("description", description)

				db.write(data)

				return Result(True, self.embed)
			else:
				# ITS NOT IN THERE WHY U CLICK THIS BUTTON THEN
				embed = discord.Embed(
					title="You don't have this item!",
					description=f"{itemname.capitalize()} can be bought in the shop.",
					color=theme.colours.red
				)
				return Result(False, embed)

		@discord.ui.button(label='bug spray', style=discord.ButtonStyle.primary, custom_id='bug_spray')
		async def bug_spray(self, interaction: discord.Interaction, button: discord.ui.Button):
			results = self.use_item(interaction, "bug spray")

			if results.success:
				await interaction.response.edit_message(embed=results.embed)
			else:
				await interaction.response.send_message(embed=results.embed, ephemeral=True)

		@discord.ui.button(label='slippers', style=discord.ButtonStyle.secondary, custom_id='slippers')
		async def slippers(self, interaction: discord.Interaction, button: discord.ui.Button):
			results = self.use_item(interaction, "slippers")

			if results.success:
				await interaction.response.edit_message(embed=results.embed)
			else:
				await interaction.response.send_message(embed=results.embed, ephemeral=True)

		@discord.ui.button(label='trainers', style=discord.ButtonStyle.secondary, custom_id='trainers')
		async def trainers(self, interaction: discord.Interaction, button: discord.ui.Button):
			results = self.use_item(interaction, "trainers")

			if results.success:
				await interaction.response.edit_message(embed=results.embed)
			else:
				await interaction.response.send_message(embed=results.embed, ephemeral=True)

		@discord.ui.button(label='flypaper', style=discord.ButtonStyle.secondary, custom_id='flypaper')
		async def flypaper(self, interaction: discord.Interaction, button: discord.ui.Button):
			results = self.use_item(interaction, "flypaper")

			if results.success:
				await interaction.response.edit_message(embed=results.embed)
			else:
				await interaction.response.send_message(embed=results.embed, ephemeral=True)

	@group.command(name="hunt")
	async def hunt(self, interaction: discord.Interaction) -> None:
		"""
		Hunt for bugs to earn xp and money."""
		# await interaction.response.defer(ephemeral=True)

		user = interaction.user
		guildid = str(interaction.guild.id)
		userid = str(user.id)

		# get the user's data
		db.exists([guildid, userid, "equipped"], True, {})
		data = db.read()
		equippedlist = data[guildid][userid]["equipped"]
		xp = data[guildid][userid]["xp"]

		multi = calc_multi(equippedlist, xp)
		kill_multi = multi.kill_multi

		r = random.uniform

		bug_amount = [r(0.1, 2), r(0.1, 2), r(
			0.1, 2), r(2, 5), r(2, 5), r(1, 10)]
		# pick random from bug_amount
		bugs = random.choice(bug_amount) * kill_multi
		bugs = int(bugs)

		if bugs == 0:
			bugs = 1

		embed = discord.Embed(
			title=f"{theme.loader} {user.name} started a bug hunt!",
			description=f"There are **{bugs} bugs** in the area.",
			color=theme.colours.secondary
		)

		footertext = f"This hunt starts in 3 seconds."

		embed.set_footer(text=footertext)

		await interaction.response.send_message(embed=embed)

		db.write(data)

		await asyncio.sleep(3)

		embed = discord.Embed(
			title=f"{theme.loader} {user.name} is hunting for bugs!",
			description=f"There are **{bugs} bugs** in the area. Click on the items you want to use hunt the bugs. There is a 1/3 chance of one bug being killed per attempt.\n" +
			"Other users can join in too! Rewards will be shared equally.\n" +
			"```asciidoc\n" +
			f"{user.name}:: started the bug hunt```",
			color=theme.colours.green
		)

		embed.set_footer(
			text=f"This hunt ends in 15 seconds."
		)

		view = self.BugHunt(user, kill_multi, embed)

		await interaction.edit_original_response(view=view, embed=embed)

		view.message = await interaction.original_response()

		await asyncio.sleep(15)

		embed = discord.Embed(
			title=f"{theme.loader} {user.name}'s hunt ended!",
			description=f"There were **{bugs} bugs** in the area." +
			"\nPlease wait while the results are calculated.",
			color=theme.colours.secondary
		)

		data = db.read()

		await interaction.edit_original_response(view=None, embed=embed)

		await asyncio.sleep(3)

		attempts = view.bugs_killed
		users = view.users

		successes = 0

		for i in range(attempts):
			if random.randint(1, 3) == 1:
				successes += 1

		# no more than {bugs} that can be killed (duh)
		if successes > bugs:
			successes = bugs

		# different bug types return different rewards!

		# 🐝🐞🐜🪰🦟🪳🪲🕷️
		# :bee::lady_beetle::ant::fly::mosquito::cockroach::beetle::spider:
		bug_types = {
			"bee": {"emoji": "🐝", "prize": 50, "plural": "bees"},
			"lady beetle": {"emoji": "🐞", "prize": 77, "plural": "lady beetles"},
			"ant": {"emoji": "🐜", "prize": 10, "plural": "ants"},
			"fly": {"emoji": "🪰", "prize": 10, "plural": "flies"},
			"mosquito": {"emoji": "🦟", "prize": 15, "plural": "mosquitoes"},
			"cockroach": {"emoji": "🪳", "prize": 20, "plural": "cockroaches"},
			"beetle": {"emoji": "🪲", "prize": 30, "plural": "beetles"},
			"spider": {"emoji": "🕷️", "prize": 30, "plural": "spiders"}
		}
		bug_types_rarity = [
			"ant", "ant", "ant",
			"fly", "fly", "fly", "fly", "fly", "fly", "fly", "fly", "fly", "fly", 
			"cockroach", "cockroach", "cockroach", "cockroach", "cockroach", 
			"mosquito", "mosquito", "mosquito",
			"bee", "bee",
			"lady beetle", "beetle", "beetle", "spider"
		]

		bug_types_caught = []
		for i in range(successes):
			bug_type = random.choice(bug_types_rarity)
			bug_types_caught.append(bug_type)

		# return a list of all bug types in the bug_types_caught list
		unique_bug_types_caught = list(set(bug_types_caught))
		bug_types_caught_str = []

		for bug_type in unique_bug_types_caught:
			count = bug_types_caught.count(bug_type)
			emoji = bug_types[bug_type]["emoji"]
			bug_name = bug_types[bug_type]["plural"]
			reward = bug_types[bug_type]["prize"] * count
			bug_types_caught_str.append(f"{emoji} {bug_name}:: {count} [+{reward} {self.currency}]")

		bug_types_caught_str = "\n".join(bug_types_caught_str)

		if bug_types_caught_str == "":
			bug_types_caught_str = "[None]"
		
		bug_rewards = 0

		# get the rewards for each bug
		for bug_type in bug_types_caught:
			bug_rewards += bug_types[bug_type]["prize"]


		money_reward = int(bug_rewards / len(users))
		xp_reward = int((bug_rewards / len(users)) / 2)

		usernames = []

		for auserid in users:
			auserid = str(auserid)
			data[guildid][auserid]["$$$"] += money_reward
			data[guildid][auserid]["xp"] += xp_reward

			# get the user as discord.User
			user = self.bot.get_user(int(auserid))
			usernames.append(user.name)

		db.write(data)

		embed = discord.Embed(
			title=f"{user.name}'s hunt results:",
			description=f"**{successes} bugs** were killed out of {attempts} attempts." + "\n" +
			f"There were {bugs} bugs in the area." + "\n" +
			f"Each user earned **{money_reward} {self.currency}** and **{xp_reward} xp**.",
			color=theme.colours.green
		)

		embed.add_field(
			name = "Bugs caught",
			value = "```asciidoc\n" + bug_types_caught_str + "```",
			inline = True
		)

		embed.add_field(
			name = "Participants",
			value = f"```{', '.join(usernames)}```",
			inline = True
		)

		await interaction.edit_original_response(view=None, embed=embed)

	@group.command(name="roll")
	@has_enough_money(2)
	async def roll(self, interaction: discord.Interaction) -> None:
		"""
		Rolling more than 2 numbers of the same kind gives you money."""
		await interaction.response.defer(ephemeral=False)

		def r():
			return random.randint(1, 9)
		
		rolled = []

		for i in range(4):
			rolled.append(r())
		
		emojis = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]

		rolled_str = ""

		for i in rolled:
			rolled_str += emojis[i]

		embed = discord.Embed(
			title = "Rolling the machine...",
		)

		guildid = str(interaction.guild.id)
		userid = str(interaction.user.id)
		db.exists([guildid, userid, "$$$"], True, 0)
		db.exists([guildid, userid, "rolls"], True, 0)

		data = db.read()

		data[guildid][userid]["rolls"] += 1
		rolls = data[guildid][userid]["rolls"]

		# check for how many duplicates there are
		rolledset = set(rolled)
		duplicates = len(rolled) - len(rolledset)

		# eg rolled = [1, 1, 1, 1], duplicates = 3
		# eg rolled = [1, 1, 1, 2], duplicates = 2
		# eg rolled = [1, 1, 2, 3], duplicates = 1
		# eg rolled = [1, 2, 3, 4], duplicates = 0

		# eg rolled = [1, 1, 2, 2], duplicates = 2
		
		# if all the numbers are the same, you win!

		rolled_int = int(f"{rolled[0]}{rolled[1]}{rolled[2]}{rolled[3]}")

		if rolled_int == int(interaction.user.discriminator):
			win = True
			# cool prize
			prize = int(rolled_int / 5)
			description = "Your disciminator!"
			embed.color = theme.colours.green

		if rolled_int == 1989:
			win = True
			# cool prize
			prize = 1989
			description = "Special 1989!"
			embed.color = theme.colours.green

		elif duplicates == 3:
			win = True
			# get the first 3 characters
			prize = int(rolled_int / 10)
			description = "Four-of-a-kind!"
			embed.color = theme.colours.green

		elif duplicates == 2:
			win = True
			# minor prize (1111 = 4)
			# find the occurences of the first number
			occurences = rolled.count(rolled[0])
			if occurences == 2:
				description = "Double-two-of-a-kind!"
			else:
				description = "Three-of-a-kind!"
			prize = int(rolled_int / 300)
			embed.color = theme.colours.primary

		else:
			win = False
			data[guildid][userid]["$$$"] -= 2
			# no prize rip
			prize = 0
			description = "Better luck next time!"
			embed.color = theme.colours.red
		
		if prize <= 0 and win:
			# sum of items in rolled
			prize = sum(rolled)
		
		embed.description = f"{rolled_str} {description}"
		
		if prize > 0:
			embed.set_footer(
				text = f"You won {prize} {self.currency}  •  roll #{rolls}"
			)
		else:
			embed.set_footer(
				text = f"You lost 2 {self.currency}  •  roll #{rolls}"
			)
		
		data[guildid][userid]["$$$"] += prize
		db.write(data)

		await interaction.followup.send(embed=embed)




async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Minigames(bot))
