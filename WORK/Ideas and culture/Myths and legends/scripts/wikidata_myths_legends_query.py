import json
import pathlib
import requests


QUERY = """
SELECT ?item ?itemLabel ?description ?instance_of ?instance_ofLabel WHERE {
  VALUES ?item {
    wd:Q189349
    wd:Q12827256
    wd:Q9134
    wd:Q36192
    wd:Q133182
    wd:Q8102
    wd:Q2927074
    wd:Q30893372
    wd:Q843894
  }

  OPTIONAL {
    ?item wdt:P31 ?instance_of .
  }

  SERVICE wikibase:label { bd:serviceParam wikibase:language "ru,en". }

  OPTIONAL {
    ?item schema:description ?description .
    FILTER(LANG(?description) = "ru")
  }
}
"""

URL = "https://query.wikidata.org/sparql"


def run_query(query: str) -> dict:
  headers = {
    "Accept": "application/sparql-results+json",
    "User-Agent": "teenbook-myths-legends-project/1.0 (educational project)",
  }

  response = requests.get(
    URL,
    params={"query": query, "format": "json"},
    headers=headers,
    timeout=60,
  )
  response.raise_for_status()
  return response.json()


def save_result(data: dict, output_path: pathlib.Path) -> None:
  output_path.parent.mkdir(parents=True, exist_ok=True)
  with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)


def main() -> None:
  script_dir = pathlib.Path(__file__).resolve().parent
  output_path = script_dir.parent / "data" / "wikidata_export.json"

  data = run_query(QUERY)
  data["query_info"] = {
    "description": "SPARQL-запрос для раздела Myths and legends",
    "entities_searched": ["Q189349", "Q12827256", "Q9134", "Q36192", "Q133182", "Q8102", "Q2927074", "Q30893372", "Q843894"],
  }

  save_result(data, output_path)
  print(f"Готово: результат сохранён в {output_path}")


if __name__ == "__main__":
  main()
