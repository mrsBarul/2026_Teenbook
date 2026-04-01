# pip install sparqlwrapper
# https://rdflib.github.io/sparqlwrapper/

import sys
from SPARQLWrapper import SPARQLWrapper, JSON

endpoint_url = "https://query.wikidata.org/sparql"

query = """SELECT ?cheat ?cheatLabel ?cheatDescription ?game ?gameLabel WHERE {
  # Ищем читы
  ?cheat wdt:P31/wdt:P279* wd:Q264609.
  
  # Для какого они (возможно) предназначены
  OPTIONAL {
    ?cheat ?prop ?game.
    ?game wdt:P31/wdt:P279* wd:Q7889.
  }
  
  OPTIONAL { ?cheat schema:description ?cheatDescription FILTER(LANG(?cheatDescription) = "ru") }
  
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
