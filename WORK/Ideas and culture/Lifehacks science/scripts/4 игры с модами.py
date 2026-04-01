# pip install sparqlwrapper
# https://rdflib.github.io/sparqlwrapper/

import sys
from SPARQLWrapper import SPARQLWrapper, JSON

endpoint_url = "https://query.wikidata.org/sparql"

query = """SELECT ?game ?gameLabel ?modSupport ?modSupportLabel WHERE {
  # Игры
  ?game wdt:P31/wdt:P279* wd:Q7889.
  
  # Ищем явные указания на поддержку модов
  OPTIONAL {
    ?game ?prop ?modSupport.
    ?modSupport wdt:P279* wd:Q1087043.  # моддинг
  }
  
  # Добавляем игры с большим количеством сайтлинков (популярные)
  ?game wikibase:sitelinks ?sitelinks.
  FILTER(?sitelinks > 50)
  
  SERVICE wikibase:label { bd:serviceParam wikibase:language "ru". }
}
ORDER BY DESC(?sitelinks)
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
