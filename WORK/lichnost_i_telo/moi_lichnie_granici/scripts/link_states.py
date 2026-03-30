from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

DEFAULT_DRY_RUN = True
DEFAULT_MAKE_BACKUP = True
LINK_MAP_FILE = "link_map.json"


def resolve_paths() -> tuple[Path, Path]:
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parents[3]
    articles_root = project_root / "2026_TeenBook--"/ "WEB" / "lichnost_i_telo" / "moi_lichnie_granici" / "concepts"
    return script_dir, articles_root


def load_link_map(script_dir: Path) -> dict[str, list[str]]:
    link_map_path = script_dir / LINK_MAP_FILE

    if not link_map_path.exists():
        raise FileNotFoundError(f"Не найден файл словаря ссылок: {link_map_path}")

    with open(link_map_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError('link_map.json должен содержать объект вида {"file.md": ["термин1", "термин2"]}')

    validated: dict[str, list[str]] = {}
    for target_file, terms in data.items():
        if not isinstance(target_file, str):
            raise ValueError("Ключи link_map.json должны быть строками")
        if not isinstance(terms, list) or not all(isinstance(term, str) for term in terms):
            raise ValueError(f"Значение для {target_file} должно быть списком строк")
        validated[target_file] = terms

    return validated


def split_frontmatter(raw: str) -> tuple[str, str]:
    if raw.startswith("---\n"):
        match = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, flags=re.DOTALL)
        if match:
            return f"---\n{match.group(1)}\n---\n", match.group(2)
    return "", raw


def split_body_lines(body: str) -> list[str]:
    return body.splitlines(keepends=True)


def protect_regions(text: str) -> tuple[str, dict[str, str]]:
    placeholders: dict[str, str] = {}
    counter = 0

    patterns = [
        r"```.*?```",
        r"`[^`\n]+`",
        r"\[([^\]]+)\]\(([^)]+)\)",
    ]

    for pattern in patterns:
        def repl(match):
            nonlocal counter
            key = f"__PROTECTED_{counter}__"
            placeholders[key] = match.group(0)
            counter += 1
            return key

        text = re.sub(pattern, repl, text, flags=re.DOTALL)

    return text, placeholders


def restore_regions(text: str, placeholders: dict[str, str]) -> str:
    for key, value in placeholders.items():
        text = text.replace(key, value)
    return text


def build_relative_link(from_file: Path, to_file: Path) -> str:
    return Path(os.path.relpath(to_file, from_file.parent)).as_posix()


def is_heading_line(line: str) -> bool:
    return re.match(r"^\s*#{1,6}\s+", line) is not None


def replace_bold_term_all(
    text: str,
    term: str,
    rel_link: str,
    replacements_log: list[tuple[str, str]],
) -> str:
    pattern_star = re.compile(
        rf"(?<!\[)\*\*(?P<term>{re.escape(term)})\*\*(?!\])",
        flags=re.IGNORECASE
    )

    def repl_star(match):
        original = match.group(0)
        inner = match.group("term")
        replaced = f"[**{inner}**]({rel_link})"
        replacements_log.append((original, replaced))
        return replaced

    text = pattern_star.sub(repl_star, text)

    pattern_underscore = re.compile(
        rf"(?<!\[)__(?P<term>{re.escape(term)})__(?!\])",
        flags=re.IGNORECASE
    )

    def repl_underscore(match):
        original = match.group(0)
        inner = match.group("term")
        replaced = f"[__{inner}__]({rel_link})"
        replacements_log.append((original, replaced))
        return replaced

    text = pattern_underscore.sub(repl_underscore, text)

    return text


def replace_plain_term_all(
    text: str,
    term: str,
    rel_link: str,
    replacements_log: list[tuple[str, str]],
) -> str:
    pattern = re.compile(
        rf"(?<![\w\[\*`_]){re.escape(term)}(?![\w\]`_])",
        flags=re.IGNORECASE
    )

    def repl(match):
        original = match.group(0)
        replaced = f"[{original}]({rel_link})"
        replacements_log.append((original, replaced))
        return replaced

    return pattern.sub(repl, text)


def process_non_heading_line(
    line: str,
    article_path: Path,
    articles_root: Path,
    link_map: dict[str, list[str]],
) -> tuple[str, list[tuple[str, str]]]:
    protected_line, placeholders = protect_regions(line)
    updated = protected_line
    replacements_log: list[tuple[str, str]] = []

    for target_file_name, terms in link_map.items():
        target_path = articles_root / target_file_name

        if article_path.name == target_file_name:
            continue

        if not target_path.exists():
            print(f"Предупреждение: целевая статья не найдена: {target_path}")
            continue

        rel_link = build_relative_link(article_path, target_path)

        for term in sorted(terms, key=len, reverse=True):
            updated = replace_bold_term_all(updated, term, rel_link, replacements_log)
            updated = replace_plain_term_all(updated, term, rel_link, replacements_log)

    updated = restore_regions(updated, placeholders)
    return updated, replacements_log


def process_article(
    article_path: Path,
    articles_root: Path,
    link_map: dict[str, list[str]],
) -> tuple[str, str, list[tuple[str, str]]]:
    raw = article_path.read_text(encoding="utf-8")
    frontmatter, body = split_frontmatter(raw)

    lines = split_body_lines(body)
    processed_lines = []
    article_replacements: list[tuple[str, str]] = []

    for line in lines:
        if is_heading_line(line):
            processed_lines.append(line)
            continue

        processed_line, replacements_log = process_non_heading_line(
            line,
            article_path,
            articles_root,
            link_map,
        )
        processed_lines.append(processed_line)
        article_replacements.extend(replacements_log)

    new_body = "".join(processed_lines)
    return raw, frontmatter + new_body, article_replacements


