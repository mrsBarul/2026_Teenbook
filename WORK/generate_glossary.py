#!/usr/bin/env python3
"""
словарь терминов: 
1) выводит все термины из wikidata_export.json с их wikidata_id и определением (термины без определений пропускаются)
2) сопоставляет concepts.json с wikidata_export.json и добавляет ссылки на статьи, в которых встречается термин (если есть совпадение)
"""

import json
import pathlib
import re
from collections import defaultdict

STOP_WORDS = {
    'или', 'и', 'в', 'на', 'с', 'по', 'для', 'что', 'это', 'как', 'не', 'но',
    'за', 'из', 'о', 'об', 'от', 'до', 'уже', 'еще', 'все', 'было', 'будет',
    'чем', 'когда', 'где', 'куда', 'откуда', 'почему', 'зачем', '—',
    'то', 'так', 'вот', 'ли', 'же', 'кто', 'чего', 'чтобы', 'если',
    'только', 'даже', 'ведь', 'потому', 'поэтому', 'который', 'которая',
    'которое', 'которые', 'можно', 'нельзя', 'нужно', 'надо', 'очень',
    'всегда', 'никогда', 'иногда', 'часто', 'редко'
}


def get_sections():
    work_dir = pathlib.Path(__file__).resolve().parent.parent
    sections = []
    for level1 in work_dir.iterdir():
        if level1.is_dir() and level1.name != "scripts":
            for level2 in level1.iterdir():
                if level2.is_dir():
                    sections.append(level2)
    return sections


def load_wikidata(filepath):
    descriptions = {}
    items = []
    
    if not filepath.exists():
        return descriptions, items
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for binding in data.get("results", {}).get("bindings", []):
        uri = binding.get("item", {}).get("value", "")
        if not uri.startswith("http://www.wikidata.org/entity/Q"):
            continue
        
        wd_id = uri.split("/")[-1]
        label = binding.get("itemLabel", {}).get("value", "")
        description = binding.get("description", {}).get("value", "")
        
        if not label:
            continue
        
        # исключаем английские термины
        if re.search(r'[a-zA-Z]', label):
            continue
        
        term_data = {"id": wd_id, "label": label, "description": description}
        
        descriptions[wd_id] = term_data
        descriptions[label.lower()] = term_data
        
        if label.endswith(('а', 'я')):
            descriptions[label[:-1]] = term_data
        if label.endswith('ие'):
            descriptions[label[:-2]] = term_data
        
        items.append({
            "id": wd_id,
            "label": label,
            "description": description,
            "label_lower": label.lower()
        })
    
    return descriptions, items


def get_keywords(text):
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    words = [w for w in text.split() if w not in STOP_WORDS and len(w) > 2]
    
    phrases = []
    for i in range(len(words)):
        for j in range(i + 1, min(i + 4, len(words) + 1)):
            phrase = ' '.join(words[i:j])
            if len(phrase) > 3:
                phrases.append(phrase)
    
    keywords = list(set(words + phrases))
    
    simplified = []
    for kw in keywords:
        if kw.endswith(('а', 'я')):
            simplified.append(kw[:-1])
        if kw.endswith('ие'):
            simplified.append(kw[:-2])
        if kw.endswith('ь'):
            simplified.append(kw[:-1])
    
    keywords.extend(simplified)
    return list(set(keywords))


def match_score(term, article, keywords):
    """три уровня соотвествия:
    3 - прямое вхождение термина в навзвание статьи
    2 - общие ключевые слова (+1/3 или 2/3 в зависимости от количества общих ключ. слов)
    0 - нет совпадений"""
    term_lower = term.lower()
    article_lower = article.lower()
    
    if term_lower in article_lower:
        return 3 
    
    term_keywords = get_keywords(term_lower)
    common = set(keywords) & set(term_keywords)
    if common:
        return 2 + min(1, len(common) / 3)
    
    return 0


def find_best_match(title, descriptions, items):
    keywords = get_keywords(title)
    
    candidates = []
    
    for term_str, term_data in descriptions.items():
        if isinstance(term_str, str) and len(term_str) > 2:
            score = match_score(term_str, title, keywords)
            if score > 0:
                candidates.append((score, len(term_str), term_data))
    
    if not candidates:
        for item in items:
            score = match_score(item["label_lower"], title, keywords)
            if score > 0:
                candidates.append((score, len(item["label"]), item))
    
    if not candidates:
        return None
    
    candidates.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return candidates[0][2]


