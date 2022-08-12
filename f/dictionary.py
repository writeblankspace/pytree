# for more information on how to install requests
# http://docs.python-requests.org/en/master/user/install/#install
import  requests
import json
import os
from dotenv import load_dotenv
import discord
from f.templates import theme

def search_dictionary(word: str) -> tuple:
	url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word.lower()}"
	# make a request to the dictionary api
	r = requests.get(url)
	# get the json response
	json_response = r.json()

	if type(json_response) == list:
		# if there are multiple entries, flatten the list
		flattened = {}
		flattened.update(json_response[0])

		# for the rest of the entires, add their meanings to the flattened entry
		for entry in json_response[1:]:
			for meaning in entry["meanings"]:
				flattened["meanings"].append(meaning)
		
	result = (flattened, r.status_code)

	return result

def dictionary_embed(dictionary: dict, meaning_index: int, definition_index: int) -> discord.Embed:
	word = dictionary["word"]

	# get the phonetic text
	phonetics: list = dictionary["phonetics"]
	phonetic = None
	if phonetics != None:
		# get the dict that has "text" as a key
		for i in phonetics:
			i: dict = i
			if i.get("text") != None:
				phonetic: str = i["text"]
				break
	
	# get the meaning
	meanings: list = dictionary["meanings"]
	
	meaning: dict = meanings[meaning_index]
	
	definition: str = meaning["definitions"][definition_index]["definition"]

	part_of_speech: str = meaning["partOfSpeech"]

	synonyms: list = meaning["synonyms"] + meaning["definitions"][definition_index]["synonyms"]
	antonyms: list = meaning["antonyms"] + meaning["definitions"][definition_index]["antonyms"]

	# get the unique ones
	synonyms = list(set(synonyms))
	antonyms = list(set(antonyms))

	example: str = meaning["definitions"][definition_index].get("example")

	description: str = definition

	if phonetic != None:
		description = f"`{phonetic}` {description}"
	
	embed = discord.Embed(
		title = f"[{part_of_speech}] {word}",
		description = description,
		color = theme.colours.primary
	)

	if example != None:
		embed.add_field(
			name="Example",
			value=example,
			inline=False
		)

	if len(synonyms) > 0:
		# first 10 synonyms
		synonyms = synonyms[:10]
		embed.add_field(
			name = "Synonyms",
			value = ", ".join(synonyms),
			inline = True
		)
	if len(antonyms) > 0:
		antonyms = antonyms[:10]
		embed.add_field(
			name = "Antonyms",
			value = ", ".join(antonyms),
			inline = True
		)
	
	embed.set_footer(
		text = f"definition {definition_index + 1} of {len(meaning['definitions'])}"
	)

	return embed