def make_backup(article_path: Path) -> None:
    backup_path = article_path.with_suffix(article_path.suffix + ".bak")
    backup_path.write_text(
        article_path.read_text(encoding="utf-8"),
        encoding="utf-8"
    )


def run_processing(
    articles_root: Path,
    link_map: dict[str, list[str]],
    dry_run: bool,
    make_backup_enabled: bool,
) -> int:
    md_files = sorted(articles_root.glob("*.md"))
    changed = 0

    for article_path in md_files:
        old_content, new_content, replacements_log = process_article(article_path, articles_root, link_map)

        if old_content != new_content:
            changed += 1
            print(f"Изменения: {article_path.name}")

            unique_logs = []
            seen = set()
            for old, new in replacements_log:
                key = (old, new)
                if key not in seen:
                    seen.add(key)
                    unique_logs.append((old, new))

            for old, new in unique_logs:
                print(f'  - "{old}" -> {new}')

            if not dry_run:
                if make_backup_enabled:
                    make_backup(article_path)
                article_path.write_text(new_content, encoding="utf-8")

    return changed


def restore_backups(articles_root: Path) -> int:
    restored = 0

    for backup_path in sorted(articles_root.glob("*.md.bak")):
        original_path = backup_path.with_suffix("")
        original_path.write_text(
            backup_path.read_text(encoding="utf-8"),
            encoding="utf-8"
        )
        restored += 1
        print(f"Восстановлен файл: {original_path.name}")

    return restored


parser = argparse.ArgumentParser(
    description=(
        "Автолинковка markdown-статей по словарю терминов из link_map.json.\n\n"
        "Что делает скрипт:\n"
        "  1. Находит статьи в папке concepts\n"
        "  2. Читает link_map.json рядом со скриптом\n"
        "  3. Заменяет термины в тексте на markdown-ссылки\n"
        "  4. Не трогает front matter, заголовки, code blocks и существующие ссылки\n"
    ),
    epilog=(
        "Примеры запуска:\n"
        "  python3 link_states.py --help\n"
        "  python3 link_states.py --dry-run\n"
        "  python3 link_states.py --write\n"
        "  python3 link_states.py --write --no-backup\n"
        "  python3 link_states.py --yes\n"
        "  python3 link_states.py --restore-backups"
    ),
    formatter_class=argparse.RawTextHelpFormatter,
)
parser.add_argument(
    "--dry-run",
    action="store_true",
    help="Только показать изменения, не записывая в файлы."
)
parser.add_argument(
    "--write",
    action="store_true",
    help="Сразу записывать изменения в файлы."
)
parser.add_argument(
    "--no-backup",
    action="store_true",
    help="Не создавать .bak при записи."
)
parser.add_argument(
    "--restore-backups",
    action="store_true",
    help="Восстановить .md файлы из .bak и выйти."
)
parser.add_argument(
    "--yes",
    action="store_true",
    help="Не спрашивать подтверждение."
)

args = parser.parse_args()

script_dir, articles_root = resolve_paths()
link_map = load_link_map(script_dir)

if not articles_root.exists():
    raise FileNotFoundError(f"Папка не найдена: {articles_root}")

print(f"Скрипт:       {script_dir}")
print(f"Папка статей: {articles_root}")
print(f"Файл словаря: {script_dir / LINK_MAP_FILE}")
print()

if args.restore_backups:
    restored_count = restore_backups(articles_root)
    print(f"Готово. Восстановлено файлов: {restored_count}")
    raise SystemExit(0)

if args.dry_run and args.write:
    raise ValueError("Нельзя одновременно указать --dry-run и --write")

if args.write:
    DRY_RUN = False
elif args.dry_run:
    DRY_RUN = True
else:
    DRY_RUN = DEFAULT_DRY_RUN

MAKE_BACKUP = DEFAULT_MAKE_BACKUP and not args.no_backup

if args.write:
    changed_count = run_processing(
        articles_root=articles_root,
        link_map=link_map,
        dry_run=False,
        make_backup_enabled=MAKE_BACKUP,
    )
    print(f"Готово. Изменено файлов: {changed_count}")
    raise SystemExit(0)

if args.dry_run:
    changed_count = run_processing(
        articles_root=articles_root,
        link_map=link_map,
        dry_run=True,
        make_backup_enabled=MAKE_BACKUP,
    )
    print(f"DRY_RUN=True. Было бы изменено файлов: {changed_count}")
    raise SystemExit(0)

changed_count = run_processing(
    articles_root=articles_root,
    link_map=link_map,
    dry_run=True,
    make_backup_enabled=MAKE_BACKUP,
)
print(f"DRY_RUN=True. Было бы изменено файлов: {changed_count}")

if changed_count == 0:
    print("Изменений нет. Подтверждение не требуется.")
    raise SystemExit(0)

if args.yes:
    confirm = "y"
else:
    confirm = input("Применить изменения и записать файлы? [y/N]: ").strip().lower()

if confirm in {"y", "yes", "д", "да"}:
    changed_count = run_processing(
        articles_root=articles_root,
        link_map=link_map,
        dry_run=False,
        make_backup_enabled=MAKE_BACKUP,
    )
    print(f"Готово. Изменено файлов: {changed_count}")
else:
    print("Запись отменена.")