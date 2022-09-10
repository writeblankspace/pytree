import asyncpg
import os
import json
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
OWNERS = os.getenv('OWNERS').split(", ")

PG_USER = os.getenv('PG_USER')
PG_PW = os.getenv('PG_PW')

class Psql():
	def __init__(self):
		self.db: asyncpg.Pool = None
		self.asyncpg = asyncpg

	async def init_db(self):
		"""
		Initialize the database by creating the pools and making the tables."""
		credentials = {"user": PG_USER, "password": PG_PW, "database": "postgres", "host": "127.0.0.1"}
		self.db = await asyncpg.create_pool(**credentials)

		# guilds and users tables
		await self.db.execute(
			"""--sql
			CREATE TABLE IF NOT EXISTS guilds (
				guildid BIGINT PRIMARY KEY
			); 

			CREATE TABLE IF NOT EXISTS users (
				userid BIGINT NOT NULL,
				guildid BIGINT NOT NULL,
				PRIMARY KEY (userid, guildid)
			); """ # inventory and equipped are lists separated by commas
		)

		nb_default = "\\n".join([
			"Welcome to your new notebook! You can use this to keep track of your personal notes.\\n",
			"`/nb open` lets you open your notebook. You can edit your notes by clicking on the buttons below. You can also delete pages and add new ones.\\n",
			"`/nb quick` is for quick note-taking. All quick notes go into the first page of your notebook.\\n",
			"**Quick notes:**",
			"- try it out by typing `/nb quick`"
		])

		guilds_columns = (
			("guildid", "BIGINT", None),
			("starboardid", "BIGINT", None),
			("farmid", "BIGINT", None),
			("blight_strength", "INTEGER", 1)
		)

		users_columns = [
			("userid", "BIGINT", None),
			("guildid", "BIGINT", None),
			("xp", "INTEGER", "0"),
			("forest", "JSON", "JSON '{}'"),
			("balance", "INTEGER", "0"),
			("inventory", "TEXT", "''"),
			("equipped", "TEXT", "''"),
			("rolls", "INTEGER", "0"),
			("notebook", "JSON", "JSON '{\"data\": [\"" + nb_default + "\"]}'"),
			("planted", "INTEGER", "0")
		]

		for column in users_columns:
			await self.db.execute(
				f"""--sql
				ALTER TABLE users
				ADD COLUMN IF NOT EXISTS {column[0]} {column[1]};"""
			)
			if column[2] is not None:
				await self.db.execute(
					f"""--sql
					ALTER TABLE users
					ALTER COLUMN {column[0]} SET DEFAULT {column[2]};

					UPDATE users
					SET {column[0]} = {column[2]}
					WHERE {column[0]} IS NULL;"""
				)
		
		for column in guilds_columns:
			await self.db.execute(
				f"""--sql
				ALTER TABLE guilds
				ADD COLUMN IF NOT EXISTS {column[0]} {column[1]};"""
			)
			if column[2] is not None:
				await self.db.execute(
					f"""--sql
					ALTER TABLE guilds
					ALTER COLUMN {column[0]} SET DEFAULT {column[2]};

					UPDATE guilds
					SET {column[0]} = {column[2]}
					WHERE {column[0]} IS NULL;"""
				)

	async def check_user(self, userid, guildid):
		"""
		Makes sure the user exists in the database."""
		await self.db.execute(
			"""--sql
			INSERT INTO users (userid, guildid)
			VALUES ($1, $2)
			ON CONFLICT DO NOTHING; """,
			userid, guildid
		)
	
	async def check_guild(self, guildid):
		"""
		Makes sure the guild exists in the database."""
		await self.db.execute(
			"""--sql
			INSERT INTO guilds (guildid)
			VALUES ($1)
			ON CONFLICT DO NOTHING """,
			guildid
		)

	def json_to_dict(self, json_str) -> dict:
		"""
		Converts a json string to a dictionary."""
		return json.loads(json_str)
	
	def dict_to_json(self, dict_obj) -> str:
		"""
		Converts a dictionary to a json string."""
		return json.dumps(dict_obj)
	
	def commasplit(self, string) -> list:
		"""
		Splits a string by commas and returns a list."""
		result =  string.split(", ")
		if result == [""]:
			result = []
		return result
	
	def commasjoin(self, list_obj) -> str:
		"""
		Joins a list by commas and returns a string."""
		result = ", ".join(list_obj)
		return result

psql = Psql()