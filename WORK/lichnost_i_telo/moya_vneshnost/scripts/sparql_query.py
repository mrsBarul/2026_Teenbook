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

# SPARQL запрос для получения понятий и их связей
query = """
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX bd: <http://www.bigdata.com/rdf#>

SELECT DISTINCT ?item1 ?item1Label ?item2 ?item2Label ?property ?propertyLabel WHERE {
  VALUES (?item1 ?concept1) {
    (wd:Q15733239 "Образ тела")
    (wd:Q10981881 "Самооценка")
    (wd:Q79928 "Акне")
    (wd:Q23013372 "Бодипозитив")
    (wd:Q12684 "Мода")
    (wd:Q7162 "Генетика")
    (wd:Q131774 "Подростковый возраст")
    (wd:Q11364 "Гормон")
  }
  
  VALUES (?item2 ?concept2) {
    (wd:Q15733239 "Образ тела")
    (wd:Q10981881 "Самооценка")
    (wd:Q79928 "Акне")
    (wd:Q23013372 "Бодипозитив")
    (wd:Q12684 "Мода")
    (wd:Q7162 "Генетика")
    (wd:Q131774 "Подростковый возраст")
    (wd:Q11364 "Гормон")
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

# ============================================
# ОНТОЛОГИЯ РАЗДЕЛА "МОЯ ВНЕШНОСТЬ"
# ============================================

# Центральные концепты (ядро темы)
central_nodes = ["Образ тела", "Самооценка"]

# Факторы влияния (биологические)
bio_factors = ["Генетика", "Гормон", "Акне", "Подростковый возраст"]

# Факторы влияния (социальные/психологические)
social_factors = ["Бодипозитив", "Мода"]

# Добавляем узлы с типами
for node in central_nodes:
    G.add_node(node, node_type="central")

for node in bio_factors:
    G.add_node(node, node_type="biological")

for node in social_factors:
    G.add_node(node, node_type="social")

# Логические связи между концептами
edges = [
    # Биологические факторы → Внешность
    ("Генетика", "Образ тела"),
    ("Гормон", "Акне"),
    ("Акне", "Образ тела"),
    ("Подростковый возраст", "Гормон"),
    ("Подростковый возраст", "Акне"),
    
    # Социальные факторы → Восприятие себя
    ("Бодипозитив", "Образ тела"),
    ("Бодипозитив", "Самооценка"),
    ("Мода", "Самооценка"),
    
    # Связь между центральными концептами
    ("Образ тела", "Самооценка"),
    
    # Дополнительные связи
    ("Генетика", "Акне"),
    ("Подростковый возраст", "Образ тела"),
]

G.add_edges_from(edges)

# ============================================
# ВИЗУАЛИЗАЦИЯ
# ============================================

plt.figure(figsize=(16, 10))

# Позиции узлов (трёхуровневая структура)
pos = {
    # Центральный уровень (ядро)
    "Образ тела": (-2, 2),
    "Самооценка": (2, 2),
    
    # Биологические факторы (низ слева)
    "Генетика": (-4, -1),
    "Гормон": (-2, -1),
    "Акне": (0, -1),
    "Подростковый возраст": (2, -1),
    
    # Социальные факторы (низ справа)
    "Бодипозитив": (-3, 0),
    "Мода": (4, 0),
}

# Цвета для разных типов узлов
node_colors = []
for node in G.nodes():
    if node in central_nodes:
        node_colors.append("#FF6B6B")  # Красный - центральные
    elif node in bio_factors:
        node_colors.append("#4ECDC4")  # Бирюзовый - биологические
    else:
        node_colors.append("#95E1D3")  # Зелёный - социальные

nx.draw(
    G,
    pos,
    with_labels=True,
    node_size=4000,
    font_size=11,
    font_weight="bold",
    node_color=node_colors,
    edge_color="gray",
    width=2,
    arrows=True,
    arrowsize=25,
    alpha=0.9
)

# Добавляем легенду
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor="#FF6B6B", label="Центральные концепты"),
    Patch(facecolor="#4ECDC4", label="Биологические факторы"),
    Patch(facecolor="#95E1D3", label="Социальные факторы")
]
plt.legend(handles=legend_elements, loc="lower right", fontsize=10)

plt.axis("off")
plt.tight_layout()
plt.savefig("ontology_moya_vneshnost.png", dpi=300, bbox_inches="tight")
plt.show()

# ============================================
# ВЫВОД ИНФОРМАЦИИ О ГРАФЕ
# ============================================

print("=" * 60)
print("ОНТОЛОГИЯ РАЗДЕЛА: МОЯ ВНЕШНОСТЬ")
print("=" * 60)
print(f"\n📊 Всего узлов: {G.number_of_nodes()}")
print(f"🔗 Всего связей: {G.number_of_edges()}")

print("\n📌 Центральные концепты:")
for node in central_nodes:
    print(f"   • {node}")

print("\n🧬 Биологические факторы:")
for node in bio_factors:
    print(f"   • {node}")

print("\n🌐 Социальные факторы:")
for node in social_factors:
    print(f"   • {node}")

print("\n🔗 Все связи:")
for edge in G.edges():
    print(f"   {edge[0]} → {edge[1]}")

# Сохранение в JSON для использования в проекте
import json

ontology_data = {
    "topic": "Моя внешность",
    "topic_slug": "moya_vneshnost",
    "central_concepts": central_nodes,
    "biological_factors": bio_factors,
    "social_factors": social_factors,
    "edges": [{"from": e[0], "to": e[1]} for e in G.edges()],
    "wikidata_ids": {
        "Образ тела": "Q15733239",
        "Самооценка": "Q10981881",
        "Акне": "Q79928",
        "Бодипозитив": "Q23013372",
        "Мода": "Q12684",
        "Генетика": "Q7162",
        "Подростковый возраст": "Q131774",
        "Гормон": "Q11364"
    }
}

with open("ontology_moya_vneshnost.json", "w", encoding="utf-8") as f:
    json.dump(ontology_data, f, ensure_ascii=False, indent=2)

print("\n✅ Онтология сохранена в: ontology_moya_vneshnost.json")
print("✅ График сохранён в: ontology_moya_vneshnost.png")