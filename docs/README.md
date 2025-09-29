# FineRP: Документація

Ця директорія містить документацію проекту FineRP, побудовану з використанням Sphinx.

## Налаштування середовища для роботи з документацією

1. Встановіть Python 3.8 або новіше
2. Встановіть необхідні залежності:
   ```bash
   pip install -r requirements.txt

## Структура документації проекту FineRP з використанням Sphinx

repo_root/
│── docs/
│   ├── Makefile                  # Makefile для збірки документації (Linux/Mac)
│   ├── make.bat                  # Batch-файл для збірки документації (Windows)
│   ├── requirements.txt          # Залежності для документації
│   │
│   ├── source/                   # Вихідні файли документації
│   │   ├── conf.py               # Конфігурація Sphinx
│   │   ├── index.rst             # Головна сторінка документації
│   │   │
│   │   ├── _static/              # Статичні файли (CSS, JS, зображення)
│   │   │   └── custom.css        # Кастомні стилі
│   │   ├── _templates/           # Кастомні шаблони Sphinx
│   │   │
│   │   ├── en/                   # Англомовна документація
│   │   │   ├── index.rst         # Головна сторінка англомовної документації
│   │   │   ├── architecture/     # Архітектура проекту
│   │   │   │   ├── index.rst     # Зміст розділу
│   │   │   │   ├── overview.rst  # Загальний огляд архітектури
│   │   │   │   └── decisions.rst # Архітектурні рішення (ADR)
│   │   │   ├── api/              # API документація
│   │   │   │   ├── index.rst     # Зміст API-документації
│   │   │   │   └── endpoints.rst # Опис API ендпоінтів
│   │   │   └── contributing.rst  # Гайд для контриб'юторів
│   │   │
│   │   ├── uk/                   # Українська документація (детальніша)
│   │   │   ├── index.rst         # Головна сторінка української документації
│   │   │   ├── architecture/     # Опис архітектури
│   │   │   │   ├── index.rst     # Зміст розділу архітектури
│   │   │   │   ├── overview.rst  # Загальний огляд
│   │   │   │   ├── backend.rst   # Бекенд архітектура
│   │   │   │   ├── frontend.rst  # Фронтенд архітектура
│   │   │   ├── components/       # Опис компонентів системи
│   │   │   │   ├── index.rst     # Зміст розділу компонентів
│   │   │   │   ├── taxpayers.rst # Компонент "Платники податків"
│   │   │   │   ├── banks.rst     # Компонент "Банки і рахунки"
│   │   │   │   ├── finops.rst    # Компонент "Фінансові операції"
│   │   │   │   ├── income_book.rst # Компонент "Книга доходів"
│   │   │   │   └── tax_reports.rst # Компонент "Податкові звіти"
│   │   │   ├── development/      # Розробка
│   │   │   │   ├── index.rst     # Зміст розділу розробки
│   │   │   │   ├── setup.rst     # Налаштування середовища
│   │   │   │   ├── tests.rst     # Написання тестів
│   │   │   │   └── deployment.rst # Деплой проекту
│   │   │   ├── api/              # API документація
│   │   │   │   ├── index.rst     # Зміст API-документації
│   │   │   │   └── endpoints.rst # Детальний опис API
│   │   │   └── user_guides/      # Посібники користувача
│   │   │       ├── index.rst     # Зміст розділу посібників
│   │   │       ├── getting_started.rst # Початок роботи
│   │   │       └── reports.rst    # Робота зі звітами
│   │   │
│   │   ├── _ext/                 # Розширення Sphinx
│   │   │   └── custom_extension.py # Власне розширення (якщо потрібно)
│   │   │
│   │   └── _templates_rst/       # Шаблони для нових документів RST
│   │       ├── component_template.rst # Шаблон опису компонента
│   │       └── adr_template.rst  # Шаблон для Architecture Decision Record
│   │
│   ├── build/                    # Директорія з зібраною документацією (створюється автоматично)
│   │   ├── html/                 # HTML-документація
│   │   ├── pdf/                  # PDF-документація
│   │   └── epub/                 # EPUB-документація
│   │
│   └── README.md                 # Інструкції по роботі з документацією

## використання PlantUML діаграм

Для використання PlantUML діаграм, встановіть Java та завантажте PlantUML JAR

### Для Linux/Mac
sudo apt-get install default-jre  # для Debian/Ubuntu
### або
brew install openjdk  # для macOS з Homebrew

### Завантажте PlantUML
mkdir -p ~/bin
wget https://sourceforge.net/projects/plantuml/files/plantuml.jar/download -O ~/bin/plantuml.jar

Потім оновіть шлях до PlantUML у файлі source/conf.py

## Збірка документації

### Linux/Mac:
cd docs
make html  # для HTML
make pdf   # для PDF
make epub  # для EPUB

### Windows:
cd docs
make.bat html  # для HTML
make.bat pdf   # для PDF
make.bat epub  # для EPUB

### Для автоматичної генерації документації з docstrings
sphinx-apidoc -o source/api/ ../sc_backend/djapps/