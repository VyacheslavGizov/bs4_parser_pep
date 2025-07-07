# bs4_parser_pep

Парсер, выполняющий сбор информации о:

- статьях о нововведениях в Python и их авторах и редакторах
- статусах версий Python
- статусах PEP, подсчет количества PEP в каждом статусе
- также реализована функция скачивания архива с актуальной документацией Python

---

## Как запустить проект локально

1. Клонировать репозиторий:

```bash
git clone https://github.com/VyacheslavGizov/bs4_parser_pep.git
```

2. В корневой папке создать и активировать виртуальное окружение, установить зависимости:

```bash
cd bs4_parser_pep/
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```

3. Перейти в директорию ./src/ и запустить **main.py** с необходимыми параметрами:

```bash
python main.py [режим работы] [аргументы]
```

---

## Режимы работы парсера

- `whats-new`  - ссылки на статьи о нововведениях, заголовки, авторы и редакторы
- `latest_versions` - ссылки на документацию, версии, статусы
- `pep` - количество PEP в каждом статусе и общее количество PEP
- `download` - загрузка архива с документацией Python в ./downloads/

---

## Аргументы

1. `-h`, `--help` - информация о командах

```bash
python main.py -h
```

2. `-c`, `--clear-cache` - очистка кэша перед выполнением парсинга

```bash
python main.py [режим работы] -c
```

3. `-o {pretty,file}`, `--output {pretty,file}` - способы вывода данных:

- `pretty` - вывод в терминал в табличном виде.
- `file` - сохранение результатов в формате .csv в ./results/

```bash
python main.py [режим работы] -o pretty
python main.py [режим работы] -o file
```

---

## Авторы

[Вячеслав Гизов](https://github.com/VyacheslavGizov)
