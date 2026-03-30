from turtle import pos

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
    (wd:Q3182649  "Сепарация")
    (wd:Q131774 "Подростковый возраст")
    (wd:Q659974 "Доверие")
    (wd:Q1274115 "Ответственность")
    (wd:Q484105  "Автономия")
    (wd:Q202875 "Переговоры")
  }
  
  VALUES (?item2 ?concept2) {
    (wd:Q3182649  "Сепарация")
    (wd:Q131774 "Подростковый возраст")
    (wd:Q659974 "Доверие")
    (wd:Q1274115 "Ответственность")
    (wd:Q484105  "Автономия")
    (wd:Q202875 "Переговоры")
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

nodes = [
    "Родительский контроль",
    "Как договариваться",
    "Доверие",
    "Ответственность",
    "Родительская тревога"
]

for node in nodes:
    G.add_node(node)

edges = [
    ("Родительский контроль", "Как договариваться"),
    ("Родительский контроль", "Доверие"),
    ("Родительский контроль", "Ответственность"),
    ("Родительский контроль", "Родительская тревога"),
    
    ("Как договариваться", "Доверие"),
    ("Доверие", "Ответственность"),
    ("Ответственность", "Родительская тревога"),
    ("Родительская тревога", "Доверие")
]

G.add_edges_from(edges)

plt.figure(figsize=(12, 8))

nx.draw(
    G,
    with_labels=True,
    node_size=3500,
    node_color="lightgreen",
    font_size=10,
    font_weight="bold",
    edge_color="gray",
    width=2,
    arrows=True,
    arrowsize=20,
    arrowstyle="-|>",
    bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.3")
)

plt.axis("off")
plt.tight_layout()
plt.show()