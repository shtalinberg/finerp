# Configuration file for the Sphinx documentation builder.

import datetime
import os
import sys

# Щоб мати доступ до коду проекту для autodoc
sys.path.insert(0, os.path.abspath('../..'))

# Основні налаштування проекту
project = 'FineRP'
copyright = f'{datetime.datetime.now().year}, FineRP Team'
author = 'FineRP Team'
release = '0.1.0'

# Розширення, які використовуються
extensions = [
    'sphinx.ext.autodoc',        # Автодокументація з docstrings
    'sphinx.ext.napoleon',       # Підтримка Google/NumPy стилів docstrings
    'sphinx.ext.viewcode',       # Додає посилання на вихідний код
    'sphinx.ext.intersphinx',    # Посилання на зовнішні документації
    'sphinx_rtd_theme',          # Тема Read the Docs
    'sphinx.ext.graphviz',       # Підтримка діаграм Graphviz
    'sphinxcontrib.plantuml',    # Підтримка PlantUML діаграм
    'sphinx.ext.todo',           # Підтримка TO-DO
    'sphinx.ext.ifconfig',       # Умовні директиви
    'sphinx.ext.githubpages',    # Для публікації на GitHub Pages
]

# Шаблони сторінок
templates_path = ['_templates']

# Файли, які потрібно виключити
exclude_patterns = []

# Мова за замовчуванням (en)
language = 'uk'  # можна змінити на 'en' за потреби

# HTML налаштування
html_theme = 'sphinx_rtd_theme'  # Використовуємо тему Read the Docs
html_static_path = ['_static']
html_css_files = ['custom.css']
html_logo = '_static/logo.png'  # Логотип проекту
html_favicon = '_static/favicon.ico'  # Фавікон

# LaTeX налаштування для PDF
latex_elements = {
    'preamble': r'''
    \usepackage[utf8]{inputenc}
    \usepackage[T1]{fontenc}
    \usepackage{babel}
    \usepackage{tgschola}
    '''
}

# Налаштування для підсвічування коду
pygments_style = 'sphinx'

# Налаштування для intersphinx (посилання на зовнішні документації)
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'django': ('https://docs.djangoproject.com/en/5.2/', None),
}

# Налаштування для PlantUML
plantuml = 'java -jar /path/to/plantuml.jar'

# Включаємо todo-блоки тільки в dev-режимі
todo_include_todos = True