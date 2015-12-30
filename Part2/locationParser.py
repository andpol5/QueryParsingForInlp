import re
import sys
from Tkinter import Tk
from tkFileDialog import askopenfilename, asksaveasfilename
from xml.etree import ElementTree
import XMLwriteClass as xmlC
from XMLwrite import saveQueriesToXml
from DBpediaAccessor import checkLocation

def convertUSAstates(text, mode, convStr=None):
    # Function converts USA/Canada abbreviations to full names or vice versa in text.
    # Mode == 'abbr2str - converts abbbreviations to full names
    # Mode == 'str2abbr' converts full names to abbreviations
    # convStr specifies which full name should be abbreviated. If not given, names are searched.
    if mode == 'abb2str':
        dictionary = {'AL': 'Alabama', 'AK': 'Alaska', 'AS': 'American Samoa', 'AZ': 'Arizona', 'AR': 'Arkansas',
                      'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
                      'DC': 'DC',
                      'FL': 'Florida', 'GA': 'Georgia', 'GU': 'Guam', 'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois',
                      'IN': 'Indiana',
                      'IA': 'Iowa', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine',
                      'MD': 'Maryland',
                      'MH': 'Marshall Islands', 'MA': 'Massachusetts', 'MI': 'Michigan', 'FM': 'Micronesia',
                      'MN': 'Minnesota',
                      'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
                      'NH': 'New Hampshire',
                      'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina',
                      'ND': 'North Dakota',
                      'MP': 'Northern Marianas', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PW': 'Palau',
                      'PA': 'Pennsylvania',
                      'PR': 'Puerto Rico', 'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota',
                      'TN': 'Tennessee',
                      'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont', 'VA': 'Virginia', 'VI': 'Virgin Islands',
                      'WA': 'Washington',
                      'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming', 'NL': 'Newfoundland and Labrador',
                      'PE': 'Prince Edward Island', 'NS': 'Nova Scotia', 'NB': 'New Brunswick', 'QC': 'Quebec',
                      'ON': 'Ontario',
                      'MB': 'Manitoba', 'SK': 'Saskatchewan', 'AB': 'Alberta', 'BC': 'British Columbia', 'YT': 'Yukon',
                      'NT': 'Northwest Territories', 'NU': 'Nunavut'}
    elif mode == 'str2abb':
        dictionary = {'Alabama': 'AL', 'Alaska': 'AK', 'American Samoa': 'AS', 'Arizona': 'AZ', 'Arkansas': 'AR',
                      'California': 'CA',
                      'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'DC': 'DC',
                      'Florida': 'FL',
                      'Georgia': 'GA', 'Guam': 'GU', 'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN',
                      'Iowa': 'IA',
                      'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
                      'Marshall Islands': 'MH',
                      'Massachusetts': 'MA', 'Michigan': 'MI', 'Micronesia': 'FM', 'Minnesota': 'MN',
                      'Mississippi': 'MS',
                      'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH',
                      'New Jersey': 'NJ',
                      'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND',
                      'Northern Marianas': 'MP', 'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR', 'Palau': 'PW',
                      'Pennsylvania': 'PA',
                      'Puerto Rico': 'PR', 'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD',
                      'Tennessee': 'TN',
                      'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA', 'Virgin Islands': 'VI',
                      'Washington': 'WA',
                      'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY', 'Newfoundland and Labrador': 'NL',
                      'Prince Edward Island': 'PE', 'Nova Scotia': 'NS', 'New Brunswick': 'NB', 'Quebec': 'QC',
                      'Ontario': 'ON',
                      'Manitoba': 'MB', 'Saskatchewan': 'SK', 'Alberta': 'AB', 'British Columbia': 'BC', 'Yukon': 'YT',
                      'Northwest Territories': 'NT', 'Nunavut': 'NU'}
    else:
        return None
    changeList = []
    forbAbbr = ['in', 'me', 'or', 'on']
    if convStr is None:
        textFrom = re.findall(ur'\b[A-Z]{2}\b', " ".join(text), re.IGNORECASE)
        [textFrom.remove(i) for i in forbAbbr if i in textFrom]
    else:
        if isinstance(convStr, basestring):
            textFrom = [convStr]
        else:
            textFrom = convStr
    for n in range(0, len(text)):
        for t in textFrom:
            if mode == 'abb2str': textTo = dictionary.get(t.upper())
            if mode == 'str2abb': textTo = dictionary.get(t.title())
            if textTo is not None and text[n].find(t) > -1:
                text[n] = (" " + text[n] + " ").replace(" " + t + " ", " " + textTo + " ")
                changeList.append(textTo)

    return (text, changeList)

