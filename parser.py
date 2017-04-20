# import PyPeg2
from __future__ import unicode_literals
from pypeg2 import *

# This defines a quote-encapsulated string

string = re.compile(r"\".*\"")

# We define a type as simply a word equaling either "global" or "node" as these are currently our
# two types of code objects.

class Type(Keyword):
	grammar = Enum( K("global"), K("node") )


# This defines the type of line actions that can occur within a node block

class LineType(Keyword):
	grammar = Enum( K("describe"), K("option"), K("end") )


# This is the definition of a line that occurs within a node, with instructions like describe, end, etc (aka LineType)

class NodeDescription(str):
	grammar = K("describe"), string, endl

class NodeEnd(str):
	grammar = K("end"), endl


class OptionType(Keyword):
	grammar = Enum( K("goto") )


class OptionCommand(List):
	grammar = attr("typing", OptionType), attr("arg", word)


class NodeOption(List):
	grammar = K("option"), attr("value", string), "{", endl, maybe_some(OptionCommand), "}", endl


# Global variables that can be used to track things like stats, money, etc.

class Global(List):
	grammar = K("global"), name(), "=", word, endl


# The heart of PyAdventure: the node. This is a story block. Text gets displayed on the screen and
# you can make a choice.

class Node(List):
	block = "{", endl, attr("description", NodeDescription), maybe_some(NodeOption), optional(NodeEnd), "}", endl
	grammar = K("node"), blank, name(), block

class HomeObject(List):
	grammar = maybe_some(Global), maybe_some(Node)


# Here endeth PyPEG2 land. The rest is boilerplate for actually running the thing.

currentNode = 0

def strip(string):
	return string[1:-1]

def describe(ob):
	for i in ob:
		print i.__class__.__name__ + " " + str(i)

def runNode(node):

	global currentNode

	# Print the description
	print "\n\n\n" + strip(node.description) + "\n"

	# Collect your options and check for end
	options = []
	for ob in node:
		if isinstance(ob, NodeOption):
			options.append(ob)

		if isinstance(ob, NodeEnd):
			print("\n\n\nGAME OVER\n\n\n")
			currentNode = -1
			return

	# Print options
	index = 0
	for option in options:
		index += 1
		print str(index) + ") " + strip(option.value)

	# Get user choice
	choice = -1
	while choice < 1 or choice > options.count:
		try:
			choice = int(raw_input("\n > "))
		except Exception:
			choice = -1
			print("\nThat's no answer!")

	# Process choice
	selection = options[choice - 1]
	nextNode = ""
	for command in selection:

		if isinstance(command, OptionCommand):

			# The only extant commant is goto. `command.arg` contains the tag of the appropriate node.

			if command.typing == "goto":
				nextNode = command.arg

	return nextNode


def play(results):

	global currentNode

	# name = raw_input("Enter your name, hero > ")
	# print("Welcome, " + name + "!\n\n")

	# Get a list of nodes and globals
	nodes = []
	globalVars = []

	for ob in results:
		if isinstance(ob, Global):
			globalVars.append(ob)

		if isinstance(ob, Node):
			nodes.append(ob)

	# Run the first node
	while currentNode != -1:
		next = runNode(nodes[currentNode])

		# Check to see if we're already done; if so, great!
		if currentNode == -1:
			break

		# Assume we're ending
		currentNode = -1

		# Check for a next string (returned by the `goto` command of the choice that brought us here)
		if len(next) > 0:

			# Iterate through nodes looking for a match
			next_index = 0
			for node in nodes:
				if node.name == next:
					currentNode = next_index
				next_index += 1


def parseFile(filename):
	print("Loading " + filename)
	with open(filename, 'r') as source_file:
		data = source_file.read()

		try:
			results = parse(data, HomeObject)
		except GrammarTypeError as e:
			print "GrammarTypeError: " + str(e)
		except GrammarValueError as e2:
			print "GrammarValueError" + str(e2)
		else:
			play(results)

def main():
	parseFile("adventure.fun")


main()