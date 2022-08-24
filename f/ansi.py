"\u001b[{format};{color}m"

class AnsiMd():
	def __init__(self):
		self.format = self.Format()
		self.color = self.Color()
		self.backgroundcolor = self.BackgroundColor()

	def ansi(self, format: tuple | int = None, color: int = None, backgroundcolor: int = None):
		if type(format) is int:
			format = tuple([format])

		mylist = []

		if format is not None:
			for f in format:
				mylist.append(str(f))
		
		if color is not None:
			mylist.append(str(color))

		if backgroundcolor is not None:
			mylist.append(str(backgroundcolor))
		
		ansistr = f"\u001b[{';'.join(mylist)}m"
		return ansistr

	def normal(self):
		return "\u001b[0m"
	
	class Format():
		def __init__(self):
			self.normal = 0
			self.bold = 1
			self.faint = 2
			self.italic = 3
			self.underline = 4
	
	class Color():
		def __init__(self):
			self.gray = 30
			self.red = 31
			self.green = 32
			self.yellow = 33
			self.blue = 34
			self.magenta = 35
			self.cyan = 36
			self.white = 37
	
	class BackgroundColor():
		def __init__(self):
			self.firefly_dark_blue = 40
			self.orange = 41
			self.marble_blue = 42
			self.greyish_turquiose = 43
			self.gray = 44
			self.blurple = 45
			self.light_gray = 46
			self.white = 47

ansimd = AnsiMd()