def getListofLocs(text):
    # This funtion given sentnece(s) in text queries to DBpedia to check if they contain location names

    # Initialize variables
    x = 0  # counter for DBpedia queries
    dbpHist = []  # A list for DBpedia query history
    listOfLocs = []
    listOfDisamb=[]
    # List of prepositions to watch out when querying
    prepos = ['at', 'in', 'to', 'of', 'on', 'for', 'from', 'off', 'upon', 'and',
              'At', 'In', 'To', 'Of', 'On', 'For', 'From', 'Off', 'Upon', 'And']

    # Check if 'text' is a list obejct
    if isinstance(text, basestring):
        sentence = [text]
    else:
        sentence = text

    # Convert USA/Canada state abbreviations to full text
    (sentence, convAbbrs) = convertUSAstates(sentence, 'abb2str')

    # Try multiple combinations of sequential words in DBpedia
    for c in range(4, 0, -1):  # c - number of words in the DBpedia query string
        flagSearch = True
        while flagSearch:
            flagSearch = False
            flagRestart = False
            for lists in range(0, len(sentence)):  # for every list in the sentence. Initially always 1
                if flagRestart: break
                try:words = sentence[lists].split()
                except:
                    continue
                if flagRestart: break

                for word in range(0, len(words), 1):  # for every word in a list
                    w1 = word
                    w2 = word + c

                    if w1 <= len(words) and w2 <= len(words):  # check if indices do not exceed dimensions
                        str1 = words[w1:w2]

                        # Define logical checks before querying DBpedia

                        # Query with <=2 words and contains a preposition
                        log1 = (any([w in str1 for w in prepos]) and c <= 2)
                        # Query already in the history list
                        log2 = (" ".join(str1) in dbpHist)
                        # Query with >2 words and contains a preposition at the start or end of query
                        log3 = (any([w in [str1[0], str1[-1]] for w in prepos]) and c >= 3)

                        if log1 or log2 or log3:  # If any is true, try other combination
                            continue

                        # Query DBpedia
                        str1 = " ".join(words[w1:w2])

                        countAttempts=1
                        while True:
                            try:
                                if countAttempts>5:raise ValueError('Connecting to DBpedia has failed.')
                                isl = checkLocation(str1)
                            except ValueError:
                                raise
                            except:
                                countAttempts+=1
                                print 'Unexpected DBpedia error. Retrying ('+str(countAttempts)+' of 5)...'
                                continue
                            break


                        # Append search string to history
                        dbpHist.append(str1)

                        if isl==1: # Query is a 100% location
                            for cnt,item in enumerate(sentence):
                                try: # Find location string in the sentence
                                    str2=re.findall(r'\b(?:the)?\W?\b(?:'+str1+r')\b', item,flags=re.IGNORECASE)
                                except:
                                    continue
                                if len(str2)>0: # Remove the location from the sentence
                                    sentence[cnt]= re.split(r'\b(?:the)?\W?\b(?:'+str1+r')\b', item,flags=re.IGNORECASE)

                                    # Clean up sentence and append results
                                    sentence=list(flatten_all(sentence))
                                    sentence=list(cleanUpList(sentence))
                                    listOfLocs.append(str2[0])
                                    # Set flags
                                    flagRestart = True
                                    flagSearch = True

                        elif 0.5<isl<1: # Confidence of 0.5 is required to consider a disambiguate a location
                            listOfDisamb.append((str1,isl))
                            flagRestart = True
                            flagSearch = True
                            break

    # If a definite location has not been found and there are disambiguates...
    if len(listOfLocs)==0 and len(listOfDisamb)>0:
        # Sort disambiguates by descending confidence and treat the highest score as the only location
        listOfDisamb=sorted(listOfDisamb,key=lambda item:item[1],reverse=True)[0][0]
        # Remove the location from the sentence
        for scnt,sitem in enumerate(sentence):
            str3=re.findall(r'\b(?:the)?\W?\b(?:'+listOfDisamb+r')\b', sitem,flags=re.IGNORECASE)
            if len(str3)>0:
                sentence[scnt]= re.split(r'\b(?:the)?\W?\b(?:'+listOfDisamb+r')\b', sitem,flags=re.IGNORECASE)
                sentence=list(flatten_all(sentence))
                sentence=list(cleanUpList(sentence))
                listOfLocs.append(str3[0])

    # If there were conversions of USA states made, convert back to abbreviations
    if len(convAbbrs) > 0:
        listOfLocs = convertUSAstates(listOfLocs, 'str2abb', convStr=convAbbrs)[0]

    # Return
    return listOfLocs


