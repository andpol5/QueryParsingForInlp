# Program: Query parser
# Organization: UPC FIB
# Project: INLP laboratory project
# Authors: Andrei Polzounov, Andrei Mihai, Deividas Skiparis

# Note this script requires the installation of
# https://pypi.python.org/pypi/SPARQLWrapper
# version used 1.7.5

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

    database.setQuery("""
    SELECT DISTINCT ?Dir fn:concat(str(?label),", ", str(?Cnto)) as ?FullName1
    fn:concat(str(?label),", ", str(?Cntp)) as ?FullName2 WHERE  {
    ?Dir rdfs:label \"""" + locationString + """\"@en;a owl:Thing;rdfs:label ?label.

    OPTIONAL{?Dir dbo:country ?CountryLink.
    ?CountryLink rdfs:label ?Cnto.
    FILTER (lang(?Cnto) = 'en')}
    OPTIONAL{?Dir dbp:country ?Cntp
    FILTER (lang(?Cntp) = 'en')}

    FILTER (lang(?label) = 'en')
    }""")

    database.setReturnFormat(JSON)
    results = database.query().convert()
    if results["results"]["bindings"].__len__()>0:
        for result in results["results"]["bindings"]:
            r1,r2,r3 = (result["Dir"]["value"],result["FullName1"]["value"],result["FullName2"]["value"])
            return (r1,resolveLabels(r2,r3))
    else:
        return (None,None)


def searchLabels(locationString, database):
    searchStart = locationString.split()[0].lower()
    searchEnd = locationString.split()[-1].lower()
    qryString = """SELECT DISTINCT ?Dir fn:concat(str(?label),", ", str(?Cnto)) as ?FullName1
    fn:concat(str(?label),", ", str(?Cntp)) as ?FullName2 WHERE  {
    ?Dir rdfs:label ?label;a ?types.
    ?label bif:xcontains \"\'""" + locationString + """\'\".

    OPTIONAL{?Dir dbo:country ?CountryLink.
    ?CountryLink rdfs:label ?Cnto.
    FILTER (lang(?Cnto) = 'en')}
    OPTIONAL{?Dir dbp:country ?Cntp
    FILTER (lang(?Cntp) = 'en')}

    FILTER (lang(?label) = 'en')
    FILTER(fn:starts-with(fn:lower-case(?label), \"""" + searchStart + """\"))
    FILTER(fn:ends-with(fn:lower-case(?label), \"""" + searchEnd + """\"))
    FILTER((fn:string-length(?label)-fn:string-length(\"""" + locationString + """\"))<4)
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
    if results["results"]["bindings"].__len__()>0:
        for result in results["results"]["bindings"]:
            r1,r2,r3 = (result["Dir"]["value"],result["FullName1"]["value"],result["FullName2"]["value"])
            return (r1,resolveLabels(r2,r3))
    else:
        return (None,None)


# This function checks if a string is a redirection
# and returns original resources URL
def getRedirectedResourceURL(locationString, database):
    # database.setQuery("""SELECT DISTINCT ?Redir WHERE {dbr:""" + locationString + """ dbo:wikiPageRedirects ?Redir}""")
    database.setQuery("""
    SELECT DISTINCT ?Dir fn:concat(str(?label),", ", str(?Cnto)) as ?FullName1
    fn:concat(str(?label),", ", str(?Cntp)) as ?FullName2 WHERE {
    dbr:""" + locationString + """ dbo:wikiPageRedirects ?Dir.
    ?Dir rdfs:label ?label.
    OPTIONAL{?Dir dbo:country ?CountryLink.
    ?CountryLink rdfs:label ?Cnto.
    FILTER (lang(?Cnto) = 'en')}
    OPTIONAL{?Dir dbp:country ?Cntp
    FILTER (lang(?Cntp) = 'en')}
    FILTER (lang(?label) = 'en')
    }""")

    database.setReturnFormat(JSON)
    results = database.query().convert()
    if results["results"]["bindings"].__len__()>0:
        for result in results["results"]["bindings"]:
            r1,r2,r3 = (result["Dir"]["value"],result["FullName1"]["value"],result["FullName2"]["value"])
            return (r1,resolveLabels(r2,r3))
    else:
        return (None,None)


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
    select DISTINCT ?Disamb as ?Dir ?P fn:concat(str(?label),", ", str(?Cnto)) as ?FullName1
    fn:concat(str(?label),", ", str(?Cntp)) as ?FullName2 where
    {dbr:""" + locationString + """ dbo:wikiPageDisambiguates ?Disamb.
    ?Disamb a ?types.
    ?Disamb dbo:populationTotal ?Pop.
    ?Disamb rdfs:label ?label.
    FILTER (lang(?label) = 'en')

    OPTIONAL{?Disamb dbo:country ?CountryLink.
    ?CountryLink rdfs:label ?Cnto.
    FILTER (lang(?Cnto) = 'en')}
    OPTIONAL{?Disamb dbp:country ?Cntp
    FILTER (lang(?Cntp) = 'en')}

    FILTER (?types = dbo:PopulatedPlace OR
        ?types  = dbo:Settlement OR
        ?types  = dbo:Town OR
        ?types  = dbo:City OR
        ?types  = dbo:Region OR
        ?types  = dbo:Country OR
        ?types  = dbo:NaturalPlace OR
        ?types  = dbo:AdministrativeRegion OR
        ?types  = umbel-rc:PopulatedPlace)

    {select xsd:float(count(distinct ?Disamb))/xsd:float(count(distinct ?Disamb2)) as ?P where
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
        ?Disamb2 a ?types2}}}}
        ORDER BY DESC(?Pop)
        LIMIT 1""")

    database.setReturnFormat(JSON)
    results = database.query().convert()
    if results["results"]["bindings"].__len__()>0:
        for result in results["results"]["bindings"]:
            r1,r2,r3,r4 = (result["Dir"]["value"],result["FullName1"]["value"],result["FullName2"]["value"],result["P"]["value"])
            return (r1,resolveLabels(r2,r3),r4)
    else:
        return (None,None,None)


