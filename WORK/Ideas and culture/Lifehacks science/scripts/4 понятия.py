# pip install sparqlwrapper
# https://rdflib.github.io/sparqlwrapper/

import sys
from SPARQLWrapper import SPARQLWrapper, JSON

endpoint_url = "https://query.wikidata.org/sparql"

query = """#defaultView:ImageGrid
SELECT DISTINCT ?item ?itemLabel ?itemDescription ?image WHERE {
  VALUES ?gameConcepts {
    wd:Q7889      # компьютерная игра
    wd:Q264609   # чит-код
    wd:Q11140433    # память
    wd:Q128751    # исходный код
    wd:Q865493    # модификация
    wd:Q1087043   # моддинг
    wd:Q15122700  # трейнер
  }
  
  ?item wdt:P279* ?gameConcepts.
  
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
