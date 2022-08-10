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
	Searches for a word in the Oxford Dictionary and parses it."""
	def __init__(self, word: str, lang: str = default_lang):
		self.word = word
		self.lang = lang

		lemmas = self.oxford_lemmas()
		dictionary = self.oxford_dictionary()
		thesaurus = self.oxford_thesaurus()

		self.lemmas = lemmas.dict
		self.dictionary = dictionary.dict
		self.thesaurus = thesaurus.dict

		self.lemmas_code = lemmas.code
		self.dictionary_code = dictionary.code
		self.thesaurus_code = thesaurus.code

	def oxford_lemmas(self):
		word = self.word
		lang = self.lang

		word_id = word.lower()

		url = f"{main_url}/api/v2/lemmas/{lang}/{word_id}"
		r = requests.get(url, headers = {'app_id' : app_id, 'app_key' : app_key})

		# r.json to dict
		rjson: str = r.json()
		rdict: dict = json.load(rjson)

		returnstuff = object()
		returnstuff.code = r.status_code
		returnstuff.json = r.json()
		returnstuff.dict = rdict

		return returnstuff
	
	def oxford_dictionary(self):
		word = self.word
		lang = self.lang

		word_id = word.lower()

		url = f"{main_url}/api/v2/entries/{lang}/{word_id}"
		r = requests.get(url, headers = {'app_id' : app_id, 'app_key' : app_key})

		# r.json to dict
		rjson: str = r.json()
		rdict: dict = json.load(rjson)

		returnstuff = object()
		returnstuff.code = r.status_code
		returnstuff.json = r.json()
		returnstuff.dict = rdict

		return returnstuff

	def oxford_thesaurus(self):
		word = self.word
		lang = self.lang

		word_id = word.lower()
		url = f"{main_url}/api/v2/thesaurus/{lang}/{word_id}"
		r = requests.get(url, headers = {'app_id' : app_id, 'app_key' : app_key})

		# r.json to dict
		rjson: str = r.json()
		rdict: dict = json.load(rjson)

		returnstuff = object()
		returnstuff.code = r.status_code
		returnstuff.json = r.json()
		returnstuff.dict = rdict

		return returnstuff


