from SPARQLWrapper import SPARQLWrapper, JSON
import sys

def checkAlternatives(locationString1):
	sparql = SPARQLWrapper("http://dbpedia.org/sparql")
	sparql.setQuery("""
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
		PREFIX foaf: <http://xmlns.com/foaf/0.1/>
		PREFIX dbo: <http://dbpedia.org/ontology/>

		SELECT ?s WHERE {
		{
		?s rdfs:label \""""+ locationString1.title() + """\"@en ;
		a dbo:Location

		}
		UNION
		{
		?altName rdfs:label \"""" + locationString1.title() + """\"@en ;
		dbo:wikiPageRedirects ?s .
		}
		}
		""")
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()

	for result in results["results"]["bindings"]:
		res = result["s"]["value"]
		print res
		return res



def checkLocation(locationString2):
	sparql = SPARQLWrapper("http://dbpedia.org/sparql")
	dbString = checkAlternatives(locationString2)
	if dbString is None:
		return None
	sparql.setQuery("""
		PREFIX db: <""" + dbString + """>
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
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()

	for result in results["results"]["bindings"]:
		return result["NoOfResults"]["value"]
		print result["NoOfResults"]["value"]
		

usrInput = raw_input("What location are you trying to check?\n")
if len(usrInput) > 1:
	locationString = usrInput
	fRes = checkLocation(locationString)
	if fRes is not None:
		if int(fRes)>0:
			print locationString + " is a location. (" + fRes + ")"
		else:
			print locationString + " is NOT a location"
	else:
		print locationString + " is NOT a location"
else:	
    print "Error! Enter a location"

