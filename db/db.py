
import json

class DB:
	def read(self) -> dict:
		"""
		Reads the json file and returns the data as a dictionary.
		
		```py
		from db.db import db
		data = db.read()
		``` """
		# read the json file!
		with open("database.json", "r") as f:
			dict_data = json.load(f)
			return dict_data
			# the type is now a dict

	# write into the json file!
	def write(self, data: dict) -> None:
		"""
		Writes the dictionary data into the json file. 
		
		```py
		from db.db import db
		data = {"hello": "world"}
		db.write(data)
		``` """
		json_data = json.dumps(data, indent=4)
		# write into the json file!
		with open("database.json", "w") as f:
			f.write(json_data)

db = DB()