def checkLocation(input):
    # Function checks if a input text is a location using functions above
    # Output: tuple of (P,Label,Type)
    # P - probability, that the string is a location
    # Label - full name of the location
    # Type - states, whether location was identified as direct link (D), redirection (R), label search (L) or
    #       disambiguate (D)


    databaseWrapper = SPARQLWrapper("http://dbpedia.org/sparql")

    if len(input) > 1:
        inputArray = input.split(';')  # allows multiple inputs separated by ';'
        for loc in inputArray:
            locationString = loc
            locationString = locationString.replace("_", " ")
            locationString = locationString.strip()
            locationString = re.sub(' +', ' ', locationString)
            locationString = locationString.title()

            resourceUrl,Label = getDirectResourceUrl(locationString, databaseWrapper)  # Check for direct resource
            lType = 'D'
            if resourceUrl is None:
                resourceUrl,Label = searchLabels(locationString, databaseWrapper)
                lType = 'L'
            if resourceUrl is None:
                locationString = locationString.replace(" ", "_")
                resourceUrl,Label = getRedirectedResourceURL(locationString, databaseWrapper)  # Check for indirect resource
                lType = 'R'
            locationType = isLocation(resourceUrl, databaseWrapper)  # Check if string is a location
            if locationType is not None:
                if int(locationType) > 0:
                    return (1,str(Label),lType)
                else:
                    return (0,None,None)
            else:
                try:
                    resourceUrl,Label,DisambScore = checkDisambiguates(locationString, databaseWrapper)  # Check for disambiguates
                    if DisambScore is not None:
                        DisambScore=float(DisambScore)
                        lType = 'B'
                except:
                    DisambScore=0 # There are no disambiguates

                if DisambScore > 0:
                    return (DisambScore,str(Label),lType) # Return the probability that the given string is a location
                else:
                    return (0,None,None)

def resolveLabels(L1,L2):
    L1=" ".join(L1.split())
    L2=" ".join(L2.split())
    if L1[-1]==',':L1 = L1[:-1]
    if L2[-1]==',':L2 = L2[:-1]

    if len(L1)>len(L2):
        return L1
    else:
        return L2

def askUser():
    userInput = raw_input("What location are you trying to check? (use ';' for multiple inputs)\n")

    if len(userInput) < 1: return
    inputArray = userInput.split(';')  # allows multiple inputs separated by ';'
    for itm in inputArray:
        locScore, loc, type=checkLocation(itm)
        if locScore>0:
            print itm + ' - YES. Prob.:' + str(locScore)
            print loc
        else:
            print itm + ' - NO'

if __name__ == '__main__':
    askUser()
