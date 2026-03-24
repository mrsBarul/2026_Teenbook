# pip install sparqlwrapper
# https://rdflib.github.io/sparqlwrapper/

import sys
from SPARQLWrapper import SPARQLWrapper, JSON

endpoint_url = "https://query.wikidata.org/sparql"

query = """#defaultView:ImageGrid
SELECT DISTINCT ?item ?itemLabel ?itemDescription ?image WHERE {
  VALUES ?sleepConcepts {
    wd:Q36348    # сновидение
    wd:Q35831   # сон
    wd:Q1073     # мозг
    wd:Q207011   # нейронаука
    wd:Q181078   # осознанное сновидение
    wd:Q192692   # кошмар
  }
  
  ?item wdt:P279* ?sleepConcepts.
  
  OPTIONAL { ?item wdt:P18 ?image. }
  OPTIONAL { ?item schema:description ?itemDescription FILTER(LANG(?itemDescription) = "ru") }
  
  SERVICE wikibase:label { bd:serviceParam wikibase:language "ru". }
}
LIMIT 50"""


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
