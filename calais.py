from random import choice
from xml.dom import minidom
from StringIO import StringIO
import urllib, string
from rdflib import ConjunctiveGraph as Graph
from rdflib import Namespace

CALAIS_URL="http://api.opencalais.com/enlighten/calais.asmx/Enlighten"
PARAMS_XML = """
<c:params xmlns:c="http://s.opencalais.com/1/pred/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"> 
<c:processingDirectives c:contentType="%s" c:outputFormat="xml/rdf"> 
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
	api_key = ""
	def __init__(self, submitter, api_key, allow_distro="false", allow_search="false"):
		"""
		Creates a new handler for communicating with OpenCalais.  The parameter 'submitter' must contain a string, identifying your application.  'api_key' must contain a string with your OpenCalais API key (get it here: http://developer.opencalais.com/apps/register).  
		The optional parameter 'allow_distro', if set to 'true' gives OpenCalais permission to distribute the metadata extracted from your submissions.  The default value for 'allow_distro' is 'false'.  
		The optional parameter 'allow_search', if set to 'true' tells OpenCalais that future searches can be performed on the extracted metadata.  The default value for 'allow_search' is 'false'.  
		"""
		self.submitter = submitter
		self.allow_distro = "false"
		self.allow_search = "false"
		self.api_key = api_key
		self.things = {}
	
	def random_id(self):
		"""
		Creates a random 10-character ID for your submission.  
		"""
		chars = string.letters + string.digits
		np = ""
		for i in range(10):
			np = np + choice(chars)
		return np
		
	def content_id(self, text):
		"""
		Creates a SHA1 hash of the text of your submission.  
		"""
		import hashlib
		h = hashlib.sha1()
		h.update(text)
		return h.hexdigest()
	
	def analyze(self, text, content_type="text/txt"): 
		"""
		Submits 'text' to OpenCalais for analysis and memorizes the extracted metadata.  'content_type' defaults to 'text/txt'.  Set it to 'text/html' if you are submitting HTML data.  
		"""
		self.things = {}
		externalID = self.content_id(text)
		paramsXML = PARAMS_XML % (content_type, self.allow_distro, self.allow_search, externalID, self.submitter) 
		param = urllib.urlencode({'licenseID':self.api_key, 'content':text, 'paramsXML':paramsXML}) 
		f = urllib.urlopen(CALAIS_URL, param) 
		response = f.read() 
		dom = minidom.parseString(response) 
		rdfdoc = dom.childNodes[0].childNodes[0].nodeValue 
		rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#") 
		c = Namespace("http://s.opencalais.com/1/pred/") 
		g = Graph() 
		g.parse(StringIO(rdfdoc.encode('utf-8'))) 
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
		"""
		Prints the terms from the last extraction.  
		"""
		for (hash, thing) in self.things.items(): 
			print "%s :: %s (%s)" % (hash, thing["name"], thing["type"])
			
	def analyze_url(self, url):
		"""
		Downloads HTML from the given URL and submits it to OpenCalais for analysis.  
		"""
		f = urllib.urlopen(url)
		html = f.read()
		self.analyze(html, "text/html")

# Usage:
#
#calais = Calais(submitter="MyProjectID", api_key="xxyyxyxyxyyyxxyx")
#calais.analyze(text)
#calais.print_things()
