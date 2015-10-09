from openpyxl.reader.excel import load_workbook
from NLP5 import getDirectResourceUrl, databaseWrapper, getRedirectedResourceURL, isLocation, checkDisambiguates

__author__ = 'Andrei Mihai'


def isLocationBool(keyword):
    locationString = keyword
    locationString = locationString.strip()
    locationString = locationString.title()

    locationString = locationString.replace("_"," ")
    resourceUrl = getDirectResourceUrl(locationString, databaseWrapper)  # Check for direct resource

    locationString = locationString.replace(" ", "_")
    if resourceUrl is None:
        resourceUrl = getRedirectedResourceURL(locationString, databaseWrapper)  # Check for indirect resource

    locationType = isLocation(resourceUrl, databaseWrapper)  # Check if string is a location
    if locationType is not None:
        if int(locationType) > 0:
            return True
        else:
            return False
    else:
        DisambCount = int(checkDisambiguates(locationString, databaseWrapper))  # Check for disambiguates
        if DisambCount > 0:
            return True
        else:
            return False


wb = load_workbook('Test data28092015.xlsx')

for i in range(2, 475):
    print str(i-1) + '/474'
    keyword = str(wb['Sheet1']['A' + str(i)].value)
    result = 0
    if isLocationBool(keyword):
        result = 1
    wb['Sheet1']['C' + str(i)] = result

wb.save('Test data28092015.xlsx')