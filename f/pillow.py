from PIL import Image, ImageDraw, ImageFont, ImageColor
import requests
import random

def rankcard(pfpurl: str, username: str, discrim: str, other: str, treenumber: int, color: str, progress: int):
	"""
	Creates a rank card for /rank """
	# get pfp
	pfp = Image.open(requests.get(pfpurl, stream=True).raw)
	# make it smaller
	pfp.thumbnail((115, 115))
	# mask the image so it's a circle
	mask = Image.new("L", pfp.size, 0)
	draw = ImageDraw.Draw(mask)
	draw.ellipse((0, 0, pfp.size[0], pfp.size[1]), fill=255)

	# get the tree
	tree = Image.open(f"trees/default/{treenumber}.png")
	tree.thumbnail((230, 230))

	# import some fonts
	whitneybook = ImageFont.truetype(
		'f/stuff/fonts/whitneybook.otf',
		size = 28
	)
	whitneymedium = ImageFont.truetype(
		'f/stuff/fonts/whitneymedium.otf',
		size = 38)
	consolas = ImageFont.truetype(
		'f/stuff/fonts/consolas.ttf',
		size = 30
	)
	
	# make a blank image
	img = Image.new(
		mode = "RGB",
		size = (850, 225),
		color = (32, 34, 37)
		)

	draw = ImageDraw.Draw(img)

	# add the tree
	img.paste(
		tree,
		(615, 0),
	)

	# overlay for the info
	draw.rounded_rectangle(
		xy = ((-100, 0), (632, 225)),
		fill = (32, 34, 37),
		radius = 17
	)
	
	# shorten the username
	if len(username) > 17:
		username = username[:17] + "..."
	# add the username
	draw.text(
		xy = (155, 45),
		text = f"{username}#{discrim}",
		font = whitneymedium,
		fill = (255, 255, 255)
	)
	# add the other info
	draw.text(
		xy = (155, 98),
		text = other,
		font = whitneybook,
		fill = (255, 255, 255)
	)

	# progress bar
	draw.rounded_rectangle(
		xy = ((20, 158), (610, 193)),
		fill = (79, 84, 92),
		radius = 50
	)
	# find progress width
	totalwidth = 610 - 20 # aka 100%
	progresswidth = totalwidth * progress / 100
	# round it to nearest int
	progresswidth = round(progresswidth)
	
	draw.rounded_rectangle(
		xy = ((20, 158), (progresswidth + 20, 193)),
		fill = color,
		radius = 50
	)
	
	# paste the pfp onto the blank image
	img.paste(
		pfp,
		(20, 20),
		mask=mask
	)

	# mask the image
	imgmask = Image.new("L", img.size, 0)
	draw = ImageDraw.Draw(imgmask)
	draw.rounded_rectangle(
		(0, 0, img.size[0] - 5, img.size[1]),
		fill=255,
		radius=17
	)

	# add a border to it
	border = Image.new(
		mode = "RGB",
		size = (890, 265), # + 20 on each side
		color = (47, 49, 54)
		)
	
	# paste the rounded image onto the border
	border.paste(
		img,
		(20, 20),
		mask = imgmask
	)

	bordermask = Image.new("L", border.size, 0)
	draw = ImageDraw.Draw(bordermask)
	draw.rounded_rectangle(
		(0, 0, border.size[0], border.size[1]),
		fill=255,
		radius=34
	)

	roundedimgb = border.copy()
	roundedimgb.putalpha(bordermask)

	#roundedimgb.show()

	return roundedimgb

"""
rankcard(
	pfpurl = "https://cdn.discordapp.com/avatars/722669121535475742/3021c0009e14d4765a66cd79b1c69b4c.png",
	username = "12345678901234567",
	discrim = "1989",
	other = "lvl 2 | 120/225 xp | #13",
	treenumber = 2,
	color = (88, 101, 242),
	progress = 99
)
"""