import json
import pathlib
import networkx as nx
import matplotlib.pyplot as plt


def load_data(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_graph(data):
    G = nx.DiGraph()

    for item in data["results"]["bindings"]:
        source = item["sourceLabel"]["value"]
        target = item["targetLabel"]["value"]
        prop = item["propertyLabel"]["value"]

        # 🔥 фильтр мусора (очень важно)
        if source == target:
            continue

        G.add_node(source)
        G.add_node(target)
        G.add_edge(source, target, label=prop)

    return G


def draw_graph(G, output_path):
    plt.figure(figsize=(16, 12))

    pos = nx.spring_layout(G, k=1.5, iterations=150, seed=42)

    nx.draw(
        G,
        pos,
        with_labels=True,
        node_size=3000,
        node_color="#A7D8F0",
        font_size=9,
        font_weight="bold",
        arrows=True
    )

    edge_labels = nx.get_edge_attributes(G, "label")

    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=edge_labels,
        font_size=7
    )

    # 🔥 поменяли заголовок
    plt.title("Граф знаний Wikidata: Раздельный сбор и переработка", fontsize=16)

    plt.axis("off")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def main():
    script_dir = pathlib.Path(__file__).parent
    json_path = script_dir.parent / "data" / "wikidata_export_contact.json"
    output_path = script_dir.parent / "images" / "wikidata_graph.png"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = load_data(json_path)
    G = build_graph(data)
    draw_graph(G, output_path)

    print(f"Готово: граф сохранён в {output_path}")


if __name__ == "__main__":
    main()