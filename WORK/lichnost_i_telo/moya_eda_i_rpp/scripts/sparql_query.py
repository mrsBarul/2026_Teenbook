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
    (wd:Q373822  "Расстройство пищевого поведения")
    (wd:Q131749 "Анорексия")
    (wd:Q254327 "Анорексия")
    (wd:Q64513386 "Булимия")
    (wd:Q209522  "Компульсивное переедание")
    (wd:Q448191 "Диета")
    (wd:Q121670  "Недоедание")
  }
  
  VALUES (?item2 ?concept2) {
    (wd:Q373822  "Расстройство пищевого поведения")
    (wd:Q131749 "Анорексия")
    (wd:Q254327 "Анорексия")
    (wd:Q64513386 "Булимия")
    (wd:Q209522  "Компульсивное переедание")
    (wd:Q448191 "Диета")
    (wd:Q121670  "Недоедание")
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

top_nodes = ["Еда как удовольствие, топливо и наказание"]
middle_nodes = ["Диета и РПП"]
bottom_nodes = [
    "Булимия",
    "Анорексия",
    "Компульсивное переедание",
    "Помощь при РПП"
]

for node in top_nodes:
    G.add_node(node, level="top")
for node in middle_nodes:
    G.add_node(node, level="middle")
for node in bottom_nodes:
    G.add_node(node, level="bottom")

edges = [
    ("Еда как удовольствие, топливо и наказание", "Диета и РПП"),
    ("Диета и РПП", "Булимия"),
    ("Диета и РПП", "Анорексия"),
    ("Диета и РПП", "Компульсивное переедание"),
    ("Диета и РПП", "Помощь при РПП")
]

G.add_edges_from(edges)

plt.figure(figsize=(14, 10))

pos = {
    "Еда как удовольствие, топливо и наказание": (0, 2),
    "Диета и РПП": (0, 1),
    "Булимия": (-2, 0),
    "Анорексия": (-0.7, 0),
    "Компульсивное переедание": (0.6, 0),
    "Помощь при РПП": (2, 0)
}

nx.draw(
    G,
    pos,
    with_labels=True,
    node_size=4000,
    node_color="lightblue",
    font_size=9,
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
plt.title("Иерархия расстройств пищевого поведения", fontsize=14, fontweight="bold", pad=20)
plt.show()