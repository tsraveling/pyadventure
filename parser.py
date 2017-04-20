#
# PyAdventure; a simple game engine using PyPEG 2
# Built in 2017 Tim Raveling
# Use and abuse if you please
# Attribute if you want to tickle my ego or whatevs ;)


# For whatever reason you need this in order to be able to process operators like =
from __future__ import unicode_literals

# import PyPeg2
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


# An `end` in a node informs the engine that we've reached game over. Any choices that exist in the node block will be ignored.

class NodeEnd(str):
	grammar = K("end"), endl


# We may in future add other commands (score increments maybe, ways to use the globals). For now there's only one option command, `goto`.

class OptionType(Keyword):
	grammar = Enum( K("goto") )


# Every command currently consists of a type and an argument, in this case e.g. `goto mall`

class OptionCommand(List):
	grammar = attr("typing", OptionType), attr("arg", word)


# An option consist of declaration, string value, and execution block, eg `option "Go home" { goto home }`

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


#
# Here endeth PyPEG2 land. The rest is boilerplate for actually running the thing.
#


# This variable will track which node we are on.
currentNode = 0


# This function strips closing quotes off of the strings PyPEG2 returns via the regex `string` at the top of this file.
def strip(string):
	return string[1:-1]


# This is a debug function that will return the objects contained in a given object
def describe(ob):
	for i in ob:
		print i.__class__.__name__ + " " + str(i)


# This is the main driver of the engine. It processes an entire node, including user input.
def runNode(node):

	global currentNode

	# Print the description
	print "\n\n" + strip(node.description) + "\n"

	# Collect your options and check for end
	options = []
	for ob in node:

		# IF we find a NodeOption object add it to our array.
		if isinstance(ob, NodeOption):
			options.append(ob)

		# If we find a NodeEnd object we're at the end of the line. Game over, man, game over!
		if isinstance(ob, NodeEnd):
			print("\nGAME OVER\n\n\n")
			currentNode = -1
			return

	# Print options
	index = 0
	for option in options:
		index += 1
		print str(index) + ") " + strip(option.value)

	# Get user choice. Make sure that it's a) an int and b) within the range of our option array.
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

		# Make sure the object is a standard command. We may in future want support for eg operators on variables.
		if isinstance(command, OptionCommand):

			# The only extant commant is goto. `command.arg` contains the tag of the appropriate node.

			if command.typing == "goto":
				nextNode = command.arg

	# Note that you can only go to one node for a given choice.
	return nextNode


# This function plays the game given the results of an entire *.fun file.
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


# This does the work of actually loading in the file and parsing it using PyPEG2.
def parseFile(filename):

	# Read the data
	with open(filename, 'r') as source_file:
		data = source_file.read()

		# Attempt to parse it, or throw errors
		try:
			results = parse(data, HomeObject)
		except GrammarTypeError as e:
			print "GrammarTypeError: " + str(e)
		except GrammarValueError as e2:
			print "GrammarValueError" + str(e2)
		else:
			play(results)

# For all y'all C fans in the house
def main():
	parseFile("adventure.fun")

# Run this puppy
main()