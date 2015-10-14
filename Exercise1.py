# Program: DB Pedia lookup 
# Organization: UPC FIB 
# Project: INLP laboratory project
# Authors: Andrei Polzounov, Andrei Mihai, Deividas Skiparis

# Note this script requires the installation of 
# https://pypi.python.org/pypi/SPARQLWrapper

from SPARQLWrapper import SPARQLWrapper, JSON			
import os
import sys
import array
import re

# This function checks if the given string has a direct resource in dbpedia database
# and returns the resource URL
def getDirectResourceUrl(locationString, database):
	#database.setQuery("""SELECT DISTINCT ?Dir WHERE {?Dir rdfs:label \"""" + locationString + """\"@en; a owl:Thing}""")
	database.setQuery("""SELECT DISTINCT ?Dir WHERE {?Dir rdfs:label \"""" + locationString + """\"@en; a owl:Thing}""")
	database.setReturnFormat(JSON)
	results = database.query().convert()
	for result in results["results"]["bindings"]:
		return result["Dir"]["value"]


# This function checks if a string is a redirection 
# and returns original resources URL
def getRedirectedResourceURL(locationString, database):
	database.setQuery("""SELECT DISTINCT ?Redir WHERE {dbr:""" + locationString + """ dbo:wikiPageRedirects ?Redir}""")
	database.setReturnFormat(JSON)
	results = database.query().convert()
	for result in results["results"]["bindings"]:
		return result["Redir"]["value"]
		

# Function to query if a given resource has one of the below properties 
# signifying that it is a location.
def isLocation(resourceUrl, database):
	if resourceUrl is None:
		return None
	database.setQuery("""
		SELECT COUNT(?o) AS ?NoOfResults
		WHERE {<""" + resourceUrl + """> a ?o
		FILTER (?o = dbo:PopulatedPlace OR
		?o = dbo:Place OR
		?o = dbo:Location OR
		?o = dbo:Settlement OR
		?o = dbo:Town OR
		?o = dbo:City OR
		?o = dbo:AdministrativeRegion OR
		?o = yago:Location100027167 OR
		?o = umbel-rc:PopulatedPlace)
		}
		""")
	database.setReturnFormat(JSON)
	results = database.query().convert()

	for result in results["results"]["bindings"]:
		return result["NoOfResults"]["value"]
		
# Function to query in case a location has any disambiguates.
# If it does, the function counts all disambiguates, which have below properties.
# If a function returns >0, this means the the string is a location
def checkDisambiguates(locationString, database):
	database.setQuery("""
		select DISTINCT Count(?Disamb) as ?countOfDisambg  where 
		{
		dbr:""" + locationString + """ dbo:wikiPageDisambiguates ?Disamb .
		?Disamb a ?types .
		FILTER (?types = dbo:PopulatedPlace OR
		?types  = dbo:Place OR
		?types  = dbo:Location OR
		?types  = dbo:Settlement OR
		?types  = dbo:Town OR
		?types  = dbo:City OR
		?types  = dbo:AdministrativeRegion OR
		?types  = yago:Location100027167 OR
		?types  = umbel-rc:PopulatedPlace)
		}
		""")
	database.setReturnFormat(JSON)
	results = database.query().convert()

	for result in results["results"]["bindings"]:
		return result["countOfDisambg"]["value"]
		

def checkLocation(input):
	#userInput = raw_input("What location are you trying to check? (use ';' for multiple inputs)\n")
	databaseWrapper = SPARQLWrapper("http://dbpedia.org/sparql")

	if len(input) > 1:

		inputArray = input.split(';') #allows multiple inputs separated by ';'
		for loc in inputArray:
			locationString = loc
			locationString = locationString.replace("_"," ")
			locationString = locationString.strip()
			locationString = re.sub(' +',' ',locationString)
			locationString = locationString.title()
			
			resourceUrl = getDirectResourceUrl(locationString, databaseWrapper) #Check for direct resource
	
			#If string has "-", try lowering the case of some names after "-"
			if resourceUrl is None and '-' in locationString:
				splitArray=locationString.split("-") #split the location into an array
				for i in range(1,len(splitArray)):
					inst=splitArray[:] #create instance
					inst[i]=inst[i].lower() #lowercase i word in the array
					locationStringMod = "-".join(inst) # rejoin array to a location
					resourceUrl = getDirectResourceUrl(locationStringMod, databaseWrapper) #Check for direct resource
					if resourceUrl is not None:
						break
						
			if resourceUrl is None:
				locationString = locationString.replace(" ","_")
				resourceUrl = getRedirectedResourceURL(locationString, databaseWrapper) #Check for indirect resource
				
			locationType = isLocation(resourceUrl, databaseWrapper) #Check if string is a location
			if locationType is not None: 
				if int(locationType)>0:
					return True
				else:
					return False
			else:
				DisambCount = int(checkDisambiguates(locationString, databaseWrapper)) #Check for disambiguates
				if DisambCount>0:
					return True
				else:
					return False

# Function that evaluates text files contained 'locs' folder.
# Script file has to be in the same directory as 'locs' folder				
def evaluation(workingDir):
	print 'Running...Please wait'
	locDir = os.listdir(workingDir+'\locs')
	ok = 0
	ko = 0
	for locFile in locDir: 
		for locInput in open(workingDir+'\locs\\'+locFile):
			try:
				locCheck=checkLocation(locInput);
				if locCheck:
					ok+=1
				else:
					ko+=1
			except:
				pass0
	print 'Done'
	print 'Locations - ',
	print ok
	print 'Not locations - ',
	print ko
	print float(ok)/(ok+ko)

evaluation(os.path.dirname(os.path.realpath(__file__)))