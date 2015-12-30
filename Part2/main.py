from locationParser import parseQueries
from XMLScorer import obtain_score
# Test function to parse location queries and evaluate

# Option 1: Provide file paths of xml files
# rFileName = 'inputFileName.xml'
# wFileName = 'outputFileName.xml'
# parseQueries('write',readFileName=rFileName,writeFileName=wFileName)

# Option 2: Don't provide file paths and use file dialogs to select files
(rFileName,wFileName) = parseQueries('write')


# Calculate results:
results = obtain_score(wFileName, 'GC_Test_Solved_100.xml',unsorted=True,usepaper=True)
print "Precision:", results[0]
print "Recall:", results[1]
print "F1-Score:", results[2]
