
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
	
	def exists(self, to_key: list, create: bool = False) -> bool:
		"""
		Sees if the key exists.

		`to_key` is the path to go to the key, eg `["path", "to", "key"]`

		`create` is whether or not to create the key if it doesn't exist. The value becomes `None`.
		
		Returns a `bool` of whether the key exists or not. """

		unchangeddata = self.read()
		data = unchangeddata
		for i in range(len(to_key)):
			current = to_key[i]
			if to_key[i] not in data:
				if create and i < len(to_key) - 1:
					# not the last key, so create it
					data[to_key[i]] = {}
				elif create:
					# last key, so create it with a value of None
					data[to_key[i]] = None
				else:
					# we don't want to create it, and it doesn't exist
					return False
			# move forward through the dict
			data = data[to_key[i]]
		self.write(unchangeddata)
		return True 

db = DB()
