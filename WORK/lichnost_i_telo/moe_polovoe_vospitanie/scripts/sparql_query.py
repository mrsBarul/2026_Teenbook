from SPARQLWrapper import SPARQLWrapper, JSON
import networkx as nx
import matplotlib.pyplot as plt

# Функция для выполнения SPARQL запроса
def run_sparql_query(query):
    endpoint_url = "https://query.wikidata.org/sparql"
    sparql = SPARQLWrapper(endpoint_url)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results

# SPARQL запрос для получения понятий и их категорий
query = """
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX bd: <http://www.bigdata.com/rdf#>

SELECT DISTINCT ?item1 ?item1Label ?item2 ?item2Label ?property ?propertyLabel WHERE {
  VALUES (?item1 ?concept1) {
    (wd:Q101065 "Половое созревание")
    (wd:Q1189047 "Романтические отношения")
    (wd:Q764527 "Согласие")
    (wd:Q231043 "Согласие")
    (wd:Q122224  "Контрацепция")
    (wd:Q67867650 "Возраст начала половой жизни")
    (wd:Q1190058 "Физическая близость")
    (wd:Q5373791 "Эмоциональная близость")
    (wd:Q12198 "ЗППП")
    (wd:Q291 "Порнография")
    (wd:Q63522120 "Бодишейминг")
  }
  
  VALUES (?item2 ?concept2) {
    (wd:Q101065 "Половое созревание")
    (wd:Q1189047 "Романтические отношения")
    (wd:Q764527 "Согласие")
    (wd:Q231043 "Согласие")
    (wd:Q122224  "Контрацепция")
    (wd:Q67867650 "Возраст начала половой жизни")
    (wd:Q1190058 "Физическая близость")
    (wd:Q5373791 "Эмоциональная близость")
    (wd:Q12198 "ЗППП")
    (wd:Q291 "Порнография")
    (wd:Q63522120 "Бодишейминг")
  }
  
  # Ищем связи между парами (исключая связи с самим собой)
  FILTER(?item1 != ?item2)
  
  # Поиск прямых связей через любые свойства
  ?item1 ?property ?item2 .
  
  # Фильтруем только интересующие нас типы свойств
  ?property a wikibase:Property .
  
  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "ru,en" .
    ?property rdfs:label ?propertyLabel .
    ?item1 rdfs:label ?item1Label .
    ?item2 rdfs:label ?item2Label .
  }
}
ORDER BY ?item1Label ?item2Label
"""

# Выполнение запроса
results = run_sparql_query(query)

# Создание ориентированного графа
G = nx.DiGraph()


top_nodes = ["Первые отношения", "Порно и реальность"]
bottom_nodes = [
    "Контрацепция",
    "ЗППП",
    "Порнография",
    "Бодишейминг",
    "Половое созревание"
]


for node in top_nodes:
    G.add_node(node, node_type="main")

for node in bottom_nodes:
    G.add_node(node, node_type="topic")

edges = [
    ("Контрацепция", "Первые отношения"),
    ("ЗППП", "Первые отношения"),
    ("Порнография", "Первые отношения"),
    ("Бодишейминг", "Первые отношения"),
    ("Половое созревание", "Первые отношения"),

    ("Порнография", "Порно и реальность"),
    ("Бодишейминг", "Порно и реальность"),
    ("Половое созревание", "Порно и реальность"),
    ("Контрацепция", "Порно и реальность"),
]

G.add_edges_from(edges)

plt.figure(figsize=(14, 8))

pos = {
    "Первые отношения": (-1.5, 1),
    "Порно и реальность": (1.5, 1),

    "Контрацепция": (-3, -1),
    "ЗППП": (-1.5, -1),
    "Порнография": (0, -1),
    "Бодишейминг": (1.5, -1),
    "Половое созревание": (3, -1),
}

nx.draw(
    G,
    pos,
    with_labels=True,
    node_size=3500,
    font_size=10,
    font_weight="bold",
    edge_color="gray",
    width=1.5,
    arrows=True,
    arrowsize=20
)

plt.axis("off")
plt.tight_layout()
plt.show()