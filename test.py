from openpyxl.reader.excel import load_workbook
from re import sub
from NLP5 import getDirectResourceUrl, databaseWrapper, getRedirectedResourceURL, isLocation, checkDisambiguates

__author__ = 'Andrei Mihai'


def isLocationBool(keyword):
    locationString = keyword
    locationString = locationString.replace("_"," ")
    locationString = sub(' +',' ',locationString) #delete double spaces between words if any
    locationString = locationString.strip()
    locationString = locationString.title()

    resourceUrl = getDirectResourceUrl(locationString, databaseWrapper)  # Check for direct resource

    #if string has "-", try lowering the case of some names after "-"
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