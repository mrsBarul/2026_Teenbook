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

# Запрос 1: Глобальное потепление - это реально?
QUERY_GLOBALWARMING = """
SELECT DISTINCT ?item ?itemLabel ?description WHERE {
  VALUES ?item { wd:Q1134996 wd:Q7967 }
  OPTIONAL { ?item schema:description ?description . 
             FILTER(LANG(?description) = "ru") }
  SERVICE wikibase:label { 
    bd:serviceParam wikibase:language "ru,en" . 
  }
}
LIMIT 30
"""

# Запрос 2: Природные катастрофы
QUERY_NATURALDISASTERS = """
SELECT DISTINCT ?item ?itemLabel ?description WHERE {
  VALUES ?item { wd:Q8074 wd:Q919917 }
  OPTIONAL { ?item schema:description ?description . 
             FILTER(LANG(?description) = "ru") }
  SERVICE wikibase:label { 
    bd:serviceParam wikibase:language "ru,en" . 
  }
}
LIMIT 30
"""

# Запрос 3: Что будет через 50 лет
QUERY_FUTURENATURAL = """
SELECT DISTINCT ?item ?itemLabel ?description WHERE {
  VALUES ?item { wd:Q11959879 wd:Q16942367 wd:Q157943 }
  OPTIONAL { ?item schema:description ?description . 
             FILTER(LANG(?description) = "ru") }
  SERVICE wikibase:label { 
    bd:serviceParam wikibase:language "ru,en" . 
  }
}
LIMIT 30
"""

# Запрос 4: Можно ли останоить изменения
QUERY_STOPNEWDISASTERS = """
SELECT DISTINCT ?item ?itemLabel ?description WHERE {
  VALUES ?item { wd:Q11959879 wd:Q5134242 }
  OPTIONAL { ?item schema:description ?description . 
             FILTER(LANG(?description) = "ru") }
  SERVICE wikibase:label { 
    bd:serviceParam wikibase:language "ru,en" . 
  }
}
LIMIT 30
"""

# Запрос 5: Рольчелоека во всем этом
QUERY_ROLEOFHUMANS = """
SELECT DISTINCT ?item ?itemLabel ?description WHERE {
  VALUES ?item { wd:Q8074 }
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
        (QUERY_GLOBALWARMING, "globalwarming"),
        (QUERY_NATURALDISASTERS, "naturaldisasters"),
        (QUERY_FUTURENATURAL, "futuredisasters"),
        (QUERY_STOPNEWDISASTERS, "stopnewdisasters"),
        (QUERY_ROLEOFHUMANS, "roleofhumans"),
    ]

    for query, name in queries:
        result = run_sparql_query(query, name)
        if result:
            save_results(result, name)

    print("\nГотово! Проверь папку data/")
