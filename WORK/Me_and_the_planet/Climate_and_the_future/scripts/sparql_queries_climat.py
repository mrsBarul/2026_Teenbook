import json
import pathlib
import requests

# SPARQL-запрос: связи между понятиями осознанного потребления
QUERY = """
SELECT DISTINCT ?source ?sourceLabel ?property ?propertyLabel ?target ?targetLabel WHERE {
  VALUES ?source {
    wd:Q1134996     # Глобальное потепление — миф или реальность?
    wd:Q8074        # Климатические катастрофы: новая норма
    wd:Q11959879    # Земля через 50 лет: сценарии будущего
    wd:Q29533       # Остановить климатический кризис: что возможно?
    wd:Q7967        # Планета +2°C: пути спасения
    wd:Q80697991    # Экстремальная погода 2025: статистика
    wd:Q919917      # Таяние ледников: Арктика и Антарктида
    wd:Q16942367    # Углеродная нейтральность к 2050
    wd:Q157943      # Метановые выбросы: "спящая бомба" Арктики
    wd:Q5134242     # Климатические беженцы
    wd:Q164206      # Геоинженерия: риски
    wd:Q8074        # Роль человека в климате
  }

  VALUES ?directProp {
    wdt:P31        # экземпляр
    wdt:P279       # подкласс
    wdt:P361       # часть
    wdt:P1542      # влияет на
    wdt:P921       # основная тема
    wdt:P1269      # сфера деятельности
    wdt:P1552      # имеет характеристику
    wdt:P1889      # отличается от
  }

  ?source ?directProp ?target .
  FILTER(isIRI(?target))

  ?property wikibase:directClaim ?directProp .

  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "ru,en"
  }
}
LIMIT 300
"""

URL = "https://query.wikidata.org/sparql"


def run_query(query: str) -> dict:
    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": "teenbook-conscious-consumption/1.0 (educational project)"
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
