"""
python-calais v.1.0 -- Python interface to the OpenCalais API
Author: Jordan Dimov (jdimov@mlke.net)
Last-Update: 01/09/2009
"""

import httplib, urllib
import simplejson as json
from StringIO import StringIO

PARAMS_XML = """
<c:params xmlns:c="http://s.opencalais.com/1/pred/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"> <c:processingDirectives %s> </c:processingDirectives> <c:userDirectives %s> </c:userDirectives> <c:externalMetadata %s> </c:externalMetadata> </c:params>
"""

__version__ = "1.0"

class Calais():
    api_key = None
    processing_directives = {"contentType":"TEXT/RAW", "outputFormat":"application/json", "reltagBaseURL":None, "calculateRelevanceScore":"true", "enableMetadataType":None, "discardMetadata":None, "omitOutputtingOriginalText":"true"}
    user_directives = {"allowDistribution":"false", "allowSearch":"false", "externalID":None}
    external_metadata = {}
    _last_doc = None
    _last_result = None

    def __init__(self, api_key, submitter="python-calais client v.%s" % __version__):
        self.api_key = api_key
        self.user_directives["submitter"]=submitter

    def _get_params_XML(self):
        return PARAMS_XML % (" ".join('c:%s="%s"' % (k,v) for (k,v) in self.processing_directives.items() if v), " ".join('c:%s="%s"' % (k,v) for (k,v) in self.user_directives.items() if v), " ".join('c:%s="%s"' % (k,v) for (k,v) in self.external_metadata.items() if v))

    def rest_POST(self, content):
        params = urllib.urlencode({'licenseID':self.api_key, 'content':content, 'paramsXML':self._get_params_XML()})
        headers = {"Content-type":"application/x-www-form-urlencoded"}
        conn = httplib.HTTPConnection("api.opencalais.com:80")
        conn.request("POST", "/enlighten/rest/", params, headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        return (data)

    def get_random_id(self):
        """
        Creates a random 10-character ID for your submission.  
        """
        import string
        from random import choice
        chars = string.letters + string.digits
        np = ""
        for i in range(10):
            np = np + choice(chars)
        return np

    def get_content_id(self, text):
        """
        Creates a SHA1 hash of the text of your submission.  
        """
        import hashlib
        h = hashlib.sha1()
        h.update(text)
        return h.hexdigest()

    def analyze(self, content, content_type="TEXT/RAW", external_id=None):
        self.processing_directives["contentType"]=content_type
        if external_id:
            self.user_directives["externalID"] = external_id
        result = json.load(StringIO(self.rest_POST(content)))
        self._last_doc = result['doc']
        self._last_result = self.simplify_json(result)
        return self._last_result

    def analyze_url(self, url):
        f = urllib.urlopen(url)
        html = f.read()
        return self.analyze(html, content_type="TEXT/HTML", external_id=url)

    def simplify_json(self, json):
        result = {}
        for element in json.values():
            for k,v in element.items():
                if isinstance(v, unicode) and v.startswith("http://") and json.has_key(v):
                    element[k] = json[v]
        for k, v in json.items():
            if v.has_key("_typeGroup"):
                group = v["_typeGroup"]
                if not result.has_key(group):
                    result[group]=[]
                del v["_typeGroup"]
                v["__reference"] = k
                result[group].append(v)
        return result

    def print_summary(self):
        info = self._last_doc['info']
        print "Calais Request ID: %s" % info['calaisRequestID']
        if info.has_key('externalID'): 
            print "External ID: %s" % info['externalID']
        if info.has_key('docTitle'):
            print "Title: %s " % info['docTitle']
        print "Language: %s" % self._last_doc['meta']['language']
        print "Extractions: "
        for k,v in self._last_result.items():
            print "\t%d %s" % (len(v), k)

    def print_entities(self):
        if self._last_result.has_key('entities'):
            for item in self._last_result['entities']:
                print "%s: %s (%.2f)" % (item['_type'], item['name'], item['relevance'])
        else:
            print "Result has no entities."

    def print_topics(self):
        if self._last_result.has_key('topics'):
            for topic in self._last_result['topics']:
                print topic['categoryName']
        else:
            print "Result has no topics."

    def print_relations(self):
        if self._last_result.has_key('relations'):
            for relation in self._last_result['relations']:
                print relation['_type']
                for k,v in relation.items():
                    if not k.startswith("_"):
                        if isinstance(v, unicode):
                            print "\t%s:%s" % (k,v)
                        elif isinstance(v, dict) and v.has_key('name'):
                            print "\t%s:%s" % (k, v['name'])
        else:
            print "Result has no relations."
