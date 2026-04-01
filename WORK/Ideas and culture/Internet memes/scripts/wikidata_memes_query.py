import json
import pathlib
import requests


QUERY = """
SELECT ?item ?itemLabel ?description ?instance_of ?instance_ofLabel WHERE {
  VALUES ?item {
    wd:Q2001305     # Internet meme
    wd:Q13442814    # Meme
    wd:Q1523883     # Viral video
    wd:Q1080288     # Image macro
    wd:Q3273210     # Internet celebrity
    wd:Q1226219     # Satire
    wd:Q11022       # Caricature
    wd:Q189819      # Cartoon
    wd:Q219523      # TikTok
    wd:Q866         # YouTube
    wd:Q220982      # Telegram
    wd:Q22697       # VK
    wd:Q206843      # 4chan
    wd:Q1136        # Reddit
    wd:Q1047113     # Know Your Meme
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
  """
  Выполняет SPARQL-запрос к Wikidata и возвращает результат как словарь.
  """
  headers = {
    "Accept": "application/sparql-results+json",
    "User-Agent": "teenbook-memes-project/1.0 (educational project)",
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
  """
  Сохраняет результат запроса в JSON-файл.
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
