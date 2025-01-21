## Описание:

Парсер, выполняющий сбор информации о:
- статьях о нововведениях в Python и их авторах и редакторах .
- статусах версий Python.
- статусах PEP, подсчет количества PEP в каждом статусе.
- также реализована функция скачивания архива с актуальной документацией Python.

## Как запустить проект локально:
1. Клонировать репозиторий:
```
git clone https://github.com/VyacheslavGizov/bs4_parser_pep.git
```
2. В корневой папке создать и активировать виртуальное окружение, установить зависимости:
```
cd bs4_parser_pep/
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```
3. Перейти в директорию ./src/ и запустить main.py с необходимыми параметрами:
```
python main.py [режим работы] [аргументы]
```
## Режимы работы парсера:
1. whats-new  - ссылки на статьи о нововведениях, заголовки, авторы и редакторы.
2. latest_versions - ссылки на документацию, версии, статусы.
3. pep - количество PEP в каждом статусе и общее колиество PEP.
4. download - загрузка архива с документацией Python в ./downloads/

## Аргументы:
1. -h, --help - информация о командах
```
python main.py -h
```
2. -c, --clear-cache - очистка кеша перед выполнением парсинга.

```
python main.py [режим работы] -c
```
3. -o {pretty,file}, --output {pretty,file} - способы вывода данных:
- pretty - вывод в терминал в табличном виде.
- file - сохранение результатов в формате .csv в ./results/
```
python main.py [режим работы] -o pretty
python main.py [режим работы] -o file
```

## Авторы:
- [ЯП](https://github.com/yandex-praktikum);
- [Vyacheslav Gizov](https://github.com/VyacheslavGizov).


