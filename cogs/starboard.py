import discord
from discord.ext import commands
import datetime
from db.db import db
from db.sql import *


class Starboard(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.Cog.listener()  # starboard
	async def on_raw_reaction_add(self, ctx: discord.RawReactionActionEvent) -> None:
		channel = self.bot.get_channel(ctx.channel_id)
		guild = ctx.guild_id

		await psql.check_guild(guild)

		row = await psql.db.fetchrow(
			"""--sql
			SELECT starboardid FROM guilds
			WHERE guildid = $1;
			""",
			guild
		)

		if row == None:
			return

		starboard = row["starboardid"]
		
		data = db.read()

		emoji = "📌"

		star_channel = starboard

		if star_channel != None:
			board = self.bot.get_channel(star_channel)
			if channel != star_channel:
				message = await channel.fetch_message(ctx.message_id)
				attachment = message.attachments

				file = ""
				link = message.jump_url

				for i in attachment:
					# await i.to_file(use_cached = True)
					file = i.url

				if ctx.emoji.name == emoji:
					# print(message.reactions)
					count = 0
					for i in message.reactions:
						if i.emoji == emoji:
							count = i.count

					# print(message.content)

					if count == 1:

						embed = discord.Embed(
							description=f"<#{channel.id}> — [Jump]({link}) \n\n{message.content}"
						)

						embed.set_author(
							name=f"{message.author.name}",
							# url = 'Url to author',
							icon_url=message.author.avatar.url
						)
						
						# add channel and msg jump
						if file != "":
							embed.set_image(url=file)
						embed.set_footer(
							text=f"{emoji} | {str(message.author.id)}")
						embed.timestamp = datetime.datetime.utcnow()
						embed.colour = 0xdd2e44 #0xffac33

						await board.send(embed=embed)

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Starboard(bot))
