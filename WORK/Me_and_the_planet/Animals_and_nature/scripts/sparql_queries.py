# -*- coding: utf-8 -*-
import requests
import json
from datetime import datetime
from pathlib import Path

WIKIDATA_ENDPOINT = "https://query.wikidata.org/sparql"
HEADERS = {
    'Accept': 'application/sparql-results+json',
    'User-Agent': 'TeenBook-Animals/1.0'
}

QUERY_REDBOOK = """
SELECT DISTINCT ?item ?itemLabel ?description WHERE {
  VALUES ?item { wd:Q552725 wd:Q11394 }
  OPTIONAL { ?item schema:description ?description . 
             FILTER(LANG(?description) = "ru") }
  SERVICE wikibase:label { 
    bd:serviceParam wikibase:language "ru,en" . 
  }
}
LIMIT 30
"""

QUERY_STRAY = """
SELECT DISTINCT ?item ?itemLabel ?description WHERE {
  VALUES ?item { wd:Q2858709 wd:Q161700 wd:Q230268 }
  OPTIONAL { ?item schema:description ?description . 
             FILTER(LANG(?description) = "ru") }
  SERVICE wikibase:label { 
    bd:serviceParam wikibase:language "ru,en" . 
  }
}
LIMIT 30
"""


QUERY_WILDFIRE = """
SELECT DISTINCT ?item ?itemLabel ?description WHERE {
  VALUES ?item { wd:Q107434304 wd:Q169950 }
  OPTIONAL { ?item schema:description ?description . 
             FILTER(LANG(?description) = "ru") }
  SERVICE wikibase:label { 
    bd:serviceParam wikibase:language "ru,en" . 
  }
}
LIMIT 30
"""

QUERY_PROTECTED = """
SELECT DISTINCT ?item ?itemLabel ?description WHERE {
  VALUES ?item { wd:Q46169 wd:Q473972 }
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


def save_results(results, query_name, output_dir="../data"):
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
    print("SPARQL-запросы для темы: Животные и природа\n")

    queries = [
        (QUERY_REDBOOK, "redbook"),
        (QUERY_STRAY, "stray"),
        (QUERY_WILDFIRE, "wildfire"),
        (QUERY_PROTECTED, "protected"),
    ]

    for query, name in queries:
        result = run_sparql_query(query, name)
        if result:
            save_results(result, name)

    print("\nГотово! Проверь папку data/")