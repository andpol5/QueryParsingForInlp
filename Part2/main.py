from locationParser import parseQueries
from XMLScorer import obtain_score
# Test function to parse location queries and evaluate
rFileName = None
wFileName = None


# Option 1: Provide file paths of xml files
# rFileName = 'inputFileName.xml'
# wFileName = 'outputFileName.xml'
# parseQueries('write',readFileName=rFileName,writeFileName=wFileName)

# Option 2: Don't provide file paths and instead use file dialogs to select files
# (rFileName,wFileName) = parseQueries('write')

# Option 3: Simply provide your own queries and only print results to terminal
queries=['basketball court in petaling jaya','apartments to rent in cyprus']
parseQueries('terminal',inputStr=queries)


if wFileName == None:exit()

# Calculate results:
results = obtain_score(wFileName, 'GC_Test_Solved_100.xml',unsorted=True,usepaper=True)
print "Precision:", results[0]
print "Recall:", results[1]
print "F1-Score:", results[2]
