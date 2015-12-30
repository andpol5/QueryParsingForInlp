# Group 17
# @authors: Jordi Ganzer, Nil Sanz

from lxml import etree
import XMLwriteClass as xmlC
import os

def saveQueriesToXml(listQueries, fileName):
	'''
	This function takes a list of objects of class Query `listQueries`, and saves the xml represention in the file `fileName`
	'''

	#Create root element:
	elExampleSet = etree.Element('EXAMPLE-SET')
	for i, query in enumerate(listQueries):
		elQueryno = etree.Element('QUERYNO')
		elQueryno.text = query.queryno
		elExampleSet.append(elQueryno)

		elQuery = etree.Element('QUERY')
		elQuery.text = query.query
		elExampleSet.append(elQuery)

		elLocal = etree.Element('LOCAL')
		elLocal.text = query.local
		elExampleSet.append(elLocal)

		elWhat = etree.Element('WHAT')
		elWhat.text = query.what
		elExampleSet.append(elWhat)

		elWhatType = etree.Element('WHAT-TYPE')
		elWhatType.text = query.whatType
		elExampleSet.append(elWhatType)

		elGeoRelation = etree.Element('GEO-RELATION')
		elGeoRelation.text = query.geoRelation
		elExampleSet.append(elGeoRelation)

		elWhere = etree.Element('WHERE')
		elWhere.text = query.where
		elExampleSet.append(elWhere)

		elLatLong = etree.Element('LAT-LONG')
		elLatLong.text = query.latLong
		elExampleSet.append(elLatLong)

	strXml = etree.tostring(elExampleSet, pretty_print=True)
	text_file = open(fileName, "w")
	text_file.write(strXml)
	text_file.close()

if __name__ == '__main__':

	query1 = xmlC.Query('5004', '7 day weather welwyn garden city', 'YES', '7 day weather', 'Information', '', 'welwyn garden city', '51.80, -0.20')
	query2 = xmlC.Query('5017', '7 juniper path lanssale pa 19446', 'YES', '', 'Map', '', '7 juniper path lanssale pa 19446', '40.23, -75.30')

	listQueries = [query1, query2]
	fileName = os.path.dirname(os.path.realpath(__file__)) + '/test.xml'
	saveQueriesToXml(listQueries, fileName)
