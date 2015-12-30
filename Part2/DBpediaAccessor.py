# Program: Query parser
# Organization: UPC FIB
# Project: INLP laboratory project
# Authors: Andrei Polzounov, Andrei Mihai, Deividas Skiparis

# Note this script requires the installation of
# https://pypi.python.org/pypi/SPARQLWrapper

from SPARQLWrapper import SPARQLWrapper, JSON
import re


# This function checks if the given string has a direct resource in dbpedia database
# and returns the probability (score) that the given string is a location,
# 1 - the string is a location
# 0 - the string is not a location
# 0<score<1 - the string has disambiguates. The score is the ratio between 'disambiguates which are location' over
# 'total number of disambiguates'

def getDirectResourceUrl(locationString, database):
    # database.setQuery("""SELECT DISTINCT ?Dir WHERE {?Dir rdfs:label \"""" + locationString + """\"@en; a owl:Thing}""")
    database.setQuery("""SELECT DISTINCT ?Dir WHERE {?Dir rdfs:label \"""" + locationString + """\"@en; a owl:Thing}""")
    database.setReturnFormat(JSON)
    results = database.query().convert()
    for result in results["results"]["bindings"]:
        return result["Dir"]["value"]


def searchLabels(locationString, database):
    searchStart = locationString.split()[0]
    searchEnd = locationString.split()[-1]
    qryString = """
    SELECT DISTINCT ?Dir WHERE {
    ?Dir rdfs:label ?label;a ?types.
    ?label bif:xcontains \"\'""" + locationString + """\'\"
    FILTER (lang(?label) = 'en')
    FILTER(fn:starts-with(?label, \"""" + searchStart + """\"))
    FILTER(fn:ends-with(?label, \"""" + searchEnd + """\"))
    FILTER((fn:string-length(?label)-fn:string-length(\"""" + locationString + """\"))<5)
    FILTER (?types = dbo:PopulatedPlace OR
		?types  = dbo:Settlement OR
		?types  = dbo:Town OR
		?types  = dbo:City OR
		?types  = dbo:Region OR
		?types  = dbo:Country OR
		?types  = dbo:NaturalPlace OR
		?types  = dbo:AdministrativeRegion OR
		?types  = umbel-rc:PopulatedPlace)
		}"""

    database.setQuery(qryString)
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
		?o = dbo:Settlement OR
		?o = dbo:Town OR
		?o = dbo:City OR
		?o = dbo:Region OR
		?o = dbo:Counrty OR
		?o = dbo:NaturalPlace OR
		?o = dbo:AdministrativeRegion OR
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
        select xsd:float(count(distinct ?Disamb))/xsd:float(count(distinct ?Disamb2)) as ?R where
        {{dbr:""" + locationString + """ dbo:wikiPageDisambiguates ?Disamb .
        ?Disamb a ?types .
        FILTER (?types = dbo:PopulatedPlace OR
        ?types  = dbo:Settlement OR
        ?types  = dbo:Town OR
        ?types  = dbo:City OR
        ?types  = dbo:Region OR
        ?types  = dbo:Country OR
        ?types  = dbo:NaturalPlace OR
        ?types  = dbo:AdministrativeRegion OR
        ?types  = umbel-rc:PopulatedPlace)}
        UNION
        {dbr:""" + locationString + """ dbo:wikiPageDisambiguates ?Disamb2 .
        ?Disamb2 a ?types2}}
        """)

    database.setReturnFormat(JSON)
    results = database.query().convert()

    for result in results["results"]["bindings"]:
        return result["R"]["value"]


def checkLocation(input):
    databaseWrapper = SPARQLWrapper("http://dbpedia.org/sparql")

    if len(input) > 1:
        inputArray = input.split(';')  # allows multiple inputs separated by ';'
        for loc in inputArray:
            locationString = loc
            locationString = locationString.replace("_", " ")
            locationString = locationString.strip()
            locationString = re.sub(' +', ' ', locationString)
            locationString = locationString.title()

            resourceUrl = getDirectResourceUrl(locationString, databaseWrapper)  # Check for direct resource

            if resourceUrl is None:
                resourceUrl = searchLabels(locationString, databaseWrapper)

            # If string has "-", try lowering the case of some names after "-"
            if resourceUrl is None and '-' in locationString:
                splitArray = locationString.split("-")  # split the location into an array
                for i in range(1, len(splitArray)):
                    inst = splitArray[:]  # create instance
                    inst[i] = inst[i].lower()  # lowercase i word in the array
                    locationStringMod = "-".join(inst)  # rejoin array to a location
                    resourceUrl = getDirectResourceUrl(locationStringMod, databaseWrapper)  # Check for direct resource
                    if resourceUrl is not None:
                        break

            if resourceUrl is None:
                locationString = locationString.replace(" ", "_")
                resourceUrl = getRedirectedResourceURL(locationString, databaseWrapper)  # Check for indirect resource

            locationType = isLocation(resourceUrl, databaseWrapper)  # Check if string is a location
            if locationType is not None:
                if int(locationType) > 0:
                    return 1
                else:
                    return 0
            else:
                try:
                    DisambScore = float(checkDisambiguates(locationString, databaseWrapper))  # Check for disambiguates
                except:
                    DisambScore=0 # There are no disambiguates

                if DisambScore > 0:
                    return DisambScore # Return the probability that the given string is a location
                else:
                    return 0

def askUser():
    userInput = raw_input("What location are you trying to check? (use ';' for multiple inputs)\n")

    if len(userInput) < 1: return
    inputArray = userInput.split(';')  # allows multiple inputs separated by ';'
    for itm in inputArray:
        locScore=checkLocation(itm)
        if locScore>0:
            print itm + ' - YES. Prob.:' + str(locScore)
        else:
            print itm + ' - NO'

if __name__ == '__main__':
    askUser()
