from xml.etree import ElementTree
import os

xmlInput = os.getcwd() + '/' + 'GC_Tr_100.xml'
text_file = open('xmlWHATTYPES.txt', 'w')

with open(xmlInput, 'rt') as f:
    tree = ElementTree.parse(f)
root = tree.getroot()

for qry in root.findall('WHERE'):
    if qry.text is not None:
        text_file.write(qry.text +'\n')
    else:
        text_file.write('None' +'\n')

text_file.close()

