---
layout: default
---

# Тест Jekyll

Текущее время: {{ site.time }}

Количество статей: {{ site.pages | size }}

Список всех файлов:
<ul>
{% for page in site.pages %}
  <li>{{ page.path }} ({{ page.ext }})</li>
{% endfor %}
</ul>


# 📚 TeenBook

Добро пожаловать в энциклопедию знаний!

## Все статьи

<div class="articles-grid">
{% assign articles = site.pages | where_exp: "page", "page.path contains '/WEB/'" | where_exp: "page", "page.ext == '.md'" | sort: "path" %}
{% for article in articles %}
  {% assign title = article.name | replace: "_", " " | replace: ".md", "" | capitalize %}
  {% assign path_parts = article.path | split: "/" %}
  {% assign category = path_parts[1] | replace: "-", " " | capitalize %}
  <div class="card">
    <h3>{{ title }}</h3>
    <p class="category">{{ category }}</p>
    <a href="{{ article.url | relative_url }}">Читать →</a>
  </div>
{% endfor %}
</div>

<style>
  .articles-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
  }
  .card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  }
  .card h3 {
    margin: 0 0 0.5rem;
    color: #2c3e50;
  }
  .category {
    color: #667eea;
    font-size: 0.8rem;
    text-transform: uppercase;
    margin-bottom: 1rem;
  }
  .card a {
    color: #667eea;
    text-decoration: none;
  }
  h1 {
    color: #2c3e50;
  }
</style>