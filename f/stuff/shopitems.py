shopitems = {
	# bug killers
	"bug spray": {
		"name": "bug spray",
		"description": "Spray pests (and enemies) away with this bug spray.",
		"use": "Kills 1 bug when hunting.",
		"price": 7, # you can buy it in Daiso!
		"kill_multi": 1,
		"equip": False,
	},
	"slippers": {
		"name": "slippers",
		"description": "The classic bug-slapper.",
		"use": "Kills 3 bugs when hunting.",
		"price": 15, # also from Daiso!
		"kill_multi": 3,
		"equip": False
	},
	"trainers": {
		"name": "trainers",
		"description": "The bug-stomper that also lets you run.",
		"use": "Kills 25 bugs when hunting.",
		"price": 100,
		"kill_multi": 25,
		"equip": False
	},
	"flypaper": {
		"name": "flypaper",
		"description": "Deadly sticky paper for flies.",
		"use": "Kills 5 bugs when hunting. Lasts for the entire month.",
		"price": 100,
		"kill_multi": 5,
		"equip": True
	},

	# fertilizers
	"synthetic fertilizer": {
		"name": "synthetic fertilizer",
		"description": "Manmade stuff to make plants grow healthier.",
		"use": "Gives some extra xp when chatting.",
		"price": 150,
		"xp_multi": 1,
		"equip": True
	},
	"organic fertilizer": {
		"name": "organic fertilizer",
		"description": "Natural stuff (poop) to make plants grow healthier.",
		"use": "Gives lots of extra xp when chatting.",
		"price": 200,
		"xp_multi": 5,
		"equip": True
	},

	# long-lasting products
	"python": {
		"name": "python",
		"description": "A mostly-friendly python to live in your tree.",
		"use": "Kills 25 extra bugs when hunting, and occasionally gives xp boosts when chatting. This is a lifetime product.",
		"price": 1300,
		"kill_multi": 25,
		"xp_multi": 13,
		"equip": True
	}
}