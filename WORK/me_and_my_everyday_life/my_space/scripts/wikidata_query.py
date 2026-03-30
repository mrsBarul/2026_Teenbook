import json
import pathlib
import requests


QUERY = """
SELECT ?item ?itemLabel ?description WHERE {
  VALUES ?item {
    wd:Q26384       # do it yourself (сделай сам)
    wd:Q26270533    # personal space (личное пространство)
    wd:Q1787424     # chaos (хаос)
    wd:Q12893838    # order (порядок)
    wd:Q7566        # parent (родитель)
    wd:Q14754454    # roommate (сосед по комнате)
    wd:Q180516      # room (комната)
    wd:Q1367353     # comfort (уют)
    wd:Q131774      # adolescence (подросток)
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
    "User-Agent": "teenbook (educational project)"
  }

  response = requests.get(
    URL,
    params={"query": query, "format": "json"},
    headers=headers,
    timeout=30,
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
  save_result(data, output_path)

  print(f"Готово: результат сохранён в {output_path}")


if __name__ == "__main__":
  main()