def flatten_all(iterable):
    for elem in iterable:
        if not isinstance(elem, list):
            yield elem
        else:
            for x in flatten_all(elem):
                yield x

def cleanUpList(inputList):
    for i in inputList:
        if not (i=='' or i==' ' or i==' ' or i=='  '):
            yield i


def findGeoTags(strings,avoidList=[]):
    # This function finds and removes geo tags from text

    if isinstance(avoidList, basestring):
        raise('avoidList must be a list')

    lastCheck=['Final']
    mainDict={'searchString': [],'geoTags': [],'splitStr': [],'avoidList': []}

    # Compile regular expression objects
    reOb1 = re.compile(r"\W?\b(?:in|at|near|from|to)+\b\W?"
                       r"\b(?:the)?\b\W?"
                       r"\b(?:south|west|north|east|near|next)\W?\b(?:south|west|north|east|near|next)?\b\W?"
                       r"\b(?:of|to|from)?\b", re.IGNORECASE)
    reOb2 = re.compile(r"\W?\b(?:in|at|near|from|to)?\b\W?"
                       r"\b(?:the)?\b\W?"
                       r"\b(?:south|west|north|east|near|next)\W?\b(?:south|west|north|east|near|next)?\b\W?"
                       r"\b(?:of|to|from)+\b", re.IGNORECASE)
    reOb31 = re.compile(r"\W?\b(?:in|at|near|from|to)?\b\W?"
                       r"\b(?:the)?\b\W?"
                       r"\b(?:southeast|southwest|northeast|northwest)+\b\W?"
                       r"\b(?:of|to|from)+\b", re.IGNORECASE)
    reOb32 = re.compile(r"\W?\b(?:in|at|near|from|to)+\b\W?"
                       r"\b(?:the)?\b\W?"
                       r"\b(?:southeast|southwest|northeast|northwest)+\b\W?"
                       r"\b(?:of|to|from)?\b", re.IGNORECASE)
    reOb4 = re.compile(r"\b(?:along)\W?(?:the){0}\b", re.IGNORECASE)
    reOb5 = re.compile(r"\b(?:within)\W+(?:[0-9]+)\W?(?:miles|m|kilometers|km)\b\W+\b(?:of|to|from)\b", re.IGNORECASE)
    reOb6 = re.compile(r"\b(?:in)\W+(?:or|and)\W+(?:around)\b", re.IGNORECASE)
    reOb7 = re.compile(r"\b(?:within)\W+", re.IGNORECASE)


    for string in strings:
        # Match geo tags in the given text
        geoMatch1 = reOb1.findall(string)
        geoMatch2 = reOb2.findall(string)
        geoMatch31 = reOb31.findall(string)
        geoMatch32 = reOb32.findall(string)
        geoMatch4 = reOb4.findall(string)
        geoMatch5 = reOb5.findall(string)
        geoMatch6 = reOb6.findall(string)
        geoMatch7 = reOb7.findall(string)

        splitStr = None
        geoTag = None
        # Remove geo tags from text
        if len(geoMatch1) > 0 and 'geoMatch1' not in avoidList:
            geoTag = geoMatch1
            splitStr = string.split(geoTag[0])
            lastCheck=['geoMatch1']

        if len(geoMatch2) > 0 and 'geoMatch2' not in avoidList:
            geoTag = geoMatch2
            splitStr = string.split(geoTag[0])
            lastCheck=['geoMatch2']

        if len(geoMatch4) > 0 and 'geoMatch4' not in avoidList:
            geoTag = geoMatch4
            splitStr = string.split(geoTag[0])
            lastCheck=['geoMatch4']

        if len(geoMatch5) > 0 and 'geoMatch5' not in avoidList:
            geoTag = geoMatch5
            splitStr = string.split(geoTag[0])
            lastCheck=['geoMatch5']

        if len(geoMatch6) > 0 and 'geoMatch6' not in avoidList:
            geoTag = geoMatch6
            splitStr = string.split(geoTag[0])
            lastCheck=['geoMatch6']

        if len(geoMatch7) > 0 and 'geoMatch7' not in avoidList:
            geoTag = geoMatch7
            splitStr = string.split(geoTag[0])
            lastCheck=['geoMatch7']

        if splitStr is None and len(geoMatch31) > 0  and 'geoMatch31' not in avoidList:
            geoTag = geoMatch31
            splitStr = string.split(geoTag[0])
            lastCheck=['geoMatch31']

        if splitStr is None and len(geoMatch32) > 0  and 'geoMatch32' not in avoidList:
            geoTag = geoMatch32
            splitStr = string.split(geoTag[0])
            lastCheck=['geoMatch32']

        if splitStr is None and 'singles' not in avoidList:
            geoTag = re.findall(r'\b(?:in|at|near|from|to|near|on|of)\b', string,flags=re.IGNORECASE)
            splitStr = re.split(r'\b(?:in|at|near|from|to|near|on|of)\b', string,re.IGNORECASE)
            if len(geoTag)>0:
                lastCheck=['singles']
        # Write results to output file
        mainDict['searchString']+=[string]
        mainDict['geoTags']+=geoTag
        mainDict['splitStr']+=splitStr
        mainDict['avoidList']+=lastCheck

    # Return the output file
    return mainDict


