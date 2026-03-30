import json
import pathlib
import requests


QUERY = """
SELECT ?item ?itemLabel ?description WHERE {
  VALUES ?item {
    # 8 ключевых концепций раздела household_pets:
    wd:Q1492760   # Подросток (teenager)
    wd:Q2421951   # Забота (care)
    wd:Q144       # Собака (dog)
    wd:Q42982     # Аллергия (allergy)
    wd:Q202883    # Ветеринар (veterinarian)
    wd:Q1026040   # Горе (grief)
    wd:Q1411287   # Приют для животных (animal shelter)
    wd:Q10566551  # Безопасность (safety)
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
