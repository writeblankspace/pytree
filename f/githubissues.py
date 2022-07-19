import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('GITHUB')

# The repository to add this issue to
REPO_OWNER = 'writeblankspace'
REPO_NAME = 'pytree'

def make_github_issue(title, body=None, labels=None):
	'''Create an issue on github.com using the given parameters.'''
	headers = {"Authorization" : f"token {TOKEN}"}
	data = {
		"title": title,
		"body": body
		}

	url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues"

	requests.post(url,data=json.dumps(data),headers=headers)
