# import PyPeg2
from __future__ import unicode_literals
from pypeg2 import *

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
	grammar = K("describe"), restline, endl


class OptionType(Keyword):
	grammar = Enum( K("goto") )


class OptionCommand(List):
	grammar = attr("typing", OptionType), word


class NodeOption(List):
	grammar = K("option"), string, "{", endl, maybe_some(OptionCommand), "}", endl


# Global variables that can be used to track things like stats, money, etc.

class Global(List):
	grammar = K("global"), name(), "=", word, endl


# The heart of PyAdventure: the node. This is a story block. Text gets displayed on the screen and
# you can make a choice.

class Node(List):
	block = "{", endl, NodeDescription, maybe_some(NodeOption), optional(K("end")), "}", endl
	grammar = K("node"), blank, name(), block

class HomeObject(List):
	grammar = maybe_some(Global), maybe_some(Node)


# Here endeth PyPEG2 land. The rest is boilerplate for actually running the thing.

def play(results):
	name = raw_input("Enter your name, hero > ")
	print("Welcome, " + name)
	print(results)

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