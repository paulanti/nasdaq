## Установка

python >=3.6

Если используется pipenv

`$ pipenv shell`
`$ pipenv install --dev`

Если нет, то

`$ pip install -r requirements.txt`

Не забыть поменять настройки БД в `config/settings/local.py`

## Запуск парсера

`$ python manage.py start_parsing n` , где n - кол-во потоков

#### Пример url для страницы с данными о разнице цен

[/cvx/analytics/?date_from=2018-02-08&date_to=2018-02-12](cvx/analytics/?date_from=2018-02-08&date_to=2018-02-12)

[/api/cvx/analytics/?date_from=2018-02-08&date_to=2018-02-12](/api/cvx/analytics/?date_from=2018-02-08&date_to=2018-02-12)

#### Пример url для страницы с данными о минимальных периодах, когда указанная цена изменилась более чем на N

[/cvx/delta/?value=11&type=open](/cvx/delta/?value=11&type=open)

[/api/cvx/delta/?value=11&type=open](/cvx/delta/?value=11&type=open)

