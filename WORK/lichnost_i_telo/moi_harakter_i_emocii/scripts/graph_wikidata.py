from pathlib import Path

from SPARQLWrapper import SPARQLWrapper, JSON
import networkx as nx
import matplotlib.pyplot as plt


def run_sparql_query(query: str):
    endpoint_url = "https://query.wikidata.org/sparql"
    sparql = SPARQLWrapper(endpoint_url)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


query = """
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX schema: <http://schema.org/>
PREFIX bd: <http://www.bigdata.com/rdf#>
PREFIX wikibase: <http://wikiba.se/ontology#>

SELECT ?item ?itemLabel ?itemDescription ?concept_ru
WHERE {
  VALUES (?item ?concept_ru) {
    (wd:Q79871 "Гнев")
    (wd:Q169251 "Грусть")
    (wd:Q154430 "Тревога")
    (wd:Q309406 "Апатия")
    (wd:Q935526 "Радость")
    (wd:Q80157 "Темперамент")
    (wd:Q182263 "Эмпатия")
    (wd:Q574559 "Управление гневом")
    (wd:Q4340209 "Депрессия")
    (wd:Q127588 "Интроверсия — экстраверсия")
    (wd:Q26214118 "Экстраверсия")
  }

  OPTIONAL {
    ?item schema:description ?itemDescription .
    FILTER(LANG(?itemDescription) IN ("ru", "en"))
  }

  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "ru,en" .
  }
}
ORDER BY ?concept_ru
"""

results = run_sparql_query(query)

# Собираем уникальные понятия из ответа SPARQL
concepts = []
for row in results["results"]["bindings"]:
    concept_ru = row["concept_ru"]["value"]
    if concept_ru not in concepts:
        concepts.append(concept_ru)

# Ручная логика классификации понятий
category_map = {
    "Эмоции": [
        "Гнев",
        "Грусть",
        "Тревога",
        "Апатия",
        "Радость",
        "Эмпатия",
        "Депрессия",
    ],
    "Саморегуляция": [
        "Управление гневом",
    ],
    "Черты личности": [
        "Темперамент",
        "Интроверсия — экстраверсия",
        "Экстраверсия",
        "Эмпатия",
    ],
}

# Создание графа
G = nx.DiGraph()

# Добавляем категории
for category in category_map:
    G.add_node(category, node_type="main")

# Добавляем понятия
for concept in concepts:
    G.add_node(concept, node_type="topic")

# Добавляем связи понятие -> категория
for category, items in category_map.items():
    for item in items:
        if item in concepts:
            G.add_edge(item, category)

# Фиксированное расположение узлов
pos = {
    "Эмоции": (-3.5, 1.8),
    "Саморегуляция": (0, 1.8),
    "Черты личности": (3.5, 1.8),

    "Гнев": (-6.0, -1.0),
    "Грусть": (-4.8, -1.0),
    "Тревога": (-3.6, -1.0),
    "Апатия": (-2.4, -1.0),
    "Радость": (-1.2, -1.0),
    "Эмпатия": (0.3, -1.0),
    "Управление гневом": (2.2, -1.0),
    "Депрессия": (4.0, -1.0),
    "Темперамент": (5.8, -1.0),
    "Интроверсия — экстраверсия": (8.4, -1.0),
    "Экстраверсия": (11.0, -1.0),
}

plt.figure(figsize=(24, 8))

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
    arrowsize=20,
)

plt.axis("off")

# Сохранение в соседнюю папку images
script_dir = Path(__file__).resolve().parent
images_dir = script_dir.parent / "images"
images_dir.mkdir(parents=True, exist_ok=True)

output_path = images_dir / "SPARQL_graph.png"
plt.savefig(output_path, dpi=300, bbox_inches="tight")

print(f"Граф сохранён в {output_path}")