def parseLocations(text, listOfLocs, geoTags):
    # This function uses information about locations in text to match them with theit geo tags
    # (if any) and remove from text

    # Match geoTags with locations and remove from text
    flagRestart = True
    fullLocList = []
    fullGeoList = []
    while flagRestart:
        flagRestart = False
        for t in range(0, len(text)):
            if flagRestart: break
            for loc in listOfLocs:
                if flagRestart: break
                for geoTag in geoTags:
                    testStr = " ".join(" ".join([geoTag, loc]).split())
                    doMatch = re.findall(testStr, text[t], re.IGNORECASE)
                    if len(doMatch) > 0:
                        text[t] = text[t].split(doMatch[0])
                        fullLocList.append(loc)
                        fullGeoList.append(geoTag.strip())
                        listOfLocs.remove(loc)
                        geoTags.remove(geoTag)
                        flagRestart = True
                        text = list(flatten_all(text))
                        break

    # Remove all locations from text without geo tags
    while len(listOfLocs) > 0:
        flagRestart = True
        while flagRestart:
            flagRestart = False
            for t in range(0, len(text)):
                if flagRestart: break
                for loc in listOfLocs:
                    testStr = " ".join(" ".join([loc]).split())
                    doMatch = re.findall(r'\b' + testStr + r'\b', text[t], flags=re.IGNORECASE)
                    if len(doMatch) > 0:
                        text[t] = re.split(r'\b' + testStr + r'\b', text[t], flags=re.IGNORECASE)
                        # text[t] = text[t].split(doMatch[0])
                        listOfLocs.remove(loc)
                        flagRestart = True
                        text = list(flatten_all(text))
                        fullLocList.append(doMatch[0])
                        break

    text=list(cleanUpList(text))
    if len(text)>0:
        whatTag = [" ".join(" ".join(text).split())]
    else:
        whatTag=[]
    return (fullLocList, fullGeoList, whatTag)

