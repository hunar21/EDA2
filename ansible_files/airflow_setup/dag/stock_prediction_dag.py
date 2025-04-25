
from airflow import DAG
from airflow.models import Variable
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os, glob

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

PIPELINE_SCRIPTS_DIR = '/data/local/pipeline_scripts'

# ▼ read csv_dir from UI‑configurable Variable, or use this default
CSV_DIR = Variable.get(
    "csv_dir",
    default_var="/data/local/venv/extracted/stock-market-dataset/stocks"
)

def count_csv_files():
    files = glob.glob(os.path.join(CSV_DIR, '*.csv'))
    print(f"Found {len(files)} CSV files to process.")

def count_accuracy_files():
    accuracy_files = glob.glob(os.path.join(CSV_DIR, '*_accuracy.txt'))
    for file in accuracy_files:
        with open(file) as f:
            print(f"{os.path.basename(file)}: {f.read().strip()}")
    print(f"Total accuracy files generated: {len(accuracy_files)}")

with DAG(
    'stock_prediction_dag',
    default_args=default_args,
    description='Run stock LSTM prediction using PySpark',
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:

    check_data = BashOperator(
        task_id='check_data_ready',
        bash_command=f'test -d {CSV_DIR}',
    )

    count_input_files = PythonOperator(
        task_id='count_input_csv_files',
        python_callable=count_csv_files,
    )

    verify_scripts = BashOperator(
        task_id='verify_pipeline_scripts',
        bash_command=f'ls {PIPELINE_SCRIPTS_DIR}/*.py',
    )

    run_spark = BashOperator(
        task_id='run_spark_prediction',
        bash_command=(
            'spark-submit test.py '
            f'--csv_dir {CSV_DIR} '
        ),
        cwd=PIPELINE_SCRIPTS_DIR,
        env={
            'JAVA_HOME': '/usr/lib/jvm/java-11-openjdk',
            'SPARK_HOME': '/opt/spark',
            'PYSPARK_PYTHON': '/data/local/venv/bin/python',
            'PATH': '/usr/lib/jvm/java-11-openjdk/bin:/opt/spark/bin:/usr/bin:/bin'
        },
    )

    verify_outputs = BashOperator(
        task_id='check_accuracy_files_exist',
        bash_command=f'ls {CSV_DIR}/*_accuracy.txt',
    )

    parse_accuracies = PythonOperator(
        task_id='parse_accuracy_outputs',
        python_callable=count_accuracy_files,
    )

    check_data >> count_input_files >> verify_scripts >> run_spark >> verify_outputs >> parse_accuracies
