import json
import pathlib
import requests


QUERY = """
SELECT ?item ?itemLabel ?description WHERE {
  VALUES ?item {
    wd:Q131774      # adolescence (подросток)
    wd:Q13197964    # stranger (незнакомец)
    wd:Q10566551    # safety (безопасность)
    wd:Q483634      # clothes iron (утюг)
    wd:Q182995      # kitchen stove (плита)
    wd:Q12069731    # space heater (обогреватель)
    wd:Q2425052     # electrical appliance (электроприбор)
    wd:Q815867      # first aid kit (аптечка)
    wd:Q41551       # pipe (труба)
    wd:Q485537      # odor (запах)
    wd:Q1132455     # hazard (опасность)
    wd:Q6010868     # solitude (одиночество)
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
