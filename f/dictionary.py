# for more information on how to install requests
# http://docs.python-requests.org/en/master/user/install/#install
import  requests
import json
import os
from dotenv import load_dotenv
import discord

load_dotenv()
APP_ID = os.getenv('APP_ID')
APP_KEY = os.getenv('APP_KEY')

app_id = APP_ID
app_key = APP_KEY
default_lang = 'en-gb'

main_url = "https://od-api.oxforddictionaries.com"

class Oxford_Search_Lemmas():
	"""
	Searches for a word's lemmas."""
	def __init__(self, word: str, lang: str = default_lang):
		self.word = word
		self.lang = lang

		lemmas = self.oxford_lemmas()

		self.lemmas: dict = lemmas.dict 

		self.lemmas_code: int = lemmas.code

	def oxford_lemmas(self):
		word = self.word
		lang = self.lang

		word_id = word.lower()

		url = f"{main_url}/api/v2/lemmas/{lang}/{word_id}"
		r = requests.get(url, headers = {'app_id' : app_id, 'app_key' : app_key})

		# r.json to dict
		rjson = r.json()
		# rdict: dict = json.load(rjson)

		class Returnstuff():
			def __init__(self):
				self.code = r.status_code
				self.json = r.json()
				self.dict = rjson

		return Returnstuff()

class Oxford_Search():
	"""
	Searches for a word in the Oxford Dictionary and parses it.
	
	`lemmas`: gives the root word of the word
	`dictionary`: gives the derivatives, etymologies, definitions, examples, etc of the word
	`thesaurus`: gives synonyms, antonyms, etc of the word"""
	def __init__(self, word: str, lang: str = default_lang):
		self.word = word
		self.lang = lang

		dictionary = self.oxford_dictionary()
		thesaurus = self.oxford_thesaurus()

		self.dictionary: dict = dictionary.dict
		self.thesaurus: dict = thesaurus.dict

		self.dictionary_code: int = dictionary.code
		self.thesaurus_code: int = thesaurus.code
	
	def oxford_dictionary(self):
		word = self.word
		lang = self.lang

		word_id = word.lower()

		url = f"{main_url}/api/v2/entries/{lang}/{word_id}"
		r = requests.get(url, headers = {'app_id' : app_id, 'app_key' : app_key})

		# r.json to dict
		rjson = r.json()
		# rdict: dict = json.load(rjson)

		class Returnstuff():
			def __init__(self):
				self.code = r.status_code
				self.json = r.json()
				self.dict = rjson

		return Returnstuff()

	def oxford_thesaurus(self):
		word = self.word
		lang = self.lang

		word_id = word.lower()
		url = f"{main_url}/api/v2/thesaurus/{lang}/{word_id}"
		r = requests.get(url, headers = {'app_id' : app_id, 'app_key' : app_key})

		# r.json to dict
		rjson = r.json()
		# rdict: dict = json.load(rjson)

		class Returnstuff():
			def __init__(self):
				self.code = r.status_code
				self.json = r.json()
				self.dict = rjson

		return Returnstuff()

def dictionary_embed(word: str, lexicalCategory: str, entry: dict, index: int) -> discord.Embed:
	sense = entry["senses"][index]

	# definition
	definition: str = f"Definition: {sense['definitions'][0]}"
	# grammatical features
	grammaticalFeatures = entry.get("grammaticalFeatures")
	if grammaticalFeatures is not None and len(grammaticalFeatures) > 0:
		grammaticalFeatures_str = []
		for feature in grammaticalFeatures:
			grammaticalFeatures_str.append(f"[{feature['text'].lower()}]")
		grammaticalFeatures_str = " " + ' '.join(grammaticalFeatures_str)
	else:
		grammaticalFeatures_str = ""
	# how to pronounce
	pronunciations = entry.get("pronunciations")
	if pronunciations is not None and len(pronunciations) > 0:
		pronunciation = f"Pronunciation: {pronunciations[0]['phoneticSpelling']}" + "\n"
	else:
		pronunciation = ""
	# registers
	registers = sense.get("registers")
	if registers is not None and len(registers) > 0:
		registers_str = []
		for register in registers:
			registers_str.append(f"[{register['text'].lower()}]")
		registers_str = " " + ' '.join(registers_str)
	else:
		registers_str = ""


	embed = discord.Embed(
		title = f"{word} [{lexicalCategory}]" + grammaticalFeatures_str + registers_str,
		description = pronunciation + definition
	)
	
	examples = sense.get("examples")
	if examples is not None and len(examples) > 0:
		example_str = []
		for example in examples:
			example_str.append(f"- {example['text']}")
		# get the first three only
		example_str = example_str[:3]
		example_str = '\n'.join(example_str)

		if example_str != "":
			embed.add_field(
				name="Examples",
				value=example_str,
				inline=True
			)
	
	synonyms = sense.get("synonyms")
	if synonyms is not None and len(synonyms) > 0:
		synonyms_str = []
		for synonym in synonyms:
			synonyms_str.append(synonym["text"])
		# only get the first nine
		synonyms_str = synonyms_str[:9]
		synonyms_str = ', '.join(synonyms_str)

		if synonyms_str != "":
			embed.add_field(
				name="Synonyms",
				value=synonyms_str,
				inline=True
			)
		
	subsenses: list = sense.get("subsenses")
	if subsenses is not None and len(subsenses) > 0:
		subsenses_str = []
		for subsense in subsenses:
			if subsense.get("definitions") is not None:
				subsenses_str.append(f"- {subsense['definitions'][0]}")
		subsenses_str = '\n'.join(subsenses_str)

		if subsenses_str != "":
			embed.add_field(
				name="Other senses of the word",
				value=subsenses_str,
				inline=False
			)
	
	etymology = entry.get("etymologies")
	if etymology is not None:
		if etymology[0] != "":
			embed.add_field(
				name="Etymology",
				value=etymology[0],
				inline=False
			)
	
	embed.set_footer(
		text=f"sense {index + 1} of {len(entry['senses'])}"
	)

	return embed
