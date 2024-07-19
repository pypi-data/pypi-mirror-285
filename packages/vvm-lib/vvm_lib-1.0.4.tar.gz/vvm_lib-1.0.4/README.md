Устанавливается
pip install vvm-lib


Основные функции:
```
from vvm_lib.vault import read_secret_data
from vvm_lib.greenplum import postgres_query_read, insert_greenplum, select_postgres
from vvm_lib.google_book import get_google_sheets, update_worksheet, clear_worksheet
from vvm_lib.mssql import pymssql
from vvm_lib.db import DB #new version 1.0
```

read_secret_data:
 Функция для получения доступов из vault

    :param secret_path: Название секрета в DAS_team
    :param vault_token_env: токент доступа
    :param url: url vault
    :return: Словарь с секретами
 
    пример:
        secret_data = read_secret_data('ИМЯ', token_vault)


postgres_query_read:
    Функция для выполнения sql запросов не требующих вывода DF в базах greenplum и postgres

    :param sql: drop table table_name;
    :param connect: {'dbname': 'dwh', 'user': LOGIN,
                  'password': PASSWORD, 'port': 5432,
                  'host': 'greenplum.ru'}
    :param name: уведомление об окончании запроса
    :return: print(f'Запрос выполнен {name}'
 
    Пример:
    postgres_query_read('''
            drop table if exists ext_das.das_crm_task;
            CREATE TABLE ext_das.das_crm_task (
            "due_date" DATE,
              "status" TEXT);''', conn, name='das_crm_task')


insert_greenplum:
  Функция для выполнения insert запросов для баз greenplum и postgres
   
```
:param df: df - который необходимо записать в БД
    :param table: название таблицы "scheme.table"
    :param conn: {'dbname': 'dwh', 'user': LOGIN,
                  'password': PASSWORD, 'port': 5432,
                  'host': 'greenplum.ru'}
    :return: уведомление о завершении
    Пример:
        insert_greenplum(total_df, 'scheme.table', conn)
```
select_postgres:
 Функция для select из greenplum и postgres

    :param sql: select * from table;
    :param connect: {'dbname': 'dwh', 'user': LOGIN,
                  'password': PASSWORD, 'port': 5432,
                  'host': 'greenplum.ru'}
    :return: DataFrame
 
    Пример:
        df = select_postgres("select * from table;", connect)


get_google_sheets:

```
Функция получает данные из гугл таблицы
    :param file_id: file_id
    :param sheet_id: sheet_id
    :param accesses: accesses - доступы
    :return: DataFrame
 ```
    Пример:
        df = get_google_sheets(book_id='1Ws3QZFo2av', worksheet_id=0, accesses=accesses)


update_worksheet:
 Функция для записи DataFrame в гугл таблицу
 
```
  :param df: DataFrame
    :param book_id: book_id, если записываем на ранее созданный лист, при создании нового не указываем,
        None - по умолчанию
    :param accesses:  accesses - Доступы
    :param worksheet_id:  worksheet_id
    :param create_new_sheet: Если нужно создать новый лист и записать в него, то ставим True, по умолчанию False
    :param new_sheet: Если нужно создать новый лист указываем его имя
    :return:
 ```
    Пример:
        update_worksheet(total,'1Ws3QZFo2av-', accesses, worksheet_id=0)

clear_worksheet:
  Функция для удаления всех данных с листа
 

```
    :param book_id:  book_id
    :param worksheet_id:  worksheet_id
    :param accesses: accesses
    :return:
 
   Пример:
        clear_worksheet(book_id='1Ws3QZFo2av', worksheet_id=0, accesses=accesses)```
```
select_mssql:
 Функция для select из mssql
    
```
:param sql: select * from table;
    :param conn: {'server': 'master', 'user': f"domen\\{LOGIN}",
               'password': PASSWORD, 'host': 'ms-sql.ru'}
    :return: DataFrame
 
    Пример:
        df = select_mssql("select * from table;", conn)
```

Новый модуль DB для работы с БД 'postgresql' , 'mssql', 'clickhouse':
```
mssql = DB(**creds_mssql, what_db='mssql')
postg = DB(**creds_posgresql)
click = DB(**creds_posgresql, what_db='clickhouse')

select:
postg.select(sql) -> pd.Dataframe

postg.insert(pd.Dataframe, "название таблицы")

```
Описание в работе