
import json

class DB:
	def read(self) -> dict:
		# read the json file!
		with open("database.json", "r") as f:
			dict_data = json.load(f)
			return dict_data
			# the type is now a dict

	# write into the json file!
	def write(self, data: dict) -> None:
		json_data = json.dumps(data, indent=4)

		with open("database.json", "w") as f:
			f.write(json_data)

db = DB()
