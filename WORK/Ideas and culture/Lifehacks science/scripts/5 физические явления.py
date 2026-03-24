# pip install sparqlwrapper
# https://rdflib.github.io/sparqlwrapper/

import sys
from SPARQLWrapper import SPARQLWrapper, JSON

endpoint_url = "https://query.wikidata.org/sparql"

query = """SELECT ?phenomenon ?phenomenonLabel ?description WHERE {
  VALUES ?phenomena {
    wd:Q41716    # кипение
    wd:Q132814   # испарение
    wd:Q166583   # конденсация
    wd:Q106080   # плавление
    wd:Q108000   # замерзание
    wd:Q82580    # трение
    wd:Q12725     # электричество
    wd:Q3294789    # магнетизм
    wd:Q7465774   # теплопроводность
  }
  
  ?phenomenon wdt:P279* ?phenomena.
  
  OPTIONAL { ?phenomenon schema:description ?description FILTER(LANG(?description) = "ru") }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "ru". }
}
ORDER BY ?phenomenonLabel"""


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
