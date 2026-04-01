import json
import pathlib
import requests


QUERY = """
SELECT ?item ?itemLabel ?description ?instance_of ?instance_ofLabel WHERE {
  VALUES ?item {
    wd:Q183046
    wd:Q16877783
    wd:Q206287
    wd:Q164800
    wd:Q4419563
    wd:Q928865
    wd:Q102686
    wd:Q25394833
    wd:Q9415
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
    "User-Agent": "teenbook-meanings-project/1.0 (educational project)",
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
    "description": "SPARQL-запрос для раздела Meanings",
    "entities_searched": ["Q183046", "Q16877783", "Q206287", "Q164800", "Q4419563", "Q928865", "Q102686", "Q25394833", "Q9415"],
  }

  save_result(data, output_path)
  print(f"Готово: результат сохранён в {output_path}")


if __name__ == "__main__":
  main()
