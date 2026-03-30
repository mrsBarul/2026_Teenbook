# -*- coding: utf-8 -*-
"""
SPARQL-запросы для темы "Мой след на планете"
WikiData: https://query.wikidata.org/
"""

import requests
import json
from datetime import datetime
from pathlib import Path

WIKIDATA_ENDPOINT = "https://query.wikidata.org/sparql"
HEADERS = {
    'Accept': 'application/sparql-results+json',
    'User-Agent': 'TeenBook-Ecology/1.0'
}

# Запрос 1: Пластик — подкатегории
QUERY_PLASTIC = """
SELECT DISTINCT ?item ?itemLabel ?description WHERE {
  ?item wdt:P279 wd:Q11474 .
  OPTIONAL { ?item schema:description ?description . 
             FILTER(LANG(?description) = "ru") }
  SERVICE wikibase:label { 
    bd:serviceParam wikibase:language "ru,en" . 
  }
}
LIMIT 30
"""

# Запрос 2: Утилизация отходов
QUERY_WASTE = """
SELECT DISTINCT ?item ?itemLabel ?description WHERE {
  ?item wdt:P361 wd:Q2684232 .
  OPTIONAL { ?item schema:description ?description . 
             FILTER(LANG(?description) = "ru") }
  SERVICE wikibase:label { 
    bd:serviceParam wikibase:language "ru,en" . 
  }
}
LIMIT 30
"""

# Запрос 3: Углеродный след — связанные понятия
QUERY_CARBON = """
SELECT DISTINCT ?item ?itemLabel ?description WHERE {
  ?item wdt:P279 wd:Q310667 .
  OPTIONAL { ?item schema:description ?description . 
             FILTER(LANG(?description) = "ru") }
  SERVICE wikibase:label { 
    bd:serviceParam wikibase:language "ru,en" . 
  }
}
LIMIT 30
"""

# Запрос 4: Защита окружающей среды
QUERY_ENV = """
SELECT DISTINCT ?item ?itemLabel ?description WHERE {
  ?item wdt:P361 wd:Q832237 .
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
    print("SPARQL-запросы для темы: Мой след на планете\n")

    queries = [
        (QUERY_PLASTIC, "plastic"),
        (QUERY_WASTE, "waste"),
        (QUERY_CARBON, "carbon"),
        (QUERY_ENV, "env"),
    ]

    for query, name in queries:
        result = run_sparql_query(query, name)
        if result:
            save_results(result, name)

    print("\nГотово! Проверь папку data/")