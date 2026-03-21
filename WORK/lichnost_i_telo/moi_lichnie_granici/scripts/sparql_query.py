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
    (wd:Q7002058 "Личные границы")
    (wd:Q231043 "Согласие")
    (wd:Q628939 "Чувство вины")
    (wd:Q26270533 "Личное пространство")
    (wd:Q8354932 "Право на тайну")
    (wd:Q1339137 "Эмоциональное насилие")
    (wd:Q3702971 "Личные вещи")
  }
  
  VALUES (?item2 ?concept2) {
    (wd:Q7002058 "Личные границы")
    (wd:Q231043 "Согласие")
    (wd:Q628939 "Чувство вины")
    (wd:Q26270533 "Личное пространство")
    (wd:Q8354932 "Право на тайну")
    (wd:Q1339137 "Эмоциональное насилие")
    (wd:Q3702971 "Личные вещи")
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

# Определяем главные узлы (темы для обсуждения)
top_nodes = [
    "Как сказать нет и не чувствовать вину",
    "Мои вещи — мои правила",
    "Что такое эмоциональное насилие"
]

# Определяем базовые понятия (нижний уровень)
bottom_nodes = [
    "Личные границы",
    "Согласие",
    "Чувство вины",
    "Личное пространство",
    "Право на тайну",
    "Эмоциональное насилие",
    "Личные вещи"
]

# Добавляем узлы в граф
for node in top_nodes:
    G.add_node(node, node_type="main")

for node in bottom_nodes:
    G.add_node(node, node_type="topic")

# Определяем связи между базовыми понятиями и главными темами
edges = [
    # Связи для "Как сказать нет и не чувствовать вину"
    ("Согласие", "Как сказать нет и не чувствовать вину"),
    ("Чувство вины", "Как сказать нет и не чувствовать вину"),
    ("Личные границы", "Как сказать нет и не чувствовать вину"),
    
    # Связи для "Мои вещи — мои правила"
    ("Личные вещи", "Мои вещи — мои правила"),
    ("Личное пространство", "Мои вещи — мои правила"),
    ("Право на тайну", "Мои вещи — мои правила"),
    
    # Связи для "Что такое эмоциональное насилие"
    ("Эмоциональное насилие", "Что такое эмоциональное насилие"),
    ("Личные границы", "Что такое эмоциональное насилие"),
    ("Согласие", "Что такое эмоциональное насилие"),
]

G.add_edges_from(edges)

# Настройка визуализации
plt.figure(figsize=(16, 10))

# Позиционирование узлов
pos = {
    # Главные темы (верхний ряд)
    "Как сказать нет и не чувствовать вину": (-3, 2),
    "Мои вещи — мои правила": (0, 2),
    "Что такое эмоциональное насилие": (3, 2),
    
    # Базовые понятия (нижний ряд)
    "Личные границы": (-4, -1),
    "Согласие": (-2, -1),
    "Чувство вины": (0, -1),
    "Личное пространство": (2, -1),
    "Право на тайну": (4, -1),
    "Эмоциональное насилие": (1, -2.5),
    "Личные вещи": (3, -2.5),
}

# Рисуем граф
nx.draw(
    G,
    pos,
    with_labels=True,
    node_size=3000,
    font_size=9,
    font_weight="bold",
    node_color=['lightblue' if node in top_nodes else 'lightgreen' for node in G.nodes()],
    edge_color="gray",
    width=1.5,
    arrows=True,
    arrowsize=20,
    arrowstyle='->'
)

# Добавляем заголовок
plt.title("Граф понятий: Мои личные границы", fontsize=14, fontweight="bold", pad=20)

plt.axis("off")
plt.tight_layout()
plt.show()

# Выводим информацию о найденных связях в Wikidata
print("Найденные связи между понятиями в Wikidata:")
if results['results']['bindings']:
    for binding in results['results']['bindings']:
        print(f"- {binding.get('item1Label', {}).get('value', '?')} → {binding.get('propertyLabel', {}).get('value', '?')} → {binding.get('item2Label', {}).get('value', '?')}")
else:
    print("Связей между понятиями в Wikidata не найдено")