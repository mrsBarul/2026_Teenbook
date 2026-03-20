from SPARQLWrapper import SPARQLWrapper, JSON
import networkx as nx
import matplotlib.pyplot as plt

# Функция для выполнения SPARQL запроса
def run_sparql_query(query):
    endpoint_url = "https://query.wikidata.org/sparql"
    sparql = SPARQLWrapper(endpoint_url)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results

# SPARQL запрос для получения понятий, связанных с половым воспитанием
query = """
SELECT DISTINCT ?concept ?conceptLabel ?related ?relatedLabel WHERE {
  {
    # Ищем понятия, связанные с половым воспитанием
    ?concept wdt:P361 wd:Q188640.  # часть системы "половое воспитание"
  }
  UNION
  {
    # Или понятия, которые являются экземплярами связанных категорий
    ?concept wdt:P31/wdt:P279* wd:Q188640.
  }
  
  # Ищем связанные понятия (например, по теме или части)
  OPTIONAL {
    ?concept wdt:P921 ?related.  # основная тема
  }
  OPTIONAL {
    ?concept wdt:P361 ?related.  # часть системы
  }
  
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],ru,en". }
}
LIMIT 50
"""

# Выполнение запроса
print("Запрашиваю данные из Викиданных...")
results = run_sparql_query(query)
print(f"Получено {len(results['results']['bindings'])} результатов")

# Создание графа
G = nx.Graph()

# Категории для классификации найденных понятий (на основе ключевых слов)
categories = {
    "физиология": ["puberty", "половое созревание", "репродуктивная", "гормон", "менструация", "эрекция"],
    "здоровье": ["контрацепция", "заболевание", "инфекция", "профилактика", "здоровье", "гигиена"],
    "психология": ["отношения", "чувства", "эмоции", "психология", "стыд", "принятие", "готовность"],
    "этика": ["согласие", "права", "границы", "уважение", "этика", "ответственность"],
    "образование": ["образование", "информация", "знание", "просвещение", "школа"]
}

# Обработка результатов запроса
concepts_found = set()
for result in results["results"]["bindings"]:
    if "conceptLabel" in result:
        concept = result["conceptLabel"]["value"]
        concepts_found.add(concept)
        G.add_node(concept, node_type="concept")
        
        # Определяем категорию для понятия
        concept_lower = concept.lower()
        assigned_category = "другое"
        for category, keywords in categories.items():
            if any(keyword in concept_lower for keyword in keywords):
                assigned_category = category
                break
        
        # Добавляем связь с категорией
        G.add_node(assigned_category, node_type="category")
        G.add_edge(concept, assigned_category, relation="относится к")
        
        # Если есть связанное понятие, добавляем и его
        if "relatedLabel" in result and result["relatedLabel"]["value"]:
            related = result["relatedLabel"]["value"]
            if related != concept:  # избегаем петель
                G.add_node(related, node_type="related")
                G.add_edge(concept, related, relation="связано с")

# Добавляем темы из вашего раздела как отдельные узлы
themes = [
    "Половое созревание: мальчики и девочки",
    "Первый раз и готовность к отношениям", 
    "Согласие: нет значит нет",
    "Контрацепция и ЗППП",
    "Порно и реальность",
    "Стыд и тело"
]

for theme in themes:
    G.add_node(theme, node_type="theme")
    # Связываем тему с найденными понятиями
    for concept in list(concepts_found)[:3]:  # берем первые 3 понятия для связи
        if any(word in concept.lower() for word in theme.lower().split()):
            G.add_edge(theme, concept, relation="обсуждает")

plt.figure(figsize=(16, 12))

# Позиционирование узлов
pos = nx.spring_layout(G, k=2, iterations=100, seed=42)

# Цвета для разных типов узлов
color_map = []
size_map = []
for node in G.nodes():
    node_type = G.nodes[node].get('node_type', 'other')
    if node_type == 'theme':
        color_map.append('#FF6B6B')  # красный для тем
        size_map.append(3000)
    elif node_type == 'category':
        color_map.append('#4ECDC4')  # бирюзовый для категорий
        size_map.append(2500)
    elif node_type == 'concept':
        color_map.append('#FFE66D')  # желтый для понятий
        size_map.append(2000)
    else:
        color_map.append('#95E1D3')  # мятный для связанного
        size_map.append(1500)

# Рисуем граф
nx.draw(G, pos, with_labels=True, node_size=size_map, 
        node_color=color_map, font_size=7, font_weight='bold',
        edge_color='gray', width=0.5, alpha=0.6)

# Добавляем заголовок
plt.title("Граф понятий полового воспитания", fontsize=16, fontweight='bold')
plt.suptitle("Данные из Викиданных и темы раздела", fontsize=12, y=0.95)

# Легенда
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#FF6B6B', markersize=10, label='Темы раздела'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#4ECDC4', markersize=10, label='Категории'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#FFE66D', markersize=10, label='Понятия из Викиданных'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#95E1D3', markersize=10, label='Связанные понятия')
]
plt.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1))

plt.tight_layout()
plt.show()

# Вывод информации
print("\nНайденные понятия из Викиданных:")
for concept in sorted(concepts_found)[:10]:  # первые 10
    print(f"• {concept}")

print(f"\nВсего понятий в графе: {len(concepts_found)}")