def getGeoTagLabel(geoTags):

    # From provided geoTags, returns the appropriate class labels to append to XML

    geoCat=[]
    if len(geoTags)==0:
        geoCat=None

    for gItem in geoTags:
        # If geo tags is a single word, this word is a class name
        if len(gItem.split())==1: #only 1 word
            geoCat.append(gItem.upper())
            continue
        # If geo tags contains more words,

        reOb = re.compile(r"\b(?:south|west|north|east)\W?(?:west|east)?\b\W?\b(?:of|to)+\b", re.IGNORECASE)
        geoMatch=reOb.findall(gItem)
        if len(geoMatch)>0:
            geoCat.append(geoMatch[0].upper())
            continue

        reOb = re.compile(r"\b(?:to)+\b\W?(?:the)?\W?\b(?:south|west|north|east)\W?(?:west|east)?\b\W?\b", re.IGNORECASE)
        geoMatch=reOb.findall(gItem)
        if len(geoMatch)>0:
            geoCat.append((re.findall(r"\b(?:south|west|north|east)\W?(?:west|east)?\b",gItem,re.IGNORECASE)[0]).upper()+' TO')
            continue

        reOb = re.compile(r"\b(?:of|in)+\b\W?(?:the)?\W?\b(?:south|west|north|east)\W?(?:west|east)?\b\W?\b", re.IGNORECASE)
        geoMatch=reOb.findall(gItem)
        if len(geoMatch)>0:
            geoCat.append((re.findall(r"\b(?:south|west|north|east)\W?(?:west|east)?\b",gItem,re.IGNORECASE)[0]).upper()+' OF')
            continue

        reOb=re.compile(r"\b(?:in)\W+(?:or|and)\W+(?:around)\b", re.IGNORECASE)
        geoMatch=reOb.findall(gItem)
        if len(geoMatch)>0:
            geoCat.append('IN_NEAR')
            continue

        reOb=re.compile(r"\b(?:near|next)\W+(?:to)?\b", re.IGNORECASE)
        geoMatch=reOb.findall(gItem)
        if len(geoMatch)>0:
            geoCat.append('NEAR')
            continue

        reOb=re.compile(r"\b(?:within)\W+(?:[0-9]+)\W?(?:miles|m|kilometers|km)\b\W+\b(?:of|to|from)\b", re.IGNORECASE)
        geoMatch=reOb.findall(gItem)
        if len(geoMatch)>0:
            geoCat.append('DISTANCE')
            continue

        geoCat.append('UNDEFINED')
    return geoCat

def getWhatLabel(whatTag):
    #Parses the What string and identifies its label

    outputList=[]
    # Define possible abbreviations for streets and roads
    streetAbbrs=open('streetAbbrs.txt').read()

    categoriesYP=open('categoriesYP.txt').read()

    # If what tag is empty string, whole full string represents a location
    if len(whatTag)==0:
        outputList.append('Map')
        return outputList


    for wlist in whatTag:
        # Firstly check if a WHAT is a possible street name
        streetTypeMatch = re.findall(r'.+\b('+streetAbbrs+r')\b\W?$', wlist,flags=re.IGNORECASE)
        if len(streetTypeMatch)>0:
            outputList.append('Map')
            return outputList

    for wlist in whatTag:
        # If not, check if WHAT is a possible Yellow page
        for wword in wlist.split():
            wMatch=re.findall(r'^\b(?:'+wword+r')s?\b$',categoriesYP,flags=re.I|re.M)
            if len(wMatch)>0:
                outputList.append('Yellow page')
                return outputList

    # It's not a map and not Yellow page. Thus, it is Information
    outputList.append('Information')
    return outputList


def defineFileName(mode):
    # Function to call file dialogs for file selection
    # mode= 'read' to open file
    #       'write' to save file

    Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing

    if mode == 'read':
        fileName = askopenfilename(filetypes=[("XML files", "*.xml")], title='Select input XML file',
                                   multiple=False, defaultextension=".txt")
    elif mode == 'write':
        fileName = asksaveasfilename(filetypes=[("XML files", "*.xml")], title='Enter name for saving XML file',
                                     confirmoverwrite=True, defaultextension=".xml")
    else:
        fileName = None

    return fileName


