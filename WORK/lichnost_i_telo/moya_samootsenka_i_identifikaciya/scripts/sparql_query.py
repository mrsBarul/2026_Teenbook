"""
SPARQL к Wikidata + синтетический граф для темы «Самооценка и идентификация».
"""

from __future__ import annotations

import json
from pathlib import Path

from SPARQLWrapper import SPARQLWrapper, JSON
import networkx as nx
import matplotlib.pyplot as plt

_THEME_ROOT = Path(__file__).resolve().parent.parent

DATA_JSON = _THEME_ROOT / "data" / "moya_samootsenka_i_identifikaciya.json"

# Картинка для отчёта / README (как у других тем: images/ontology.png)
ONTOLOGY_PNG = _THEME_ROOT / "images" / "ontology.png"


def save_sparql_results(results: dict, path: Path) -> None:
    """Пишет ответ Wikidata в JSON рядом с данными темы."""
    path.parent.mkdir(parents=True, exist_ok=True)
    out = {
        "description": (
            "Ответ Wikidata Query Service. Файл перезаписывается при запуске "
            "scripts/sparql_query.py. Запрос ниже выгружает метки выбранных QID "
            "(прямые ребра между ними в Wikidata обычно отсутствуют). "
            "Граф в конце скрипта по-прежнему синтетический."
        ),
        "head": results.get("head", {}),
        "results": results.get("results", {}),
    }
    path.write_text(
        json.dumps(out, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Сохранено: {path} (bindings: {len(out['results'].get('bindings', []))})")


def run_sparql_query(query: str) -> dict:
    """Выполняет SPARQL-запрос к Wikidata."""
    endpoint_url = "https://query.wikidata.org/sparql"
    sparql = SPARQLWrapper(endpoint_url)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


# Прямые дуги между произвольными QID в Wikidata редки — старый шаблон давал 0 строк.
# Здесь только метки выбранных сущностей — ответ непустой при рабочем интернете.
query = """
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX bd: <http://www.bigdata.com/rdf#>

SELECT ?item ?itemLabel WHERE {
  VALUES ?item {
    wd:Q120675
    wd:Q185573
    wd:Q175862
    wd:Q1963141
    wd:Q2717571
    wd:Q1860
  }
  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "ru,en" .
    ?item rdfs:label ?itemLabel .
  }
}
ORDER BY ?item
"""

results = run_sparql_query(query)
save_sparql_results(results, DATA_JSON)

G = nx.DiGraph()

top_nodes = [
    "Кто я и идентичность",
    "Мнение других",
    "Быть собой",
]

bottom_nodes = [
    "Самооценка",
    "Социальное сравнение",
    "Сильные стороны / без лайков",
]

for node in top_nodes + bottom_nodes:
    G.add_node(node, node_type="article" if node in top_nodes else "theme")

edges = [
    ("Самооценка", "Кто я и идентичность"),
    ("Социальное сравнение", "Кто я и идентичность"),
    ("Социальное сравнение", "Мнение других"),
    ("Самооценка", "Мнение других"),
    ("Сильные стороны / без лайков", "Кто я и идентичность"),
    ("Сильные стороны / без лайков", "Быть собой"),
    ("Самооценка", "Быть собой"),
]

G.add_edges_from(edges)

pos = {
    "Кто я и идентичность": (0, 1.2),
    "Мнение других": (-2, 1.2),
    "Быть собой": (2, 1.2),
    "Самооценка": (-2, -0.8),
    "Социальное сравнение": (0, -0.8),
    "Сильные стороны / без лайков": (2, -0.8),
}

fig, ax = plt.subplots(figsize=(12, 7))
nx.draw(
    G,
    pos,
    ax=ax,
    with_labels=True,
    node_size=4200,
    font_size=8,
    font_weight="bold",
    edge_color="gray",
    width=1.4,
    arrows=True,
    arrowsize=16,
)
ax.set_axis_off()
fig.subplots_adjust(left=0.02, right=0.98, bottom=0.02, top=0.98)

ONTOLOGY_PNG.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(
    ONTOLOGY_PNG,
    dpi=150,
    bbox_inches="tight",
    facecolor="white",
)
print(f"Онтология (PNG): {ONTOLOGY_PNG}")

try:
    plt.show()
finally:
    plt.close(fig)
