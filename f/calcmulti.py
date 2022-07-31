from f.stuff.shopitems import shopitems
# calculate multipliers

def calc_multi(equippeditems: list, xp: int):
	kill_multi = 1
	xp_multi = 1

	for item in equippeditems:
		item = shopitems[item]
		
		# add to the multipliers
		# if it doesn't exist, then it just adds 0 lol
		kill_multi += item.get("kill_multi", 0)
		xp_multi += item.get("xp_multi", 0)
	
	# you can kill more with more xp
	xp = round(xp / 1000)
	kill_multi += xp
	
	class Multipliers(object):
		def __init__(self, kill_multi: int, xp_multi: int):
			self.kill_multi = kill_multi
			self.xp_multi = xp_multi
	
	return Multipliers(kill_multi, xp_multi)
