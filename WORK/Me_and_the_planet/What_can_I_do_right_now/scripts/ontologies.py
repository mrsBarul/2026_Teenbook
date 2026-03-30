import json
import pathlib
import requests

QUERY = """
SELECT ?source ?sourceLabel ?property ?propertyLabel ?target ?targetLabel WHERE {
  # Экологические понятия (ваши ключевые концепции)
  VALUES ?source {
    wd:Q832237     # экологическая ответственность (environmental protection)
    wd:Q3569631    # устойчивый образ жизни (sustainable lifestyle)
    wd:Q931389     # раздельный сбор (waste sorting)
    wd:Q283         # вода (water)
    wd:Q11474       # пластик (plastic)
    wd:Q37813       # экосистема (ecosystem)
    wd:Q47041       # биоразнообразие (biodiversity)
    wd:Q12705       # возобновляемая энергия (renewable energy)
    wd:Q1274484     # устойчивое развитие (sustainable development)
    wd:Q217353      # экологический след (ecological footprint)
    wd:P5991        # углеродный след (carbon footprint)
    wd:Q2684232     # утилизация отходов (waste disposal)
    wd:Q1133632     # экологичная упаковка (eco-friendly packaging)
    wd:Q7930989     # план действий (action plan)
    wd:Q485248      # социальное влияние (social influence)
  }

  ?source ?directProp ?target .
  ?property wikibase:directClaim ?directProp .

  FILTER(?source != ?target)

  VALUES ?importantProps {
    wdt:P279   # подкласс (subclass of)
    wdt:P361   # часть (part of)
    wdt:P1269  # способствует (facilitates)
    wdt:P1542  # влияет на (has effect)
    wdt:P828   # имеет последствие (has cause)
    wdt:P1552  # имеет причину (has characteristic)
  }
  FILTER(?directProp IN (?importantProps))

  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "ru,en" .
  }
}
"""

URL = "https://query.wikidata.org/sparql"


def run_query(query: str) -> dict:
    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": "eco-actions-project/1.0 (educational project for teenagers)"
    }
    try:
        response = requests.get(
            URL,
            params={"query": query, "format": "json"},
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return None


def save_result(data: dict, output_path: str) -> None:
    path = pathlib.Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Результат сохранён в {output_path}")


def print_statistics(data: dict) -> None:
    if not data or 'results' not in data:
        print("Нет данных для статистики")
        return
    
    bindings = data['results']['bindings']
    if not bindings:
        print("Связей не найдено")
        return
    
    relations = {}
    for row in bindings:
        prop = row.get('propertyLabel', {}).get('value', 'неизвестно')
        relations[prop] = relations.get(prop, 0) + 1


def create_concepts_from_wikidata(data: dict) -> list:
    """Создание списка концепций из данных Wikidata"""
    if not data or 'results' not in data:
        return []
    
    concepts = set()
    for row in data['results']['bindings']:
        source = row.get('sourceLabel', {}).get('value')
        target = row.get('targetLabel', {}).get('value')
        if source:
            concepts.add(source)
        if target:
            concepts.add(target)
    
    return sorted(list(concepts))


def main():
    data = run_query(QUERY)
    
    if data:
        save_result(data, "WORK/eco_actions/wikidata_export.json")
        
        simplified = []
        for row in data.get('results', {}).get('bindings', []):
            simplified.append({
                'source': row.get('sourceLabel', {}).get('value'),
                'relation': row.get('propertyLabel', {}).get('value'),
                'target': row.get('targetLabel', {}).get('value')
            })
        
        save_result(simplified, "WORK/eco_actions/wikidata_relations.json")
        
        print("Готово! Файлы сохранены в WORK/eco_actions/")
        
    else:
        print("Не удалось получить данные из Wikidata")


if __name__ == "__main__":
    main()
