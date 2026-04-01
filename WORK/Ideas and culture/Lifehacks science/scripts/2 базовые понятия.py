# pip install sparqlwrapper
# https://rdflib.github.io/sparqlwrapper/

import sys
from SPARQLWrapper import SPARQLWrapper, JSON

endpoint_url = "https://query.wikidata.org/sparql"

query = """#defaultView:ImageGrid
SELECT DISTINCT ?item ?itemLabel ?itemDescription ?image ?formula WHERE {
  VALUES ?items {
    wd:Q184782    # фосфорная кислота
    wd:Q706       # кальций
    wd:Q265868    # кость
    wd:Q83692    # костная ткань
    wd:Q165328    # остеопороз
    wd:Q13417200   # газированный напиток
  }
  
  ?item wdt:P279* ?items.
  
  OPTIONAL { ?item wdt:P18 ?image. }
  OPTIONAL { ?item wdt:P274 ?formula. } # химическая формула
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
