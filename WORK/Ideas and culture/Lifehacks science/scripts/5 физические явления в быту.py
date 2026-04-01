# pip install sparqlwrapper
# https://rdflib.github.io/sparqlwrapper/

import sys
from SPARQLWrapper import SPARQLWrapper, JSON

endpoint_url = "https://query.wikidata.org/sparql"

query = """SELECT ?appliance ?applianceLabel ?principle ?principleLabel WHERE {
  VALUES ?appliances {
    wd:Q127956    # микроволновая печь
    wd:Q37828    # холодильник
    wd:Q124441    # стиральная машина
    wd:Q1318740    # лампочка
    wd:Q25504     # светодиод
    wd:Q267298    # батарейка
  }
  
  ?appliance wdt:P279* ?appliances.
  
  # Ищем, какие физические явления они используют
  OPTIONAL {
    ?appliance wdt:P2283 ?principle.  # использует
    ?principle wdt:P279* ?physicsConcept.
  }
  
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
