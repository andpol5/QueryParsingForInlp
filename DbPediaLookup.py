# DB Pedia lookup 
# UPC FIB
# INLP Project

import urllib2
import sys

def isLocation(locationName):
    contents = urllib2.urlopen("http://lookup.dbpedia.org/api/search.asmx/KeywordSearch?QueryClass=place&QueryString=" + locationName).read()
    if "<Result>" in contents:
	    return True
    else:
        return False
		
if len(sys.argv) > 1:
    locationString = sys.argv[1]
else:	
    locationString = "Papua New Guinea"
	
print "Is \"" + locationString + "\" a location? " + str(isLocation(locationString))
