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

# SPARQL запрос для получения понятий и их категорий
query = """
SELECT ?concept ?conceptLabel ?category ?categoryLabel WHERE {
  ?concept wdt:P31 wd:Q47728. # категория
  ?concept wdt:P279 ?category. # связь с категорией
  VALUES ?conceptLabel {
    "половое созревание" 
    "подростковый возраст"
    "половое воспитание"
    "репродуктивное здоровье"
    "контрацепция"
    "сексуальное образование"
    "психология отношений"
  }

  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],ru". }
}
"""

# Выполнение запроса
results = run_sparql_query(query)

# Создание графа
G = nx.Graph()

# Категории для каждой темы
theme_categories = {
    # Основные темы из вашего раздела
    "Половое созревание: что происходит с мальчиками и девочками": {
        "понятия": ["половое созревание", "гормоны", "физические изменения", "пубертат"],
        "категория": "физиология",
        "подкатегория": "развитие организма"
    },
    "Первый раз, первые отношения — как понять, что ты готов": {
        "понятия": ["первые отношения", "готовность", "эмоциональная зрелость", "взаимопонимание"],
        "категория": "психология",
        "подкатегория": "эмоциональная готовность"
    },
    "Согласие: 'нет' значит нет": {
        "понятия": ["согласие", "личные границы", "уважение", "безопасность"],
        "категория": "этика",
        "подкатегория": "взаимное согласие"
    },
    "Контрацепция и ЗППП — не страшно, а важно": {
        "понятия": ["контрацепция", "защита", "здоровье", "ЗППП", "безопасный секс"],
        "категория": "здоровье",
        "подкатегория": "профилактика"
    },
    "Порно и реальность — почему это не инструкция к применению": {
        "понятия": ["порно", "реальность", "мифы", "критическое мышление"],
        "категория": "медиаграмотность",
        "подкатегория": "информационная безопасность"
    },
    "Стыд и тело: можно ли говорить об этом вслух": {
        "понятия": ["стыд", "тело", "открытость", "принятие", "коммуникация"],
        "категория": "психология",
        "подкатегория": "самопринятие"
    }
}

# Добавление узлов и связей в граф
for theme, data in theme_categories.items():
    # Добавляем основную тему
    G.add_node(theme, node_type="theme")
    
    # Добавляем категорию
    category = data["категория"]
    G.add_node(category, node_type="category")
    G.add_edge(theme, category, relation="относится к категории")
    
    # Добавляем подкатегорию
    subcategory = data["подкатегория"]
    G.add_node(subcategory, node_type="subcategory")
    G.add_edge(category, subcategory, relation="включает")
    G.add_edge(theme, subcategory, relation="связано с")
    
    # Добавляем понятия
    for concept in data["понятия"]:
        G.add_node(concept, node_type="concept")
        G.add_edge(theme, concept, relation="включает понятие")
        G.add_edge(concept, category, relation="относится к")

plt.figure(figsize=(15, 10))

# Позиционирование узлов
pos = nx.spring_layout(G, k=1.5, iterations=50, seed=42)

# Цвета для разных типов узлов
color_map = []
for node in G.nodes():
    node_type = G.nodes[node].get('node_type', 'other')
    if node_type == 'theme':
        color_map.append('#FF9999')  # розовый для тем
    elif node_type == 'category':
        color_map.append('#99FF99')  # зеленый для категорий
    elif node_type == 'subcategory':
        color_map.append('#9999FF')  # синий для подкатегорий
    else:
        color_map.append('#FFE599')  # желтый для понятий

# Рисуем граф
nx.draw(G, pos, with_labels=True, node_size=3000, 
        node_color=color_map, font_size=8, font_weight='bold',
        edge_color='gray', width=1, alpha=0.7)

# Добавляем заголовок
plt.title("Граф полового воспитания подростков", fontsize=16, fontweight='bold')
plt.suptitle("Основные темы и понятия", fontsize=12, y=0.95)

# Добавляем легенду
legend_elements = [
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#FF9999', markersize=10, label='Темы раздела'),
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#99FF99', markersize=10, label='Категории'),
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#9999FF', markersize=10, label='Подкатегории'),
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#FFE599', markersize=10, label='Ключевые понятия')
]
plt.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.3, 1))

plt.tight_layout()
plt.show()

# Дополнительно: вывод статистики
print("Статистика графа:")
print(f"Всего узлов: {G.number_of_nodes()}")
print(f"Всего связей: {G.number_of_edges()}")
print("\nТемы раздела:")
for theme in theme_categories.keys():
    print(f"• {theme}")