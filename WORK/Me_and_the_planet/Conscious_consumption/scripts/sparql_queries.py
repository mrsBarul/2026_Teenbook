# -*- coding: utf-8 -*-
"""
SPARQL-запросы для темы "Осознанное потребление"
WikiData: https://query.wikidata.org/
"""

import requests
import json
from datetime import datetime
from pathlib import Path

WIKIDATA_ENDPOINT = "https://query.wikidata.org/sparql"
HEADERS = {
    'Accept': 'application/sparql-results+json',
    'User-Agent': 'TeenBook-ConsciousConsumption/1.0'
}

# Запрос 1: Устойчивое потребление (sustainable consumption)
QUERY_SUSTAINABLE = """
SELECT DISTINCT ?item ?itemLabel ?description WHERE {
  ?item wdt:P279 wd:Q477335 .
  OPTIONAL { ?item schema:description ?description . 
             FILTER(LANG(?description) = "ru") }
  SERVICE wikibase:label { 
    bd:serviceParam wikibase:language "ru,en" . 
  }
}
LIMIT 30
"""

# Запрос 2: Fast fashion — связанные понятия
QUERY_FASTFASHION = """
SELECT DISTINCT ?item ?itemLabel ?description WHERE {
  ?item wdt:P361 wd:Q2425590 .
  OPTIONAL { ?item schema:description ?description . 
             FILTER(LANG(?description) = "ru") }
  SERVICE wikibase:label { 
    bd:serviceParam wikibase:language "ru,en" . 
  }
}
LIMIT 30
"""

# Запрос 3: Право на ремонт (right to repair)
QUERY_REPAIR = """
SELECT DISTINCT ?item ?itemLabel ?description WHERE {
  ?item wdt:P279 wd:Q108837947 .
  OPTIONAL { ?item schema:description ?description . 
             FILTER(LANG(?description) = "ru") }
  SERVICE wikibase:label { 
    bd:serviceParam wikibase:language "ru,en" . 
  }
}
LIMIT 30
"""

# Запрос 4: Обмен одеждой и секонд-хенд
QUERY_SWAP = """
SELECT DISTINCT ?item ?itemLabel ?description WHERE {
  VALUES ?item { wd:Q5135580 wd:Q223722 }
  OPTIONAL { ?item schema:description ?description . 
             FILTER(LANG(?description) = "ru") }
  SERVICE wikibase:label { 
    bd:serviceParam wikibase:language "ru,en" . 
  }
}
LIMIT 30
"""

# Запрос 5: Избыточное потребление (overconsumption)
QUERY_OVERCONSUMPTION = """
SELECT DISTINCT ?item ?itemLabel ?description WHERE {
  ?item wdt:P279 wd:Q740691 .
  OPTIONAL { ?item schema:description ?description . 
             FILTER(LANG(?description) = "ru") }
  SERVICE wikibase:label { 
    bd:serviceParam wikibase:language "ru,en" . 
  }
}
LIMIT 30
"""

# Запрос 6: Циркулярная экономика (circular economy)
QUERY_CIRCULAR = """
SELECT DISTINCT ?item ?itemLabel ?description WHERE {
  ?item wdt:P279 wd:Q497743 .
  OPTIONAL { ?item schema:description ?description . 
             FILTER(LANG(?description) = "ru") }
  SERVICE wikibase:label { 
    bd:serviceParam wikibase:language "ru,en" . 
  }
}
LIMIT 30
"""


def run_sparql_query(query, query_name="unnamed"):
    """Выполняет SPARQL-запрос и возвращает результаты"""
    print(f"Выполняю запрос: {query_name}...")
    try:
        response = requests.get(
            WIKIDATA_ENDPOINT,
            params={'query': query},
            headers=HEADERS,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        count = len(data.get('results', {}).get('bindings', []))
        print(f"Получено {count} результатов")
        return data
    except Exception as e:
        print(f"Ошибка: {e}")
        return None


def save_results(results, query_name, output_dir="data"):
    """Сохраняет результаты в JSON-файл"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    export_data = {
        "query_name": query_name,
        "timestamp": datetime.now().isoformat(),
        "endpoint": WIKIDATA_ENDPOINT,
        "results_count": len(results.get('results', {}).get('bindings', [])) if results else 0,
        "results": results
    }

    filename = f"{output_dir}/wikidata_{query_name}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)

    print(f"Сохранено в {filename}")
    return filename


if __name__ == "__main__":
    print("SPARQL-запросы для темы: Осознанное потребление\n")

    queries = [
        (QUERY_SUSTAINABLE, "sustainable"),
        (QUERY_FASTFASHION, "fastfashion"),
        (QUERY_REPAIR, "repair"),
        (QUERY_SWAP, "swap"),
        (QUERY_OVERCONSUMPTION, "overconsumption"),
        (QUERY_CIRCULAR, "circular"),
    ]

    for query, name in queries:
        result = run_sparql_query(query, name)
        if result:
            save_results(result, name)

    print("\nГотово! Проверь папку data/")