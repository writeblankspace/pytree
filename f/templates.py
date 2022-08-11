import discord
class Theme(object):
	def __init__(self):
		self.loader = "<a:loader:1007265720926744586>"
		self.colours = self.Colours()
		self.colors = self.Colours()
	class Colours(object):
		def __init__(self):
			self.primary = 0xb5815b
			self.secondary = 0xb5947b
			self.red = 0xf28a8a
			self.green = 0x8af29a

theme = Theme()
