from __future__ import annotations

import argparse
import json
import ssl
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error, parse, request


ROOT_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = ROOT_DIR / "gigachat_config.json"
DEFAULT_CONCEPTS_GLOB = "WORK/**/concepts.json"
DEFAULT_TIMEOUT_SECONDS = 120


@dataclass
class GigaChatConfig:
    authorization_key: str
    scope: str = "GIGACHAT_API_PERS"
    model: str = "GigaChat-2"
    temperature: float = 0.7
    max_tokens: int = 1800
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS
    verify_ssl: bool = True
    sleep_between_requests_seconds: float = 1.0
    token_url: str = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    chat_url: str = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"


@dataclass
class ThemeConcept:
    concept_name: str
    output_path: Path


@dataclass
class ThemeInfo:
    concepts_json_path: Path
    readme_path: Path | None
    theme_title: str
    theme_key: str
    output_dir: Path
    concepts: list[ThemeConcept]


class GigaChatClient:
    def __init__(self, config: GigaChatConfig) -> None:
        self.config = config
        self._access_token: str | None = None
        self._expires_at_ms: int = 0

    def _build_ssl_context(self) -> ssl.SSLContext | None:
        if self.config.verify_ssl:
            return None
        return ssl._create_unverified_context()

    def _request_json(
        self,
        url: str,
        *,
        headers: dict[str, str],
        data: bytes | None = None,
    ) -> dict[str, Any]:
        req = request.Request(url=url, headers=headers, data=data, method="POST")
        try:
            with request.urlopen(
                req,
                timeout=self.config.timeout_seconds,
                context=self._build_ssl_context(),
            ) as response:
                raw = response.read().decode("utf-8")
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"HTTP {exc.code} for {url}: {body}"
            ) from exc
        except error.URLError as exc:
            raise RuntimeError(f"Network error for {url}: {exc}") from exc

        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Invalid JSON from {url}: {raw}") from exc

    def _refresh_access_token(self) -> None:
        payload = parse.urlencode({"scope": self.config.scope}).encode("utf-8")
        headers = {
            "Authorization": f"Basic {self.config.authorization_key}",
            "RqUID": str(uuid.uuid4()),
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }
        data = self._request_json(self.config.token_url, headers=headers, data=payload)
        token = data.get("access_token")
        expires_at = data.get("expires_at", 0)
        if not token:
            raise RuntimeError(f"Token response does not contain access_token: {data}")
        self._access_token = str(token)
        self._expires_at_ms = int(expires_at) if expires_at else int(time.time() * 1000) + 25 * 60 * 1000

    def _get_access_token(self) -> str:
        now_ms = int(time.time() * 1000)
        if self._access_token and now_ms < self._expires_at_ms - 60_000:
            return self._access_token
        self._refresh_access_token()
        if not self._access_token:
            raise RuntimeError("Failed to obtain access token.")
        return self._access_token

    def generate_markdown(self, system_prompt: str, user_prompt: str) -> str:
        token = self._get_access_token()
        payload = {
            "model": self.config.model,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        data = self._request_json(
            self.config.chat_url,
            headers=headers,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        )
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"Unexpected completion response: {data}") from exc
        return str(content).strip()


