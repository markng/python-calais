from random import choice
from xml.dom import minidom
from StringIO import StringIO
import urllib, string
from rdflib import ConjunctiveGraph as Graph
from rdflib import Namespace

CALAIS_URL="http://api.opencalais.com/enlighten/calais.asmx/Enlighten"
API_KEY = "*PUT YOUR CALAIS API KEY HERE*"
PARAMS_XML = """
<c:params xmlns:c="http://s.opencalais.com/1/pred/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"> 
<c:processingDirectives c:contentType="text/txt" c:outputFormat="xml/rdf"> 
</c:processingDirectives> 
<c:userDirectives c:allowDistribution="%s" c:allowSearch="%s" c:externalID="%s" c:submitter="%s"> 
</c:userDirectives> 
<c:externalMetadata> 
</c:externalMetadata> 
</c:params>
"""

class Calais:
	submitter = "Calais.py"
	allow_distro = "false"
	allow_search = "false" 
	things = {}
	rdfdoc = ""
	def __init__(self, submitter="Calais.py", allow_distro="false", allow_search="false"):
		self.submitter = submitter
		self.allow_distro = "false"
		self.allow_search = "false"
		self.things = {}
	
	def random_id(self): 
		chars = string.letters + string.digits
		np = ""
		for i in range(10):
			np = np + choice(chars)
		return np
	
	def analyze(self, text): 
		externalID = self.random_id()
		paramsXML = PARAMS_XML % (self.allow_distro, self.allow_search, externalID, self.submitter) 
		param = urllib.urlencode({'licenseID':API_KEY, 'content':text, 'paramsXML':paramsXML}) 
		f = urllib.urlopen(CALAIS_URL, param) 
		response = f.read() 
		dom = minidom.parseString(response) 
		self.rdfdoc = dom.childNodes[0].childNodes[0].nodeValue 
		rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#") 
		c = Namespace("http://s.opencalais.com/1/pred/") 
		g = Graph() 
		g.parse(StringIO(self.rdfdoc)) 
		for so in g.subject_objects(c["name"]):
			(hash, lit) = so
			name = lit.title()
			hash = hash.title().split("/")[-1]
			thing = {'name': name, 'hash': hash}
			self.things[hash] = thing
		for so in g.subject_objects(rdf["type"]):
			(hash, lit) = so
			hash = hash.title().split("/")[-1]
			if self.things.has_key(hash):
				self.things[hash]["type"] = lit.title().split("/")[-1]

	def print_things(self): 
		for (hash, thing) in self.things.items(): 
			print "%s :: %s (%s)" % (hash, thing["name"], thing["type"])

# Usage:
#
#calais = Calais(submitter="MyProjectID")
#calais.analyze(text)
#calais.print_things()