def get_terms_from_section(section_path):
    concepts_file = section_path / "concepts.json"
    wikidata_file = section_path / "data" / "wikidata_export.json"
    
    descriptions, items = load_wikidata(wikidata_file)
    
    articles_by_term = defaultdict(list)
    if concepts_file.exists():
        with open(concepts_file, 'r', encoding='utf-8') as f:
            concepts_data = json.load(f)
        
        if isinstance(concepts_data, dict):
            concepts = concepts_data.get("concepts", concepts_data.get("topics", []))
        else:
            concepts = concepts_data
        
        for concept in concepts:
            if not isinstance(concept, dict):
                continue
            
            title = concept.get("name") or concept.get("label") or concept.get("title", "")
            if not title:
                continue
            
            wd_match = None
            wd_id = concept.get("wikidata_id")
            if wd_id and wd_id in descriptions:
                wd_match = descriptions[wd_id]
            
            if not wd_match:
                wd_match = find_best_match(title, descriptions, items)
            
            if wd_match:
                articles_by_term[wd_match["label"]].append({
                    "title": title,
                    "section": section_path.name,
                    "topic": section_path.parent.name,
                    "file": concept.get("file", "")
                })
    
    # список всех(!) терминов из wikidata
    terms = []
    for item in items:
        terms.append({
            "term_label": item["label"],
            "wikidata_id": item["id"],
            "description": item["description"],
            "articles": articles_by_term.get(item["label"], []) # если есть сопвадение со статьей, добавить ссылку на статью
        })
    
    return terms


def collect_all_terms():
    all_terms = []
    sections = get_sections()
    
    for section_path in sections:
        all_terms.extend(get_terms_from_section(section_path))
    
    grouped = {}
    for term in all_terms:
        label = term["term_label"]
        if label not in grouped:
            grouped[label] = {
                "term": label,
                "descriptions": set(),
                "wikidata_ids": set(),
                "articles": []
            }
        
        grouped[label]["descriptions"].add(term["description"])
        grouped[label]["wikidata_ids"].add(term["wikidata_id"])
        grouped[label]["articles"].extend(term["articles"])
    
    result = []
    for label, data in grouped.items():
        unique_articles = {}
        for article in data["articles"]:
            unique_articles[article["title"]] = article
        
        best_description = ""
        for desc in data["descriptions"]:
            if len(desc) > len(best_description):
                best_description = desc
        
        #  если хотим убрать из словаря термины у которых нет определения        
        if not best_description:
                    continue
        
        result.append({
            "term": label,
            "description": best_description,
            "wikidata_ids": list(data["wikidata_ids"]),
            "articles": sorted(unique_articles.values(), key=lambda x: x["title"])
        })
    
    result.sort(key=lambda x: x["term"].lower())
    return result


def generate_markdown(terms, output_path="WEB/glossary.md"):
    if not terms:
        print("Нет найденных терминов.")
        return
    
    by_letter = defaultdict(list)
    for term in terms:
        first_letter = term["term"][0].upper()
        by_letter[first_letter].append(term)
    
    # frontmatter для jekyll
    md = "---\ntitle: Словарь терминов\n---\n" 
    letters = sorted(by_letter.keys())
    md += " ".join([f"[{letter}](#{letter.lower()})" for letter in letters])
    md += "\n\n---\n\n"
    
    for letter in letters:
        md += f"## {letter}\n\n"
        
        for term in by_letter[letter]:
            md += f"### {term['term']}\n\n"
            
            if term["description"]:
                md += f"{term['description']}\n\n"
            else:
                md += "*Определение в экспортированных данных Wikidata отсутствует. Пожалуйста, дополните соответствующий термин в Wikidata.*\n\n"
            
            if term["wikidata_ids"]:
                if len(term["wikidata_ids"]) == 1:
                    md += f"**Wikidata:** [{term['wikidata_ids'][0]}](https://www.wikidata.org/entity/{term['wikidata_ids'][0]})\n\n"
                else:
                    links = ", ".join([f"[{wid}](https://www.wikidata.org/entity/{wid})" for wid in term["wikidata_ids"]])
                    md += f"**Wikidata:** {links}\n\n"
            
            if term["articles"]:
                md += f"**Встречается в статьях:**\n\n"
                for article in term["articles"]:
                    filename = article["file"] or f"{article['title'].lower().replace(' ', '_')}.md"
                    path = f"/{article['topic']}/{article['section']}/concepts/{filename.replace('.md', '.html')}" # т.к. jekyll преобразует md в html 
                    md += f"- [{article['title']}]({path}) – *{article['section']}*\n"
                md += "\n"
            else:
                pass
                # md += f"*Термин не встречается в статьях.*\n\n"
            
            md += "\n---\n\n"
    
    md += "\n*Словарь сгенерирован автоматически на основе Wikidata*\n"
    
    output_file = pathlib.Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md)
    
    print(f"Словарь сохранен: {output_path}")
    print(f"Всего уникальных терминов: {len(terms)}")
    print(f"Всего связей статей с терминами: {sum(len(t['articles']) for t in terms)}")


def main():
    terms = collect_all_terms()
    generate_markdown(terms)


if __name__ == "__main__":
    main()