def load_config(config_path: Path) -> GigaChatConfig:
    if not config_path.exists():
        raise FileNotFoundError(
            f"Не найден конфиг {config_path}. "
            f"Создай его по образцу из {ROOT_DIR / 'gigachat_config.json.example'}."
        )

    raw = json.loads(config_path.read_text(encoding="utf-8"))
    authorization_key = str(raw.get("authorization_key", "")).strip()
    if not authorization_key:
        raise ValueError(
            f"В {config_path} должен быть заполнен authorization_key."
        )

    return GigaChatConfig(
        authorization_key=authorization_key,
        scope=str(raw.get("scope", "GIGACHAT_API_PERS")),
        model=str(raw.get("model", "GigaChat-2")),
        temperature=float(raw.get("temperature", 0.7)),
        max_tokens=int(raw.get("max_tokens", 1800)),
        timeout_seconds=int(raw.get("timeout_seconds", DEFAULT_TIMEOUT_SECONDS)),
        verify_ssl=bool(raw.get("verify_ssl", True)),
        sleep_between_requests_seconds=float(raw.get("sleep_between_requests_seconds", 1.0)),
        token_url=str(raw.get("token_url", "https://ngw.devices.sberbank.ru:9443/api/v2/oauth")),
        chat_url=str(raw.get("chat_url", "https://gigachat.devices.sberbank.ru/api/v1/chat/completions")),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Генерирует markdown-статьи для всех тем из WORK/**/concepts.json через GigaChat API."
    )
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help="Путь до JSON-конфига с ключом GigaChat.",
    )
    parser.add_argument(
        "--theme",
        help="Фильтр по части пути темы, например moi_zavisimosti.",
    )
    parser.add_argument(
        "--concept",
        help="Сгенерировать только одну статью по названию понятия.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Перезаписывать существующие .md файлы.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Только показать, что было бы сгенерировано, без запросов в API.",
    )
    return parser.parse_args()


def extract_theme_title(readme_path: Path | None, fallback_dir_name: str) -> str:
    if readme_path and readme_path.exists():
        for line in readme_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith("# "):
                return stripped[2:].strip()
    return fallback_dir_name.replace("_", " ").strip()


def resolve_output_path(theme_dir: Path, mapped_path: str) -> Path:
    web_root = ROOT_DIR / "WEB"
    theme_relative = theme_dir.relative_to(ROOT_DIR / "WORK")
    expected_dir = web_root / theme_relative / "concepts"

    if mapped_path:
        candidate = (theme_dir / Path(mapped_path)).resolve()
        if candidate.parent == expected_dir:
            return candidate
        filename = Path(mapped_path).name
        return expected_dir / filename

    raise ValueError("Пустой путь статьи в concepts.json")


def discover_themes(theme_filter: str | None = None) -> list[ThemeInfo]:
    themes: list[ThemeInfo] = []
    for concepts_json_path in sorted(ROOT_DIR.glob(DEFAULT_CONCEPTS_GLOB)):
        theme_dir = concepts_json_path.parent
        theme_key = str(theme_dir.relative_to(ROOT_DIR / "WORK")).replace("\\", "/")

        if theme_filter and theme_filter not in theme_key:
            continue

        raw = json.loads(concepts_json_path.read_text(encoding="utf-8"))
        categories = raw.get("categories", {})
        if not isinstance(categories, dict):
            raise ValueError(f"Некорректный формат categories в {concepts_json_path}")

        concepts: list[ThemeConcept] = []
        for concept_name, mapped_path in categories.items():
            if not isinstance(concept_name, str) or not isinstance(mapped_path, str):
                raise ValueError(f"Некорректная запись в {concepts_json_path}: {concept_name}")
            output_path = resolve_output_path(theme_dir, mapped_path)
            concepts.append(ThemeConcept(concept_name=concept_name, output_path=output_path))

        readme_path = theme_dir / "README.md"
        theme_title = extract_theme_title(readme_path if readme_path.exists() else None, theme_dir.name)
        output_dir = ROOT_DIR / "WEB" / theme_dir.relative_to(ROOT_DIR / "WORK") / "concepts"
        themes.append(
            ThemeInfo(
                concepts_json_path=concepts_json_path,
                readme_path=readme_path if readme_path.exists() else None,
                theme_title=theme_title,
                theme_key=theme_key,
                output_dir=output_dir,
                concepts=concepts,
            )
        )
    return themes


def build_system_prompt() -> str:
    return (
        "Ты пишешь статьи для подростковой энциклопедии на русском языке. "
        "Пиши тепло, ясно и без занудства. Объясняй сложные вещи просто, "
        "как умный и доброжелательный наставник. Не пугай читателя и не читай нотации. "
        "Не используй медицинские назначения и не выдавай опасные инструкции. "
        "Формат ответа: только готовая Markdown-статья без пояснений вне статьи."
    )


