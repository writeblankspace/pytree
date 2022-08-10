# for more information on how to install requests
# http://docs.python-requests.org/en/master/user/install/#install
import  requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
APP_ID = os.getenv('APP_ID')
APP_KEY = os.getenv('APP_KEY')

app_id = APP_ID
app_key = APP_KEY
default_lang = 'en-gb'

main_url = "https://od-api.oxforddictionaries.com"

class Oxford_Search():
	"""
	Searches for a word in the Oxford Dictionary and parses it.
	
	`lemmas`: gives the root word of the word
	`dictionary`: gives the derivatives, etymologies, definitions, examples, etc of the word
	`thesaurus`: gives synonyms, antonyms, etc of the word"""
	def __init__(self, word: str, lang: str = default_lang):
		self.word = word
		self.lang = lang

		lemmas = self.oxford_lemmas()
		dictionary = self.oxford_dictionary()
		thesaurus = self.oxford_thesaurus()

		self.lemmas: dict = lemmas.dict 
		self.dictionary: dict = dictionary.dict
		self.thesaurus: dict = thesaurus.dict

		self.lemmas_code: int = lemmas.code
		self.dictionary_code: int = dictionary.code
		self.thesaurus_code: int = thesaurus.code

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


