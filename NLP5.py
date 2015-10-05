# Program: DB Pedia lookup 
# Organization: UPC FIB 
# Project: INLP laboratory project
# Authors: Andrei Polzounov, Andrei Mihai, Deividas Skiparis

# Note this script requires the installation of 
# https://pypi.python.org/pypi/SPARQLWrapper

from SPARQLWrapper import SPARQLWrapper, JSON
import sys

# This function checks if the given string has a direct resource in dbpedia database
# and returns the resource URL
def getDirectResourceUrl(locationString, database):
	database.setQuery("""SELECT DISTINCT ?Dir WHERE {?Dir rdfs:label \"""" + locationString + """\"@en; dct:subject ?x;a ?y}""")
	database.setReturnFormat(JSON)
	results = database.query().convert()
	for result in results["results"]["bindings"]:
		return result["Dir"]["value"]


#This function checks if a string is a redirection 
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
		?o = yago:Location100027167)
		}
		""")
	database.setReturnFormat(JSON)
	results = database.query().convert()

	for result in results["results"]["bindings"]:
		return result["NoOfResults"]["value"]
		
#Function to query in case a location has any disambiguates.
#If it does, the function counts all disambiguates, which have below properties.
#If a function returns >0, this means the the string is a location
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
		?types  = yago:Location100027167)
		}
		""")
	database.setReturnFormat(JSON)
	results = database.query().convert()

	for result in results["results"]["bindings"]:
		return result["countOfDisambg"]["value"]
		

userInput = raw_input("What location are you trying to check?\n")
databaseWrapper = SPARQLWrapper("http://dbpedia.org/sparql")

if len(userInput) > 1:

	locationString = userInput
	locationString = locationString.strip()
	locationString = locationString.title()
	
	resourceUrl = getDirectResourceUrl(locationString, databaseWrapper) #Check for direct resource
	print "Direct resource URL: ",
	print resourceUrl
	
	locationString = locationString.replace(" ","_")
	if resourceUrl is None:
		resourceUrl = getRedirectedResourceURL(locationString, databaseWrapper) #Check for indirect resource
		print "Redirected resource URL: ",
		print resourceUrl
		
	locationType = isLocation(resourceUrl, databaseWrapper) #Check if string is a location
	if locationType is not None: 
		if int(locationType)>0:
			print locationString + " is a location. (" + locationType + ")"
		else:
			print locationString + " is NOT a location"
	else:
		DisambCount = int(checkDisambiguates(locationString, databaseWrapper)) #Check for disambiguates
		if DisambCount>0:
			print "Disambiguates! (" + str(DisambCount) + ")\n" + locationString + " is a location."
		else:
			print "No Disambiguates"
			print locationString + " is NOT a location"
else:	
    print "Error: Enter a location"