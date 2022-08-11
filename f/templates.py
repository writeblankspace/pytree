import discord


class Embeds(object):
	def __init__(self, colours, pfp):
		self.colours = colours
		self.pfp = pfp

	def default(self, colour: hex, message: str, description: str = None, footer: str = None, ctx = None):
		""" Returns a discord embed with the standard template """
		embed = discord.Embed(
			colour=colour,
		)
		embed.set_author(
			name=message,
			icon_url=self.pfp
		)

		if description != None:
			embed.description = description
		if footer != None:
			embed.set_footer(
				text=footer
			)
		elif ctx != None:
			embed.set_footer(
				text=f"invoked by {ctx.author.name}"
			)
		return embed

	def colour(self, colourname: str, message: str, description: str = None, footer: str = None, ctx = None):
		""" Returns a discord embed with the success template """
		embed = self.default(
			colour=self.colours[colourname],
			message=message,
			description=description,
			footer=footer,
			ctx=ctx
		)
		return embed


class Templates(object):
	""" templates.pfp
	templates.colours[(colour)]
	templates.embeds.(default | colour) """

	def __init__(self):
		self.pfp = "https://cdn.discordapp.com/avatars/881461215057047554/d86de78a2bbe510a177a6a2616681d85.png?size=2048"
		# templates.colours.name
		self.colours = {
			"success": 0x79ffc2,
			"fail": 0xff7998,
			"draw": 0xf7b90f
		}
		# templates.msgs.name
		self.embeds = Embeds(
			colours=self.colours,
			pfp=self.pfp
		)
		self.loader = "<:loader:1007246985893511248>"

class Theme(object):
	def __init__(self):
		self.loader = "<:loader:1007256284178939904:>"
		self.colours = self.Colours()
		self.colors = self.Colours()
	class Colours(object):
		def __init__(self):
			self.primary = 0xb5815b
			self.secondary = 0xb5947b
			self.red = 0xf28a8a
			self.green = 0x8af29a

theme = Theme()
templates = Templates()
# templates.pfp
# templates.colours[(colour)]
# templates.embeds.(default | colour)
