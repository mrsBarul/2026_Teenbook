import json
import pathlib
import requests


QUERY = """
SELECT ?item ?itemLabel ?description ?instance_of ?instance_ofLabel WHERE {
  VALUES ?item {
    wd:Q8434
    wd:Q205961
    wd:Q15910354
    wd:Q2506189
    wd:Q133500
    wd:Q11900959
    wd:Q603773
    wd:Q644302
    wd:Q11862829
    wd:Q5038939
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
    "User-Agent": "teenbook-self-development-project/1.0 (educational project)",
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
    "description": "SPARQL-запрос для раздела Self-development",
    "entities_searched": ["Q8434", "Q205961", "Q15910354", "Q2506189", "Q133500", "Q11900959", "Q603773", "Q644302", "Q11862829", "Q5038939"],
  }

  save_result(data, output_path)
  print(f"Готово: результат сохранён в {output_path}")


if __name__ == "__main__":
  main()
