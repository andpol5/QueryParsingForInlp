# Program: DB Pedia lookup 
# Organization: UPC FIB 
# Project: INLP laboratory project
# Authors: Andrei Polzounov, Andrei Mihai, Deividas Skiparis

# Note this script requires the installation of 
# https://pypi.python.org/pypi/SPARQLWrapper

from SPARQLWrapper import SPARQLWrapper, JSON
import sys

# This function checks if the given string redirects to a different dbpedia page
# and returns the resource URL
def getDbPediaResourceUrl(locationString, database):
	database.setQuery("""
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
		PREFIX foaf: <http://xmlns.com/foaf/0.1/>
		PREFIX dbo: <http://dbpedia.org/ontology/>

		SELECT ?s WHERE {
		{
		?s rdfs:label \""""+ locationString.title() + """\"@en ;
		a dbo:Location

		}
		UNION
		{
		?altName rdfs:label \"""" + locationString.title() + """\"@en ;
		dbo:wikiPageRedirects ?s .
		}
		}
		""")
	database.setReturnFormat(JSON)
	results = database.query().convert()

	for result in results["results"]["bindings"]:
		return result["s"]["value"]

# Function to query if a given resource has one of the below properties 
# signifying that it is a location.
def isLocation(resourceUrl, database):
	if resourceUrl is None:
		return None
	database.setQuery("""
		PREFIX db: <""" + resourceUrl + """>
		PREFIX onto: <http://dbpedia.org/ontology/>
	
		SELECT COUNT(?o) AS ?NoOfResults
		WHERE {db: a ?o
		FILTER (?o = onto:PopulatedPlace OR
		?o = onto:Place OR
		?o = onto:Location OR
		?o = onto:Settlement OR
		?o = onto:Town OR
		?o = onto:City OR
		?o = onto:AdministrativeRegion)
		}
		""")
	database.setReturnFormat(JSON)
	results = database.query().convert()

	for result in results["results"]["bindings"]:
		return result["NoOfResults"]["value"]


userInput = raw_input("What location are you trying to check?\n")
databaseWrapper = SPARQLWrapper("http://dbpedia.org/sparql")

if len(userInput) > 1:
	locationString = userInput
	resourceUrl = getDbPediaResourceUrl(locationString, databaseWrapper)
	print resourceUrl
	locationType = isLocation(resourceUrl, databaseWrapper)
	if locationType is not None:
		if int(locationType)>0:
			print locationString + " is a location. (" + locationType + ")"
		else:
			print locationString + " is NOT a location"
	else:
		print locationString + " is NOT a location"
else:	
    print "Error: Enter a location"
