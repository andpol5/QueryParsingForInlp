from xml.etree import ElementTree
import os

xmlInput = os.getcwd() + '/' + 'ParsedQueries.xml'
text_file = open('xmlWHATTYPES.txt', 'w')

qrys=[]
locats=[]
whats=[]
whattypes=[]
geos=[]
wheres=[]

with open(xmlInput, 'rt') as f:
    tree = ElementTree.parse(f)
root = tree.getroot()

for qry in root.findall('QUERY'):

    if qry.text is not None:
        qrys.append(qry.text)
    else:
        qrys.append('')

for qry in root.findall('LOCAL'):
    if qry.text is not None:
        locats.append(qry.text)
    else:
        locats.append('False')

for qry in root.findall('WHAT'):
    if qry.text is not None:
        whats.append(qry.text)
    else:
        whats.append('')

for qry in root.findall('WHAT-TYPE'):
    if qry.text is not None:
        whattypes.append(qry.text)
    else:
        whattypes.append('')


for qry in root.findall('GEO-RELATION'):
    if qry.text is not None:
        geos.append(qry.text)
    else:
        geos.append('')

for qry in root.findall('WHERE'):
    if qry.text is not None:
        wheres.append(qry.text)
    else:
        wheres.append('')

for i,where in enumerate(wheres):
    print 'Query: ',
    print qrys[i]
    print 'Location: ',
    print locats[i]
    print 'What: ',
    print whats[i]
    print 'What type: ',
    print whattypes[i]
    print 'Geo Tag: ',
    print geos[i]
    print 'Location: ',
    print wheres[i]
    print






text_file.close()

