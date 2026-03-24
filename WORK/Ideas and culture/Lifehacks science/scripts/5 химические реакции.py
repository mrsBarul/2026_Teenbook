# pip install sparqlwrapper
# https://rdflib.github.io/sparqlwrapper/

import sys
from SPARQLWrapper import SPARQLWrapper, JSON

endpoint_url = "https://query.wikidata.org/sparql"

query = """SELECT ?reaction ?reactionLabel ?description WHERE {
  VALUES ?reactions {
    wd:Q133235     # горение (combustion)
    wd:Q1786087    # окисление (oxidation)
    wd:Q11982    # фотосинтез (photosynthesis)
    wd:Q64403    # электролиз (electrolysis)
  }
  
  ?reaction wdt:P279* ?reactions.
  
  OPTIONAL { ?reaction schema:description ?description FILTER(LANG(?description) = "ru") }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "ru". }
}"""


def get_results(endpoint_url, query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


results = get_results(endpoint_url, query)

for result in results["results"]["bindings"]:
    print(result)
