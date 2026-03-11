import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

nodes = {
    "Подросток": (0.5, 0.92),
    "Родитель": (0.15, 0.72),
    "Общение": (0.85, 0.72),
    "Конфликт": (0.5, 0.55),
    "Ссора": (0.15, 0.38),
    "Агрессия": (0.85, 0.38),
    "Социальная сеть": (0.85, 0.18),
    "Гордость": (0.15, 0.18),
    "Примирение": (0.5, 0.18),
    "Эмпатия": (0.28, 0.02),
    "Прощение": (0.72, 0.02),
}

edges = [
    ("Подросток", "Родитель", "взаимодействует с"),
    ("Подросток", "Общение", "участвует в"),
    ("Подросток", "Конфликт", "участвует в"),
    ("Общение", "Конфликт", "может приводить к"),
    ("Конфликт", "Ссора", "проявляется как"),
    ("Конфликт", "Агрессия", "может вызывать"),
    ("Конфликт", "Примирение", "разрешается через"),
    ("Гордость", "Примирение", "может мешать"),
    ("Эмпатия", "Примирение", "способствует"),
    ("Примирение", "Прощение", "включает"),
    ("Социальная сеть", "Конфликт", "среда для"),
]


def draw_node(ax, label, x, y, w=0.24, h=0.09):
    box = FancyBboxPatch(
        (x - w / 2, y - h / 2),
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.02",
        linewidth=1.5,
        edgecolor="black",
        facecolor="white"
    )
    ax.add_patch(box)
    ax.text(x, y, label, ha="center", va="center", fontsize=11)


def draw_edge(ax, start, end, text):
    x1, y1 = nodes[start]
    x2, y2 = nodes[end]

    ax.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle="->",
            lw=1.4,
            shrinkA=20,
            shrinkB=20
        )
    )

    mx = (x1 + x2) / 2
    my = (y1 + y2) / 2
    ax.text(mx, my + 0.025, text, ha="center", va="center", fontsize=9)


fig, ax = plt.subplots(figsize=(12, 8))
ax.set_xlim(0, 1)
ax.set_ylim(-0.05, 1)
ax.axis("off")

for label, (x, y) in nodes.items():
    draw_node(ax, label, x, y)

for start, end, label in edges:
    draw_edge(ax, start, end, label)

plt.savefig("../images/ontology.png", dpi=300, bbox_inches="tight")
plt.close()

print("Схема сохранена в ../images/ontology.png")
