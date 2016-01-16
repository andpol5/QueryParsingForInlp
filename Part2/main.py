from locationParser import parseQueries
from XMLScorer import obtain_score,parser
# Test function to parse location queries and evaluate
rFileName = None
wFileName = None


# Option 1: Provide file paths of xml files
# rFileName = 'inputFileName.xml'
# wFileName = 'outputFileName.xml'
# parseQueries('write2file',readFileName=rFileName,writeFileName=wFileName)

# # Option 2: Don't provide file paths and instead use file dialogs to select files
# (rFileName,wFileName) = parseQueries('write2file')

# Option 3: Simply provide your own queries and only print results to terminal
queries=['alabama florist','apartments in ottawa','arizona used car lemon law']
parseQueries('terminal',inputStr=queries)



# Calculate results:
# results = obtain_score(parser('ParsedQueries.xml'), parser('GC_Test_Golden_100.xml'),unsorted=True,usepaper=True)
if wFileName == None:exit()
results = obtain_score(parser(wFileName), parser('GC_Test_Golden_100.xml'),unsorted=True,usepaper=True)
print "Precision:", results[0]
print "Recall:", results[1]
print "F1-Score:", results[2]
