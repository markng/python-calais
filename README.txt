python-calais v.1.1 -- Python interface to the OpenCalais API
Author: Jordan Dimov (jdimov@mlke.net)

This Python module is a wrapper around the OpenCalais API as documented at http://www.opencalais.com/calaisAPI by Reuters.  It makes REST calls to the OpenCalais API via HTTP POST and can do rudimentary parsing and simplification of the JSON responses returned by OpenCalais.  

The module has been tested with Python 2.5.  

Dependencies:

     * simplejson (http://pypi.python.org/pypi/simplejson)

Basic Usage:

>>> from calais import Calais
>>> API_KEY = "your-opencalais-api-key"
>>> calais = Calais(API_KEY, submitter="python-calais demo")
>>> result = calais.analyze("George Bush was the President of the United Statesof America until 2009.  Barack Obama is the new President of the United States now.")
>>> result.print_summary()
Calais Request ID: 0bfa1f51-4dec-4a82-aba6-a9f8243a94fd
Title:
Language: English
Extractions:
        4 entities
        1 topics
        2 relations
>>> result.print_topics()
Politics
>>> result.print_entities()
Person: Barack Obama (0.29)
Country: United States of America (0.43)
Person: George Bush (0.43)
Country: United States (0.29)
>>> result.print_relations()
PersonPoliticalPast
        person:George Bush
        position:President
PersonPolitical
        person:Barack Obama
        position:President of the United States
>>> print result.entities[0]
{u'_type': u'Person', u'name': u'Barack Obama', '__reference': u'http://d.opencalais.com/pershash-1/cfcf1aa2-de05-3939-a7d5-10c9c7b3e87b', u'instances': [{u'suffix': u' is the new President of the United States', u'prefix': u'of the UnitedStates of America until 2009.  ', u'detection': u'[of the United States of America until 2009.  ]Barack Obama[ is the new President of the United States]', u'length': 12, u'offset': 75, u'exact': u'Barack Obama'}], u'relevance': 0.28599999999999998, u'nationality': u'N/A', u'resolutions': [], u'persontype': u'political'}
>>> result2 = calais.analyze_url("http://www.bestofsicily.com/mafia.htm")
>>> result2.print_summary()
Calais Request ID: 87f09ffe-0643-48e1-855e-7abebf315300
External ID: http://www.bestofsicily.com/mafia.htm
Title: The Mafia in Sicilian History, Sicilian Corruption, the European Commission
Language: English
Extractions:
        68 entities
        1 topics
        8 relations
