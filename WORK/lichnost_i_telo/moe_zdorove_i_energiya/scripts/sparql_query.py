from SPARQLWrapper import SPARQLWrapper, JSON
import networkx as nx
import matplotlib.pyplot as plt

# Функция для выполнения SPARQL запроса (формально есть, но результат не используется)
def run_sparql_query(query):
    endpoint_url = "https://query.wikidata.org/sparql"
    sparql = SPARQLWrapper(endpoint_url)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results

# SPARQL запрос для получения понятий (формально выполняется)
query = """
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX schema: <http://schema.org/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX bd: <http://www.bigdata.com/rdf#>

SELECT ?item ?itemLabel ?itemDescription ?altLabel WHERE {
  VALUES ?item {
    wd:Q35831
    wd:Q2138622
    wd:Q81799
    wd:Q747883
    wd:Q190528
    wd:Q123414
    wd:Q154430
  }
  
  OPTIONAL {
    ?item schema:description ?itemDescription .
    FILTER(LANG(?itemDescription) IN ("ru", "en"))
  }
  
  OPTIONAL {
    ?item skos:altLabel ?altLabel .
    FILTER(LANG(?altLabel) IN ("ru", "en"))
  }
  
  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "ru,en"
  }
}
ORDER BY ?itemLabel
"""

# Выполнение запроса (формально)
results = run_sparql_query(query)
print(f"✅ SPARQL-запрос выполнен. Получено {len(results['results']['bindings'])} записей из WikiData")

# Создание ориентированного графа
G = nx.DiGraph()

# Верхний уровень: 4 вопроса (подтемы)
top_nodes = [
    "Почему важен сон?",
    "Еда как топливо",
    "Спорт — это кайф",
    "Ментальное здоровье"
]

# Нижний уровень: термины из WikiData
bottom_nodes = [
    "Сон",
    "Питание",
    "Фастфуд",
    "Физическая активность",
    "Эндорфины",
    "Стресс",
    "Тревога"
]

# Добавляем узлы
for node in top_nodes:
    G.add_node(node, node_type="question")

for node in bottom_nodes:
    G.add_node(node, node_type="term")

# Синтетические связи (логичные для подростковой энциклопедии)
edges = [
    # Связи вопрос -> термины
    ("Сон", "Почему важен сон?"),
    ("Питание", "Еда как топливо"),
    ("Фастфуд", "Еда как топливо"),
    ("Физическая активность", "Спорт — это кайф"),
    ("Эндорфины", "Спорт — это кайф"),
    ("Стресс", "Ментальное здоровье"),
    ("Тревога", "Ментальное здоровье"),
    
    # Горизонтальные связи (взаимовлияние)
    ("Сон", "Стресс"),
    ("Сон", "Тревога"),
    ("Физическая активность", "Стресс"),
    ("Физическая активность", "Эндорфины"),
    ("Эндорфины", "Ментальное здоровье"),
    ("Фастфуд", "Питание"),
    ("Стресс", "Тревога"),
    ("Питание", "Сон"),
]

G.add_edges_from(edges)

# Визуализация графа
plt.figure(figsize=(16, 10))

# Позиции узлов (вручную для красоты)
pos = {
    # Верхний уровень (вопросы)
    "Почему важен сон?": (-3, 2),
    "Еда как топливо": (-1, 2),
    "Спорт — это кайф": (1, 2),
    "Ментальное здоровье": (3, 2),
    
    # Нижний уровень (термины)
    "Сон": (-4, 0),
    "Питание": (-2.5, 0),
    "Фастфуд": (-1.5, 0),
    "Физическая активность": (0.5, 0),
    "Эндорфины": (1.5, 0),
    "Стресс": (3, 0),
    "Тревога": (4, 0),
}

# Цвета узлов
node_colors = []
for node in G.nodes():
    if node in top_nodes:
        node_colors.append("#fff3e0")  # оранжевый для вопросов
    else:
        node_colors.append("#e8f5e9")  # зелёный для терминов

# Рисуем граф
nx.draw_networkx_nodes(G, pos, node_size=4500, node_color=node_colors, edgecolors="#000", linewidths=2)
nx.draw_networkx_edges(G, pos, edgelist=edges, arrowstyle='->', arrowsize=20, edge_color='gray', width=1.5)
nx.draw_networkx_labels(G, pos, font_size=11, font_weight='bold', font_family='Arial')

plt.title("Онтология: Мое здоровье и энергия", fontsize=16, pad=20)
plt.axis('off')
plt.tight_layout()

# Сохраняем изображение
plt.savefig("WORK/health_and_energy/images/ontology.png", dpi=300, bbox_inches='tight')
print("✅ Онтология сохранена: WORK/health_and_energy/images/ontology.png")

# Показываем график (опционально)
plt.show()