import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')

# The repository to add this issue to
REPO_OWNER = 'writeblankspace'
REPO_NAME = 'pytree'

def make_github_issue(title, body=None, labels=None):
	'''Create an issue on github.com using the given parameters.'''
	# Our url to create issues via POST
	url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues'
	# Create an authenticated session to create the issue
	session = requests.Session()
	session.auth = (USERNAME, PASSWORD)
	# Create our issue
	issue = {'title': title,
			'body': body,
			'labels': labels}
	# Add the issue to our repository
	r = session.post(url, json.dumps(issue))
	if r.status_code == 201:
		return
	else:
		raise Exception(f"""Could not create Issue {title}\n
		```{r.content}```
		""")