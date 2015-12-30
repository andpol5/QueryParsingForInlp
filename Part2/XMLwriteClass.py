# Group 17
# @authors: Jordi Ganzer, Nil Sanz

# Representation structure of the query to be saved in XML
class Query:
	def __init__(self, queryno, query, local, what, whatType, geoRelation, where, latLong):
		# Define the 8 fields of the Query:
		self.queryno = queryno
		self.query = query
		self.local = local
		self.what = what
		self.whatType = whatType
		self.geoRelation = geoRelation
		self.where = where
		self.latLong = latLong

