"""# Смысл жизни: философские концепции, литературные произведения, философы
SELECT DISTINCT ?item ?itemLabel ?description WHERE {
  {
    # Философские концепции, связанные со смыслом жизни
    ?item wdt:P31/wdt:P279* wd:Q5389993 .
    ?item rdfs:label ?label .
    FILTER(LANG(?label) IN ("ru", "en"))
    FILTER( CONTAINS(LCASE(?label), "смысл жизни") || CONTAINS(LCASE(?label), "meaning of life") )
  }
  UNION
  {
    # Литературные произведения
    ?item wdt:P31 wd:Q7725634 .
    ?item rdfs:label ?label .
    FILTER(LANG(?label) IN ("ru", "en"))
    FILTER( CONTAINS(LCASE(?label), "смысл") || CONTAINS(LCASE(?label), "meaning") )
  }
  UNION
  {
    # Философы, чьи труды связаны с темой смысла жизни
    ?item wdt:P31 wd:Q4964182 .
    ?item wdt:P101 ?field .
    ?field rdfs:label ?fieldLabel .
    FILTER(LANG(?fieldLabel) = "en" && CONTAINS(LCASE(?fieldLabel), "meaning of life"))
  }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "ru,en" }
}
ORDER BY ?itemLabel
LIMIT 100"""
