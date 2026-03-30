import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

nodes = {
    "Экологическая\nответственность": (0.5, 0.92),
    
    "Эко-привычки": (0.12, 0.72),
    "Раздельный сбор": (0.28, 0.72),
    "Экономия воды": (0.5, 0.72),
    "Эко-упаковка": (0.72, 0.72),
    "Утилизация\nотходов": (0.88, 0.72),
    
    "Углеродный след": (0.12, 0.52),
    "Экологический\nслед": (0.28, 0.52),
    "Экосистема": (0.5, 0.52),
    "Биоразнообразие": (0.72, 0.52),
    "Возобновляемая\nэнергия": (0.88, 0.52),
    
    "Личный экоплан": (0.5, 0.28),
}

# Связи между узлами
edges = [
    # От ответственности к действиям
    ("Экологическая\nответственность", "Эко-привычки", "формирует"),
    ("Экологическая\nответственность", "Раздельный сбор", "мотивирует"),
    ("Экологическая\nответственность", "Экономия воды", "побуждает"),
    ("Экологическая\nответственность", "Эко-упаковка", "влияет"),
    ("Экологическая\nответственность", "Утилизация\nотходов", "требует"),
    
    # От действий к последствиям
    ("Эко-привычки", "Углеродный след", "снижает"),
    ("Эко-привычки", "Экологический\nслед", "уменьшает"),
    ("Раздельный сбор", "Утилизация\nотходов", "основан на"),
    ("Экономия воды", "Возобновляемая\nэнергия", "связана с"),
    ("Эко-упаковка", "Утилизация\nотходов", "сокращает"),
    
    # Влияние на природу
    ("Углеродный след", "Экосистема", "влияет на"),
    ("Экологический\nслед", "Биоразнообразие", "угрожает"),
    ("Экосистема", "Биоразнообразие", "поддерживает"),
    ("Возобновляемая\nэнергия", "Углеродный след", "уменьшает"),
    ("Утилизация\nотходов", "Экосистема", "защищает"),
    
    # К личному плану
    ("Экологическая\nответственность", "Личный экоплан", "лежит в основе"),
    ("Эко-привычки", "Личный экоплан", "входят в"),
    ("Углеродный след", "Личный экоплан", "учитывает"),
    ("Экологический\nслед", "Личный экоплан", "измеряет"),
    ("Экосистема", "Личный экоплан", "защищает"),
]


def draw_node(ax, label, x, y, w=0.16, h=0.08):
    box = FancyBboxPatch(
        (x - w / 2, y - h / 2),
        w,
        h,
        boxstyle="round,pad=0.03,rounding_size=0.03",
        linewidth=2,
        edgecolor="#2e7d32",
        facecolor="#e8f5e9",
        alpha=0.95
    )
    ax.add_patch(box)
    ax.text(x, y, label, ha="center", va="center", fontsize=10, weight="bold", linespacing=1.2)


def draw_edge(ax, start, end, text):
    x1, y1 = nodes[start]
    x2, y2 = nodes[end]
    
    # Цвет и стиль стрелки в зависимости от типа связи
    if "снижает" in text or "уменьшает" in text or "защищает" in text:
        color = "#4caf50"
        lw = 2
    elif "угрожает" in text:
        color = "#f44336"
        lw = 2
    elif "формирует" in text or "мотивирует" in text:
        color = "#ff9800"
        lw = 1.8
    else:
        color = "#2196f3"
        lw = 1.6
    
    ax.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle="->",
            lw=lw,
            color=color,
            shrinkA=25,
            shrinkB=25,
            connectionstyle="arc3,rad=0.1"
        )
    )
    
    mx = (x1 + x2) / 2
    my = (y1 + y2) / 2
    
    if y1 > y2 + 0.1:  # сверху вниз
        my -= 0.03
    elif y2 > y1 + 0.1:  # снизу вверх
        my += 0.03
    elif x2 > x1:  # слева направо
        my += 0.02
    else:
        my += 0.02
    
    ax.text(mx, my + 0.02, text, ha="center", va="center", fontsize=8, 
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="#cccccc", alpha=0.85))


fig, ax = plt.subplots(figsize=(16, 12))
ax.set_xlim(-0.05, 1.05)
ax.set_ylim(-0.05, 1.05)
ax.axis("off")

ax.text(0.5, 0.98, "Что я могу сделать прямо сейчас\nЭкологические действия и их влияние", 
        ha="center", va="center", fontsize=16, weight="bold",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#c8e6c9", edgecolor="#2e7d32", linewidth=2))

for label, (x, y) in nodes.items():
    draw_node(ax, label, x, y)

for start, end, label in edges:
    draw_edge(ax, start, end, label)

legend_elements = [
    plt.Line2D([0], [0], color="#4caf50", lw=2, label="Положительное влияние (снижает, защищает)"),
    plt.Line2D([0], [0], color="#ff9800", lw=2, label="Формирует, мотивирует"),
    plt.Line2D([0], [0], color="#2196f3", lw=2, label="Связано, влияет"),
    plt.Line2D([0], [0], color="#f44336", lw=2, label="Негативное влияние (угрожает)"),
]

ax.legend(handles=legend_elements, loc="lower left", fontsize=9, frameon=True, 
          bbox_to_anchor=(0.02, 0.02), framealpha=0.9)

plt.savefig("WORK/eco_actions/images/ontology.png", dpi=300, bbox_inches="tight", facecolor="white")
plt.close()
