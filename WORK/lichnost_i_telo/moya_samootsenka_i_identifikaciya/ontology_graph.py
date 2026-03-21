"""
Тот же смысл, что в ontology.md, в виде данных для кода.
"""

EDGES: list[tuple[str, str, str]] = [
    ("kto_ya", "mnenie_drugih", "влияет_на"),
    ("kto_ya", "sravnenie", "влияет_на"),
    ("mnenie_drugih", "sravnenie", "усиливает"),
    ("sravnenie", "kto_ya", "снижает_самооценку"),
    ("byt_soboi", "kto_ya", "развивает"),
    ("byt_soboi", "silnye_storony", "помогает_заметить"),
    ("silnye_storony", "kto_ya", "поддерживает"),
    ("silnye_storony", "mnenie_drugih", "снижает_зависимость"),
]

NODE_TITLES = {
    "kto_ya": "Кто я / идентичность",
    "mnenie_drugih": "Мнение других",
    "sravnenie": "Сравнение с другими",
    "byt_soboi": "Быть собой",
    "silnye_storony": "Сильные стороны / без лайков",
}
