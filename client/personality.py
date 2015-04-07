import json
import random

SAVE_FILE = 'personalityConfig.txt'
START_TOKEN = "@"
END_TOKEN = "#"
FORMAT_TOKEN = "~~"

personalityConfig = {}
responses = {}

def main():
	loadJSON = readConfigAndResponsesFromFile(SAVE_FILE)
	global personalityConfig
	global responses
	personalityConfig = loadJSON['personalityConfig']
	responses = loadJSON['responses']

	inLineDict = {
		'thisisatest' : [
			"this is definitely a test",
			"this is most certainly a test"
		]
	}

	print(renderString("@{\"dictKey\": \"thisisatest\"}#@{\"chance\": 50, \"dictKey\": \"name\", \"format\": \", ~~\", \"conditions\": [{\"key\": \"nice\", \"type\": \"and\",\"value\": \"false\"}]}#.",inLineDict))

def readConfigAndResponsesFromFile(filePath):
	with open(filePath, 'r') as content_file:
		content = content_file.read()
		content = json.loads(content)
		return content

def renderString(s,inputDict={}):

	global responses

	# check to see if there are any responses first
	if responses == None or responses == {}:
		return "I can't seem to find my personalityConfig.txt file. Either that or it's empty, which also isn't good, because then I have nothing to say. It should be in the same folder as my personality.py file."

	# if there is an inputDict, add it to the responses dictionary
	if inputDict != {}:
		responses.update(inputDict)

	#format: Textextext {[{"chance" : chance, "dictKey" : choice1, "conditions" : [condition1, condition2]},{"chance" : chance, "dictKey" : choice1, "conditions" : [condition1, condition2]}]}
	#example: Good morning {{"chance":50,"dictKey":"name","conditions":[condition1]}}.
		#condition format: {"key" : "nice", "value" : "false", "type" : "and/not"}

	#print("\nconsidering:\"" + s + "\"")
	
	rendered = ''

	lastIndex = 0
	# for each discovered index of start and end tokens, add up to the start token to the rendered string,
	# then add the rendered string inside the tokens to the rendered string,
	# then chance the last index to the index of the end token so that the rest of the string is considered
	# it keeps the recursion working properly, doing the recursion depth first
	allIndices = getStartEnds(s)
	for indices in allIndices:
		#print(indices)
		rendered = rendered + s[lastIndex:indices[0]]
		rendered = rendered + renderString(s[indices[0]+1:indices[1]])
		lastIndex = indices[1]+1

	if lastIndex < s.__len__() and allIndices.__len__()>0:
		#print(rendered + ' still has some stuff left to process at ' + (str)(lastIndex))
		rendered = rendered + renderString(s[lastIndex:])

	# found base case
	if rendered == '':
		try:
			options = json.loads('['+s+']')
		except ValueError:
			return s
		optionIndex = 0
		for option in options:
			# for each option, verify that it's valid first. Valid if there are no conditions.
			# if no chance is given, assume 100
			if option.get('chance') == None:
				option['chance'] = 100
			else:
				chance = (int)(option['chance'])

			# if there are no conditions, it's valid. Otherwise, go through and check every condition.
			# type = 'and' means that the given value must match the value in personalityConfig[key]
			# type = 'not' means that the given value must not match the value in personalityConfig[key]
			if option.get('conditions') != None:
				conditions = option['conditions']
				valid = False
				for condition in conditions:
					if condition['type'] == 'and':
						valid = personalityConfig[condition['key']] == condition['value']
					if condition['type'] == 'not':
						valid = personalityConfig[condition['key']] != condition['value']
					if valid == False:
						break
			else:
				valid = True

			if valid:
				optionIndex += 1
			else:
				# remove any invalid options
				options.__delitem__(optionIndex)

		# if there are no options after validating conditions (no options were valid), give an empty string
		if option.__len__() == 0:
			rendered = ''
		else:
			rendered = ''
			randomInt = random.randint(0,100)
			lastChance = 0
			for option in options:
				chance = (int)(option['chance']) + lastChance
				if randomInt<=chance:
					# found the key!
					# now pick a random entry from that array
					# render it if needed
					if getStartEnds(getRandomEntry(responses[option['dictKey']])).__len__ == 0:
						rendered = s
					else:
						rendered = renderString(getRandomEntry(responses[option['dictKey']]))
						if option.get('format') != None:
							format = option.get('format')
							try:
								formatTokenIndex = format.index(FORMAT_TOKEN)
								rendered = format[0:formatTokenIndex] + rendered + format[formatTokenIndex+FORMAT_TOKEN.__len__():]
							except ValueError:
								# do nothing more
								rendered = rendered
					break
				else:
					lastChance = chance

	return rendered


def getStartEnds(str, startToken=START_TOKEN, endToken=END_TOKEN):

	indices = []
	currentIndex = -1
	startIndex = -1
	endIndex = -1
	numBrackets = 0

	for char in str:
		currentIndex+=1
		if char == startToken:
			if numBrackets == 0:
				startIndex = currentIndex
			numBrackets+=1
		if char == endToken:
			numBrackets-=1
			if numBrackets == 0:
				endIndex=currentIndex
				indices.append([startIndex,endIndex])

	return indices

def getRandomEntry(objList):
	length = objList.__len__()
	return objList[random.randint(0,length-1)]

main()