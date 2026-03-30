import json
import pathlib
import requests

QUERY = """
SELECT DISTINCT ?source ?sourceLabel ?property ?propertyLabel ?target ?targetLabel WHERE {
  VALUES ?source {
    wd:Q552725     # Красная книга России
    wd:Q11394      # Исчезающий вид
    wd:Q2858709    # Приют для животных
    wd:Q161700     # Бродячая собака
    wd:Q107434304  # Лесной пожар
    wd:Q169950     # Природный пожар
    wd:Q46169      # Национальный парк
    wd:Q473972     # Заповедник
    wd:Q832237     # Охрана окружающей среды
    wd:Q219416     # Устойчивость окружающей среды
  }

  VALUES ?directProp {
    wdt:P31        # экземпляр
    wdt:P279       # подкласс
    wdt:P361       # часть
    wdt:P1542      # влияет на
    wdt:P921       # основная тема
    wdt:P1269      # сфера деятельности
    wdt:P1889      # отличается от
  }

  ?source ?directProp ?target .
  FILTER(isIRI(?target))

  ?property wikibase:directClaim ?directProp .

  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "ru,en"
  }
}
LIMIT 200
"""

URL = "https://query.wikidata.org/sparql"


def run_query(query: str) -> dict:
    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": "teenbook-animals-project/1.0 (educational project)"
    }

    response = requests.get(
        URL,
        params={"query": query, "format": "json"},
        headers=headers,
        timeout=30
    )
    response.raise_for_status()
    return response.json()


def save_result(data: dict, output_path: pathlib.Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    script_dir = pathlib.Path(__file__).resolve().parent
    output_path = script_dir.parent / "data" / "wikidata_export.json"

    data = run_query(QUERY)
    save_result(data, output_path)

    print(f"✅ Готово: результат сохранён в {output_path}")
    print(f"📊 Получено {len(data.get('results', {}).get('bindings', []))} связей")


if __name__ == "__main__":
    main()