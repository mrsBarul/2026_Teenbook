import json
import pathlib
import requests


QUERY = """
SELECT ?item ?itemLabel ?description WHERE {
  VALUES ?item {
    wd:Q1004       # comics
    wd:Q21198342   # manga
    wd:Q1233720    # young adult literature
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
  """
  Выполняет SPARQL‑запрос к Wikidata и возвращает результат как словарь.
  """
  headers = {
    "Accept": "application/sparql-results+json",
    "User-Agent": "teenbook-books-comics-project/1.0 (educational project)",
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
  """
  Сохраняет результат запроса в JSON‑файл.
  """
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

