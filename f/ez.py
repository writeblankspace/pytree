import inspect
import textwrap
import random

l = inspect.cleandoc
# this helps with long strings
# will remove any local tabs


def list_tags(dictionary):
	tags = []
	for i in dictionary:
		tags.append[i]
	return tags


def wrap(string, width):
	wrapper = textwrap.TextWrapper(width=width)
	word_list = wrapper.wrap(text=string)
	return "\n".join(word_list)


def stringify(text: str):
	stripped = text.strip("""'" """)
	return f'"{stripped}"'


def randitem(items: list):
	""" returns random item from list """
	rand = random.randint(0, len(items) - 1)
	return items[rand]


def human_seconds(seconds):
	a = str(round(seconds//3600))
	b = str(round((seconds % 3600)//60))
	c = str(round((seconds % 3600) % 60))
	d = f"{a}h {b}m {c}s"
	return d
