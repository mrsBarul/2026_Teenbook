from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SECTION = ROOT / "WORK" / "ya_i_cifrovoy_mir"
WEB = ROOT / "WEB" / "ya_i_cifrovoy_mir"
TOPICS = ['moya_zavisimost', 'moi_igry', 'moya_informacionnaya_gigiena', 'moya_bezopasnost_v_seti', 'moya_realnost_i_virtualnost', 'moya_tehnika']

required_work_files = [
    "README.md",
    "concepts.json",
    "images/ontology.png",
    "scripts/sparql_queries.py",
    "data/wikidata_export.json",
    "data/dbpedia_export.json",
]


def check() -> int:
    missing = []
    for topic in TOPICS:
        base = SECTION / topic
        for rel in required_work_files:
            path = base / rel
            if not path.exists():
                missing.append(path)
        web_dir = WEB / topic / "concepts"
        if not web_dir.exists() or not any(web_dir.glob("*.md")):
            missing.append(web_dir)
    if missing:
        print("Не хватает файлов или папок:")
        for item in missing:
            print("-", item.relative_to(ROOT))
        return 1
    print("Структура репозитория выглядит полной.")
    return 0


if __name__ == "__main__":
    raise SystemExit(check())