def build_user_prompt(theme: ThemeInfo, concept_name: str, sibling_concepts: list[str]) -> str:
    related = ", ".join(sibling_concepts) if sibling_concepts else "нет"
    return (
        "Ты — дружелюбный эксперт, который объясняет сложные вещи детям 10 лет.\n"
        f"Задача: Напиши статью на тему {theme.theme_title} для подростковой энциклопедии.\n"
        "Требования:\n"
        "1. Язык: простой, дружелюбный, без сложных терминов (или с пояснениями), термины, описанные в других статьях указаны ниже\n"
        "2. Стиль: как будто объясняешь другу, можно с юмором и примерами из жизни.\n"
        "3. Структура:\n"
        "- Заголовок (цепляющий, не скучный)\n"
        "- Введение (почему это важно именно для подростка)\n"
        "- Основная часть (2-3 ключевых факта с примерами)\n"
        "- Практические советы (что можно сделать прямо сейчас)\n"
        "- Заключение (позитивный вывод)\n"
        "1. Объём: 500-1000 слов\n"
        "2. Формат: Markdown (используй # для заголовков, жирный для акцентов, списки)"
        "Важно:\n"
        "- Не пугай, не запугивай\n"
        "- Не давай медицинских рекомендаций, только общую информацию\n"
        "- Если упоминаешь проблемы — обязательно пиши, куда обратиться за помощью\n"
        f"Термины из других статей, на которые можно сослаться: {concept_name}\n"
        f"Тема: {theme.theme_title}."
    )


def normalize_markdown(markdown: str, concept_name: str) -> str:
    content = markdown.strip()
    if content.startswith("```"):
        parts = content.split("```")
        non_empty = [part.strip() for part in parts if part.strip() and part.strip().lower() != "markdown"]
        if non_empty:
            content = non_empty[0]
    if not content.startswith("#"):
        content = f"# {concept_name}\n\n{content}"
    return content.strip() + "\n"


def generate_for_theme(
    client: GigaChatClient,
    theme: ThemeInfo,
    *,
    overwrite: bool,
    dry_run: bool,
    concept_filter: str | None,
    sleep_seconds: float,
) -> tuple[int, int]:
    generated = 0
    skipped = 0
    theme.output_dir.mkdir(parents=True, exist_ok=True)

    all_concepts = [item.concept_name for item in theme.concepts]
    print(f"\nТема: {theme.theme_key}")
    print(f"Папка вывода: {theme.output_dir}")

    for item in theme.concepts:
        if concept_filter and concept_filter.casefold() != item.concept_name.casefold():
            continue

        if item.output_path.exists() and not overwrite:
            skipped += 1
            print(f"  [skip] {item.concept_name} -> {item.output_path.name} уже существует")
            continue

        print(f"  [gen ] {item.concept_name} -> {item.output_path.name}")
        if dry_run:
            generated += 1
            continue

        siblings = [name for name in all_concepts if name != item.concept_name]
        markdown = client.generate_markdown(
            build_system_prompt(),
            build_user_prompt(theme, item.concept_name, siblings),
        )
        item.output_path.parent.mkdir(parents=True, exist_ok=True)
        item.output_path.write_text(
            normalize_markdown(markdown, item.concept_name),
            encoding="utf-8",
        )
        generated += 1
        time.sleep(sleep_seconds)

    return generated, skipped


def main() -> int:
    args = parse_args()
    config = load_config(Path(args.config))
    themes = discover_themes(args.theme)

    if not themes:
        print("Не найдено ни одной темы с concepts.json.")
        return 1

    client = GigaChatClient(config)
    total_generated = 0
    total_skipped = 0

    for theme in themes:
        generated, skipped = generate_for_theme(
            client,
            theme,
            overwrite=args.overwrite,
            dry_run=args.dry_run,
            concept_filter=args.concept,
            sleep_seconds=config.sleep_between_requests_seconds,
        )
        total_generated += generated
        total_skipped += skipped

    mode = "DRY-RUN" if args.dry_run else "DONE"
    print(f"\n{mode}: сгенерировано {total_generated}, пропущено {total_skipped}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nОстановлено пользователем.")
        raise SystemExit(130)
    except Exception as exc:
        print(f"\nОшибка: {exc}", file=sys.stderr)
        raise SystemExit(1)
