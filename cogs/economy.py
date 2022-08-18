import discord
from discord import app_commands
from discord.ext import commands
from f.stuff.shopitems import shopitems
from f.__index__ import *
from db.db import db
from db.sql import *

class Economy(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.currency = "⚇"
		self.shopitems = shopitems
	
	group = app_commands.Group(name="economy", description=f"Economy commands: earn coins, spend coins, and more")

	# some of the economy commands will be in other cogs
	# levels: levelling up gives you some $$$
	# admin: archivemonth also removes equipped products

	# inventory stuff
	class ItemActions(discord.ui.View):
		def __init__(
			self, 
			currency: str,
			embed: discord.Embed,
			owner: discord.User,
			item: str,
			equippable: bool = False,
			sellable: bool = False
		):
			self.currency = currency
			self.embed = embed
			self.owner = owner
			self.item = item
			self.equippable = equippable
			self.sellable = sellable

			price = shopitems[self.item]["price"]
			# get 65% of the price
			self.price = int(price * 0.75)

			super().__init__()

			# disable some buttons
			self.disable_buttons()
		
		async def on_timeout(self) -> None:
			for item in self.children:
				item.disabled = True

			await self.message.edit(view=self)
		
		def disable_buttons(self):
			all_buttons = self.children
			equip = discord.utils.get(all_buttons, custom_id="equip")
			sell = discord.utils.get(all_buttons, custom_id="sell")
			sell.label = f"sell for {self.price} {self.currency}"
			equip.disabled = not self.equippable
			sell.disabled = not self.sellable

		@discord.ui.button(custom_id="equip", label='equip', style=discord.ButtonStyle.green)
		async def equip(self, interaction: discord.Interaction, button: discord.ui.Button):
			# assuming that this is the inventory
			# and that the item is equippable
			guildid = interaction.guild.id
			ownerid = self.owner.id

			# check stuff to avoid errors
			await psql.check_user(ownerid, guildid)

			if interaction.user == self.owner:
				# get the user's inventory
				row = await psql.db.fetchrow(
					"""--sql
					SELECT inventory, equipped FROM users
					WHERE userid = $1 and guildid = $2
					""",
					ownerid, guildid
				)
				inventory = psql.commasplit(row["inventory"])
				equipped = psql.commasplit(row["equipped"])

				# find the index of the item in the inventory
				index = inventory.index(self.item)

				# remove from the inventory
				inventory.pop(index)
				# add to equipped
				equipped.append(self.item)

				if self.item in inventory:
					# it's still in there, so can still be equipped and sold
					self.equippable = True
					self.sellable = True
				else:
					self.equippable = False
					# you can't sell a non-existent item already equipped
					self.sellable = False
				
				self.disable_buttons()

				# save the data
				connection = await psql.db.acquire()
				async with connection.transaction():
					await psql.db.execute(
						"""--sql
						UPDATE users
						SET inventory = $1, equipped = $2
						WHERE userid = $3 and guildid = $4
						""",
						psql.commasjoin(inventory), psql.commasjoin(equipped),
						ownerid, guildid
					)
				await psql.db.release(connection)

				# update the embed
				title = self.embed.title
				description = self.embed.description

				# log stuff in the description
				# if ``` .* ``` is in the description, replace the inside with stuff
				message = f"Equipped x1 of {self.item}"
				if "```" in description:
					# find the start and end of the code block
					start = description.find("```")
					end = description.find("```", start + 3)
					# get the code block
					logs = description[start + 3:end]
					# replace the code block with the new stuff
					description = description.replace(logs, logs + "\n" + message)
				else:
					description += "\n```\n" + f"{message}```"

				# find out how many of the item is in the inventory now
				inventory = inventory
				if self.item in inventory:
					intcount = inventory.count(self.item)
					if intcount > 0:
						count = f" (x{intcount})"
					else:
						count = " [Not in the inventory]"
					title = title.replace(f" (x{intcount + 1})", count)
				else:
					intcount = 0
					count = " [Not in the inventory]"
					if f" (x{intcount + 1})" in title:
						title = title.replace(f" (x{intcount + 1})", count)
					else:
						title += count
				self.embed.__setattr__("title", title)
				self.embed.__setattr__("description", description)


				await interaction.response.edit_message(embed=self.embed, view=self)
			else:
				embed = discord.Embed(
					title="Only the owner of this item can do this!",
					color = theme.colours.red
				)
				await interaction.response.send_message(embed=embed, ephemeral=True)

		@discord.ui.button(custom_id="sell", label='sell', style=discord.ButtonStyle.red)
		async def sell(self, interaction: discord.Interaction, button: discord.ui.Button):
			# assuming that this is the inventory
			# and that the item is equippable
			guildid = interaction.guild.id
			ownerid = self.owner.id

			# check stuff to avoid errors
			await psql.check_user(ownerid, guildid)

			if interaction.user == self.owner:
				# get the user's inventory
				row = await psql.db.fetchrow(
					"""--sql
					SELECT inventory, equipped, balance FROM users
					WHERE userid = $1 and guildid = $2
					""",
					ownerid, guildid
				)
				
				inventory = psql.commasplit(row["inventory"])
				equipped = psql.commasplit(row["equipped"])
				balance = row["balance"]

				# find the index of the item in the inventory
				index = inventory.index(self.item)

				# remove from the inventory
				inventory.pop(index)
				# instead of equipping, sell the item
				price = self.price
				# add to the user's balance
				balance = row["balance"] + price

				# save the data
				connection = await psql.db.acquire()
				async with connection.transaction():
					await psql.db.execute(
						"""--sql
						UPDATE users
						SET inventory = $1, balance = $2
						WHERE userid = $3 and guildid = $4
						""",
						psql.commasjoin(inventory), balance,
						ownerid, guildid
					)
				await psql.db.release(connection)

				if self.item in inventory:
					# it's still in there, so can still be equipped and sold
					if self.equippable != True:
						self.equippable = True
					if self.sellable != False:
						self.sellable = True
				else:
					self.equippable = False
					# you can't sell a non-existent item already equipped
					self.sellable = False
				
				self.disable_buttons()

				# update the embed
				title = self.embed.title
				description = self.embed.description

				# log stuff in the description
				# if ``` .* ``` is in the description, replace the inside with stuff
				message = f"Sold x1 of {self.item} for {price} {self.currency}"
				if "```" in description:
					# find the start and end of the code block
					start = description.find("```")
					end = description.find("```", start + 3)
					# get the code block
					logs = description[start + 3:end]
					# replace the code block with the new stuff
					description = description.replace(logs, logs + "\n" + message)
				else:
					description += "\n```\n" + f"{message}```"

				# find out how many of the item is in the inventory now
				inventory = inventory
				if self.item in inventory:
					intcount = inventory.count(self.item)
					if intcount > 0:
						count = f" (x{intcount})"
					else:
						count = " [Not in the inventory]"
					title = title.replace(f" (x{intcount + 1})", count)
				else:
					intcount = 0
					count = " [Not in the inventory]"
					if f" (x{intcount + 1})" in title:
						title = title.replace(f" (x{intcount + 1})", count)
					else:
						title += count
				self.embed.__setattr__("title", title)
				self.embed.__setattr__("description", description)


				await interaction.response.edit_message(embed=self.embed, view=self)
			else:
				embed = discord.Embed(
					title="Only the owner of this item can do this!",
					color = theme.colours.red
				)
				await interaction.response.send_message(embed=embed, ephemeral=True)

	class InventoryDropdown(discord.ui.Select):
		def __init__(self, currency: str, equipped: bool, user: discord.User, inventorylist: list, ephemeral: bool, ItemActions):
			self.currency = currency
			self.equipped = equipped # 1 for equipped items, 2 for inventory items
			self.user = user
			self.ephemeral = ephemeral
			self.ItemActions = ItemActions

			# inventorylist is a list of items in the inventory
			# make it a dict {"name": amount}
			self.items_with_count = {}
			for item in inventorylist:
				if item in self.items_with_count:
					self.items_with_count[item] += 1
				else:
					self.items_with_count[item] = 1

			# {"item": count}
			# Set the options that will be presented inside the dropdown
			options = []
			for item in self.items_with_count.keys():
				count = self.items_with_count[item]
				if count == 1:
					count = ""
				else:
					count = f"(x{count}) "

				description = f"{count}{shopitems[item]['description']}"
				# only get the first 100 characters of the description
				if len(description) > 100:
					description = description[:97] + "..."

				options.append(
					discord.SelectOption(
						label = item,
						description = description
					)
				)
			
			if equipped == True:
				placeholder = "View equipped items..."
			elif equipped == False:
				placeholder = "View inventory items..."

			super().__init__(
				placeholder=placeholder,
				min_values=1,
				max_values=1,
				options=options
				)

		async def callback(self, interaction: discord.Interaction):
			# self.values = list of selected options
			item = self.values[0]
			# get the item's description
			description = shopitems[item]["description"]
			use = shopitems[item]["use"]
			equip = shopitems[item]["equip"]

			about = self.items_with_count[item]
			if self.equipped == True:
				if about == 1:
					about = " [Equipped]"
				else:
					about = f" [Equipped x{about}]"
			elif self.equipped == False:
				if about == 1:
					about = ""
				else:
					about = f" (x{about})"
			
			description = f"{description} {use}"
			if equip and item != "python":
				description = f"{description} Can be equipped until the monthly reset."
			
			embed = discord.Embed(
				# capitalise item name
				title = f"{item.capitalize()}{about}",
				description = description,
				color = theme.colours.primary
			)
			embed.set_footer(
				text = f"Owned by {self.user.name}#{self.user.discriminator}",
			)

			if not self.equipped and equip == True:
				# not equipped yet / can be equipped
				equippable = True
			else:
				# it's equipped already / can't be equipped
				equippable = False
			
			if not self.equipped:
				# can be sold
				sellable = True
			else:
				sellable = False

			view = self.ItemActions(
				currency = self.currency,
				embed = embed,
				owner = self.user,
				item = item,
				equippable = equippable,
				sellable = sellable
			)

			view.message = await interaction.response.edit_message(
				embed = embed,
				view = view
			)
	
	class InventoryDropdownView(discord.ui.View):
		def __init__(self, InventoryDropdown, currency: str, user: discord.User, inventorylist: list, equippedlist: list, ephemeral: bool, ItemActions):
			super().__init__()

			# Adds the dropdown to our view object.
			if len(equippedlist) > 0:
				self.add_item(
					InventoryDropdown(currency, True, user, equippedlist, ephemeral, ItemActions)
				)
			if len(inventorylist) > 0:
				self.add_item(
					InventoryDropdown(currency, False, user, inventorylist, ephemeral, ItemActions)
				)
		
		async def on_timeout(self) -> None:
			for item in self.children:
				item.disabled = True

			await self.message.edit(view=self)

	@group.command(name="stats")
	@app_commands.describe(
		member = "the member to get the stats of"
	)
	async def stats(
		self,
		interaction: discord.Interaction,
		member: discord.User = None,
		ephemeral: bool = True
		) -> None:
		"""
		Gets the balance and inventory of a user. """

		if member == None:
			member = interaction.user
		else:
			member = member
		
		if member.bot:
			await interaction.response.defer(ephemeral=True)

			embed = discord.Embed(
				title = "You can't rank bots!", 
				colour = theme.colours.red
			)
			await interaction.followup.send(embed=embed)
		else:
			await interaction.response.defer(ephemeral=ephemeral)
			guildid = interaction.guild.id
			memberid = member.id

			# avoid errors
			await psql.check_user(memberid, guildid)

			row = await psql.db.fetchrow(
				"""--sql
				SELECT balance, xp, inventory, equipped FROM users
				WHERE userid = $1 AND guildid = $2
				""",
				memberid, guildid
			)

			coins = row["balance"]
			xp = row["xp"]
			inventory = row["inventory"]
			equipped = row["equipped"]

			inventorylist = psql.commasplit(inventory)
			equippedlist = psql.commasplit(equipped)

			# sort lists alphabetically
			inventorylist.sort()
			equippedlist.sort()

			# get the kill and xp multipliers
			multi = calc_multi(equippedlist, xp)
			kill_multi = multi.kill_multi
			xp_multi = multi.xp_multi

			newline = "\n"

			general = [
				f"balance: {coins} {self.currency}",
				f"hunting multiplier: {kill_multi - 1}",
				f"xp multiplier: {xp_multi - 1}"
			]
			general = "\n".join(general)

			ogequipped = equippedlist.copy()
			oginventory = inventorylist.copy()

			embed = discord.Embed(
				title = f"{member.name}'s stats",
				description = general,
				color = theme.colours.primary
			)

			if len(inventorylist) == 0:
				embed.set_footer(
					text = "This user's inventory is empty. Items can be bought in the shop."
				)
			elif len(equippedlist) == 0:
				embed.set_footer(
					text = "This user has no equipped items. Items can be equipped by selecting them in the inventory."
				)
			
			if len(equippedlist) == 0:
				equippedlist.append("[There are no equipped items.]")
			if len(inventorylist) == 0:
				inventorylist.append("[This inventory is empty.]")

			view = self.InventoryDropdownView(
				self.InventoryDropdown,
				currency = self.currency,
				user = member,
				inventorylist = oginventory,
				equippedlist = ogequipped,
				ephemeral = ephemeral,
				ItemActions = self.ItemActions
			)
			view.message = await interaction.followup.send(embed=embed, view=view)

	# leaderboard
	class LeaderboardView(discord.ui.View):
		"""
		Buttons for the /leaderboard command """

		def __init__(self, guild: discord.Guild, currency: str, users_per_page: int = 5):
			# if you want to see top 1-10, then 1
			# top 11-20, then 11
			# and so on
			self.leaderboard = []
			self.leaderboard_index = 0
			self.guild = guild
			self.max_per_page = users_per_page
			self.currency = currency

			# generate the leaderboard
			self.generate_leaderboard(self.guild)
			# gonna dump stuff here
			# ◁ ▷

			super().__init__() 
			# apparently I must do this or stuff breaks
		
		async def on_timeout(self) -> None:
			for item in self.children:
				item.disabled = True

			await self.message.edit(view=self)

		def generate_leaderboard(self, guild: discord.Guild) -> list:
			"""
			Gives a list of the leaderboard.
			
			`guild` is the server to get the leaderboard for 
			
			Returns a list of dicts, each dict containing the member and $$$.

			```py
			[
				{
					"member": discord.User,
					"$$$": int
				}, {}, {} # etc
			] 
			```"""

			# get the data
			data = db.read()
			guilddata = data[str(guild.id)]

			for user in guilddata:
				db.exists([str(guild.id), user, "$$$"], True, 0)
				data = db.read()
				# get the user's data
				userdata = data[str(guild.id)][user]
				# get the user's level
				bal = userdata["$$$"]

				# add the user to the leaderboard
				self.leaderboard.append(
					{
						"member": guild.get_member(int(user)),
						"$$$": bal
					}
				)
			
			# sort the users by most $$$ to least $$$
			# I have no idea how to use lambda, but GitHub copilot said to use it
			# I think this lambda basically returns the xp of the dict, x being the dict
			self.leaderboard.sort(key=lambda x: x["$$$"], reverse=True)

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
				bal = user["$$$"]

				# make the description
				description_list.append(
					f"**`#{rank}`** | {member.mention} | {bal} {self.currency}"
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
		Views the economy leaderboard. """
		await interaction.response.defer(ephemeral=ephemeral)

		lb = self.LeaderboardView(interaction.guild, self.currency, usersperpage)

		embed = lb.get_leaderboard_embed(
			guild = interaction.guild,
			startindex = 0
		)

		# disable some buttons
		all_buttons = lb.children

		rightbutton = discord.utils.get(all_buttons, custom_id="right")

		if lb.max_per_page > len(lb.leaderboard):
			rightbutton.disabled = True

		lb.message = await interaction.followup.send(
			embed = embed,
			view = lb
		)

	# shop
	class ShopDrop(discord.ui.Select):
		def __init__(self, currency: str):
			self.currency = currency
			itemkeys = shopitems.keys()
			# sort keys by price
			itemkeys = sorted(itemkeys, key=lambda x: shopitems[x]['price'])

			options = []

			for itemkey in itemkeys:
				name = shopitems[itemkey]['name']
				description = shopitems[itemkey]['description']
				price = f"{shopitems[itemkey]['price']} {self.currency}"

				description = f"[{price}] {description}"
				# only get the first 100 characters of the description
				if len(description) > 100:
					description = description[:97] + "..."

				options.append(
					discord.SelectOption(
						label = name,
						description = description
					)
				)
			
			super().__init__(
				placeholder='View shop items...',
				min_values=1,
				max_values=1,
				options=options
			)
		

		async def callback(self, interaction: discord.Interaction):
			# Use the interaction object to send a response message containing
			# the user's favourite colour or choice. The self object refers to the
			# Select object, and the values attribute gets a list of the user's
			# selected options. We only want the first one.
			item = self.values[0]
			itemdict = shopitems[item]

			name = itemdict["name"]
			description = itemdict["description"]
			use = itemdict["use"]
			price = itemdict["price"]
			kill_multi = itemdict.get("kill_multi")
			xp_multi = itemdict.get("xp_multi")
			equip = itemdict["equip"]

			description = f"{description} {use}"
			if equip:
				description = f"{description} Can be equipped for effects."

			embed = discord.Embed(
				title = f"{name.capitalize()} [{price} {self.currency}]",
				description = description,
				color = theme.colours.primary
			)
			
			view = self.view
			view.shopitem = item.lower()
			all_buttons = view.children
			buybutton = discord.utils.get(all_buttons, custom_id="buy")
			balancebutton = discord.utils.get(all_buttons, custom_id="balance")
			if buybutton == None:
				view.add_item(view.buy)
			if balancebutton == None:
				view.add_item(view.balance)
			# get it again
			all_buttons = view.children
			buybutton = discord.utils.get(all_buttons, custom_id="buy")
			buybutton.label = f"buy this item for {price} {self.currency}"

			await interaction.response.edit_message(embed=embed, view=view)

	class ShopDropView(discord.ui.View):
		def __init__(self, ShopDrop, currency: str):
			super().__init__()

			# Adds the dropdown to our view object.
			self.currency = currency
			self.shopitem = None
			self.add_item(ShopDrop(currency))

			# remove the buy button
			all_buttons = self.children
			buybutton = discord.utils.get(all_buttons, custom_id="buy")
			balancebutton = discord.utils.get(all_buttons, custom_id="balance")
			self.remove_item(buybutton)
			self.remove_item(balancebutton)
		
		async def on_timeout(self) -> None:
			for item in self.children:
				item.disabled = True

			await self.message.edit(view=self)

		@discord.ui.button(label='buy', style=discord.ButtonStyle.primary, custom_id="buy", row=2)
		async def buy(self, interaction: discord.Interaction, button: discord.ui.Button):
			guildid = str(interaction.guild.id)
			userid = str(interaction.user.id)
			itemdict = shopitems[self.shopitem]

			price = itemdict["price"]

			data = db.read()

			cash = data[guildid][userid]["$$$"]
			
			if cash >= price:
				# remove the money and add the item
				data[guildid][userid]["$$$"] -= price
				data[guildid][userid]["inventory"].append(self.shopitem)
				db.write(data)

				embed = discord.Embed(
					title = f"You bought x1 of {self.shopitem}",
					description = f"You now have {data[guildid][userid]['$$$']} {self.currency}",
					color = theme.colours.green
				)
				await interaction.response.send_message(embed=embed, ephemeral=True)
			else:
				embed = discord.Embed(
					title = f"You don't have enough money to buy that.",
					description = "\n".join([f"You only have {cash} {self.currency}.",
						f"You'll need {price - cash} more to buy it."]),
					color = theme.colours.red
				)
				await interaction.response.send_message(embed=embed, ephemeral=True)

		@discord.ui.button(label='view my stats', style=discord.ButtonStyle.secondary, custom_id="balance", row=2)
		async def balance(self, interaction: discord.Interaction, button: discord.ui.Button):
			guildid = str(interaction.guild.id)
			userid = str(interaction.user.id)

			data = db.read()
			balance = data[guildid][userid]["$$$"]

			itemdict = shopitems[self.shopitem]
			price = itemdict["price"]

			if balance >= price:
				colour = theme.colours.green
			else:
				colour = theme.colours.red
			
			# how many of this item do you have?
			inventory = data[guildid][userid]["inventory"]
			count = inventory.count(self.shopitem)

			embed = discord.Embed(
				title = f"You have {balance} {self.currency}",
				description = "\n".join([
					f"If you buy this item, you'll have **{balance - price} {self.currency}** left.",
					f"You have **{count}** of this item ({self.shopitem}) in your inventory."
					]),
				color = colour
			)

			await interaction.response.send_message(embed=embed, ephemeral=True)
	
	@group.command(name="shop")
	@app_commands.describe(
		ephemeral = "whether or not others should see the bot's reply",
	)
	async def shop(self, interaction: discord.Interaction, ephemeral: bool = True) -> None:
		"""
		Views the shop and its items."""
		await interaction.response.defer(ephemeral=ephemeral)

		# random from shopitems keys
		shopitems_keys = list(shopitems.keys())
		random_key = random.choice(shopitems_keys)

		feature = shopitems[random_key]
		name = feature["name"].capitalize()
		description = feature["description"]
		price = feature["price"]

		embed = discord.Embed(
			title = f"{self.bot.user.name} Shop",
			description = f"**{name}:** {description} For {price} {self.currency} only!",
			color = theme.colours.primary
		)

		view = self.ShopDropView(self.ShopDrop, self.currency)

		view.message = await interaction.followup.send(embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(Economy(bot))