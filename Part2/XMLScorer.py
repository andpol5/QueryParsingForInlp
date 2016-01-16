#This code has been developed by Daniel Duato Catalan, Luis Fabregues de los Santos and Javier Selva Castello

import xml.etree.ElementTree as ET


class Query:
    def __init__(self,query_no,query,local,query_what,query_type,geo_relation,query_where,lat_long):
        self.query_no=query_no
        self.query=query
        self.local=local
        self.query_what=query_what
        self.query_type=query_type
        self.geo_relation=geo_relation
        self.query_where=query_where
        self.lat_long=lat_long
    
    #Checks if the Query is the same Query than the other one
	#return: Boolean indicating whether the two Queries are the same or not
    def is_same_query(self,query2):
        return self.query_no==query2.query_no
    
    #Compares the Query object with the correct Query
	#return: Boolean indicating whether the Query is correct or not 
    def is_correct(self,golden):
        return (self.local==golden.local and
                ' '.join(self.query_what.lower().split())==' '.join(golden.query_what.lower().split()) and
                self.query_type==golden.query_type and self.geo_relation==golden.geo_relation and
                str(golden.query_where).lower().split(',')[0] in str(self.query_where).lower().split(',')[0])
    
    #Prints the Query object
    def show_query(self):
        print "QUERY_NO: ", self.query_no
        print "\tQUERY: ", self.query
        print "\tLOCAL: ", self.local
        print "\tQUERY_WHAT: ", self.query_what
        print "\tQUERY_TYPE: ", self.query_type
        print "\tGEO_RELATION: ", self.geo_relation
        print "\tQUERY_WHERE: ", self.query_where
        print "\tLAT_LONG: ", self.lat_long

'''
Reads a .xml file containing all the Queries and formats them as objects
@param: fileName - String containing the path and name of the .xml file to be parsed
@return: List of Query objects with the queries that were in the pared file
'''
def parser(fileName):
    # Using the xml parser from python libraries
    tree = ET.parse(fileName)
    root = tree.getroot()

    i = 0
    query_list = [] # List of query objects to be returned
    curr_query = [] # Vector containing the data of the current query
    while i < len(root):
        if i % 8 == 0 and i > 0: # Queries have 7 fields, in the 8th iteration we create a Query object
            query_list.append(Query(curr_query[0], curr_query[1], curr_query[2], curr_query[3], curr_query[4],
                                    curr_query[5], curr_query[6], curr_query[7]))
            curr_query = []
        curr_query.append(root[i].text)
        i += 1
    # Appending last query data
    query_list.append(Query(curr_query[0], curr_query[1], curr_query[2], curr_query[3], curr_query[4], curr_query[5],
                                    curr_query[6], curr_query[7]))
    return query_list

'''
Gets the precision, recall and score of a list of Query objects
@params:	to_test		- A list of Query objects containing the queries to be tested
			golden		- A list of Query objects containing the reference queries
			unsorted	- (bool) Indicates whether or not the queries in "to_test" and "golden" are sorted and if all the queries in
						  "golden" are also in "to_test"
			usepaper	- (bool) Indicates whether or not to use the paper formulas for precision and recall. If set to False
						  it will use the ACTUAL formulas for precision and recall.
@return:	precision	- (float)
			recall		- (float)
			score		- (float)
'''
def obtain_score(to_test,golden, unsorted = True, usepaper = False):
    if unsorted:
        q_num = {}
        # Arranges a dictionary from query_no -> index in the "golden" list
        for i in xrange(len(golden)):
            q_num[golden[i].query_no]=i
    
    size = len(to_test)
    correct = 0 # Amount of correctly tagged queries
    correct_local = 0 # Amount of local queries correctly tagged
    local = 0 # Total amount of local queries
    wrong_local = 0 # Amount of queries tagged wrongly as local
    for test_query, i in zip(to_test,range(size)):
        # If the current Query is correct
        if test_query.is_correct(golden[q_num[test_query.query_no] if unsorted else i]): 
            correct += 1
            if test_query.local=="True":
                correct_local += 1
        else:
            test_query.correct = False
            if test_query.local=="True":
                wrong_local += 1
                # print test_query.query
        # If the Query is local
        if golden[q_num[test_query.query_no] if unsorted else i].local == "True":
            local += 1
    
    if usepaper: # Weird formulas
        precision = correct/float(size)
        recall = correct/float(local)
    else: # Nice formulas
        precision = correct_local/float((correct_local+wrong_local))
        recall = correct_local/float(local)

    score = 2.0*precision*recall/(precision+recall)

    return precision, recall, score

if __name__ == "__main__":
    # Tester
    queries = parser('ParsedQueries.xml')
    goldens = parser('GC_Test_Golden_100.xml')
    unsorted = True
    usepaper = True

    results = obtain_score(queries, goldens, unsorted, usepaper)
    print "Precision:", results[0]
    print "Recall:", results[1]
    print "F1-Score:", results[2]
