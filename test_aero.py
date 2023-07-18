from airflow.operators.latest_only_operator import LatestOnlyOperator
from airflow.operators.python import PythonOperator
from airflow import DAG

from datetime import timedelta
import pendulum
import requests
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine

# Гиперпараметры
url = "https://random-data-api.com/api/cannabis/random_cannabis?size=10"
postgres_host = "some_host"
postgres_port = 5432
postgres_database = "database"
postgres_schema = "schema"
postgres_table = "table"
postgres_login = "username"
postgres_password = "password"

# Описание функций
def log(text):
    print(f"[{datetime.now().date()}] {text}")

def upload_data_to_postgres():
    log("Начинаем грузить данные из API")
    res_json = requests.get(url).json()
    log("Закончили грузить данные из API")
    df = pd.DataFrame(res_json)

    log("Загружаем данные в базу")
    # По факту этот код годится для postgres и greenplum
    engine = create_engine(f"postgresql://{postgres_login}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_database}")
    # Проверяем, что таблица существует (на моем опыте она много раз не существовала)
    try:
        df.to_sql(name=postgres_table, schema=postgres_schema, con=engine, if_exists="append")
    except Exception as e:
        # Ошибка в основном может возникнуть, если api поменяли и у нас теперь другие типы данных и колонки
        log("Ошибка загрузки: {str(e)}") # Тут явная типизация осознана
        # Чтоб не потерять данные, создадим новую таблицу, чтоб потом умные инженеры думали о причине ошибки
        df.to_sql(name=f"{postgres_table}_after_error", schema=postgres_schema, con=engine, if_exists="append")
        # И в конце бросим ошибку, чтоб привлечь внимание со стороны инженеров
        raise Exception(str(e))

    log("Загрузка успешна")


args = {
    'owner': 'Dmitruk_Max',
    'depends_on_past': True,
    'retries': 2,
    'retry_delay': timedelta(minutes=60)
}

sd = (pendulum.now('Europe/Moscow').subtract(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)

dag = DAG(
    dag_id='test',
    default_args=args,
    schedule_interval='0 12,24 * * *',
    start_date=sd,
    max_active_runs=1,
    catchup=False,
)

# Операторы
lo = LatestOnlyOperator(task_id="lo", dag=dag)
upload_data_to_postgres_op = PythonOperator(task_id='upload_data_to_postgres', dag=dag, python_callable=upload_data_to_postgres)

lo >> upload_data_to_postgres_op