def readXMLfile(XMLfileName):
    # Read the XML file
    listOfQueries = []
    listOfQryNumbers = []

    with open(XMLfileName, 'rt') as f:
        tree = ElementTree.parse(f)
    root = tree.getroot()

    for qry in root.findall('QUERY'):
        if qry.text is not None:
            listOfQueries.append(qry.text)

    for num in root.findall('QUERYNO'):
        if num is not None:
            listOfQryNumbers.append(num.text)

    return (listOfQueries, listOfQryNumbers)

def parseQueries(mode='terminal',readFileName=None,writeFileName=None,inputStr=None):

    if mode=='terminal':
        writeFile = None
    elif mode=='write2file':
        if writeFileName is None:
            writeFile = open(defineFileName('write'), 'w')  # Output text file
        else:
            writeFile = open(unicode(writeFileName),'w')
    else:
        raise('"mode" must be a string either "terminal" or "write2file".')

    if readFileName is None and inputStr is None:
        readFile = open(defineFileName('read'))
    elif readFileName is not None:
        readFile = open(unicode(readFileName))
    else:
        readFile = None

    if readFile is not None:
        if not readFile.name.lower().endswith('.xml'):
            raise('Read and Write files must be .xml')

    if writeFile is not None:
        if not writeFile.name.lower().endswith('.xml'):
            raise('Read and Write files must be .xml')


    # Initialize file names
    XMLReady = []

    # Read XML file
    if readFile is not None:
        (allText, qryNumbers) = readXMLfile(readFile.name)
    else:
        allText = inputStr
        qryNumbers = None

    if isinstance(allText, basestring):
        allText = allText.split(';')

    for qNum, text in enumerate(allText, 0):

        origText = text
        # Clean up the text
        if text.isupper(): text = text.lower()
        text = text.replace('\n', '')
        text = text.replace(',', '')
        text = text.replace('.', '')
        text = text.replace(';', '')
        text = text.replace(':', '')
        text = " ".join(text.split())
        text = [text]

        print 'Checking ',
        print qNum + 1,
        print ' of ',
        print len(allText),
        print ': ',
        print origText

        noCheckList=[]
        while True:
            geoTags = findGeoTags(text,noCheckList)
            listOfLocs = getListofLocs(geoTags['splitStr'])
            if len(listOfLocs) > 0 or 'final' in geoTags['avoidList']:
                break
            noCheckList=geoTags['avoidList']

        if len(listOfLocs) > 0:
            decisionLOC = "YES"
            fullLocList, fullGeoList, whatTag = parseLocations(text, listOfLocs, geoTags['geoTags'])
            fullGeoLabels=getGeoTagLabel(fullGeoList)
            fullWhatLabels=getWhatLabel(whatTag)

            if fullWhatLabels==['Map']:
                writeWHAT = None
                writeLOC = origText
                writeGEO=None
            else:
                writeWHAT = ",".join(whatTag)
                writeLOC = ",".join(fullLocList)
                if fullGeoLabels is not None:
                    writeGEO = ",".join(fullGeoLabels)
                else:
                    writeGEO=None

            if len(fullWhatLabels)>0:
                writeWHATTYPE= fullWhatLabels[0]
            else:
                writeWHATTYPE=None

        else:
            decisionLOC = "NO"
            writeWHAT = None
            writeWHATTYPE = None
            writeGEO = None
            writeLOC = None

        if not qryNumbers is None:
            writeQNo = qryNumbers[qNum]
        else:
            writeQNo = None

        XMLReady.append(xmlC.Query(
            writeQNo,
            origText,
            decisionLOC,
            writeWHAT,
            writeWHATTYPE,
            writeGEO,
            writeLOC,
            ''))

        print 'Location: ' + str(decisionLOC)
        print 'What: ' + str(writeWHAT)
        print 'What type: ' + str(writeWHATTYPE)
        print 'Geo Tag: ' + str(writeGEO)
        print 'Location: ' + str(writeLOC)
        print


    if writeFile is not None:
        saveQueriesToXml(XMLReady, writeFile.name)
        writeFile.close()
        outW = writeFile.name
    else:
        outW = None
    if readFile is not None:
        readFile.close()
        outR = readFile.name
    else:
        outR = None

    return (outR,outW)


if __name__ == '__main__':

    s1=['best resorts in mexico']

    parseQueries('terminal',inputStr=s1)
