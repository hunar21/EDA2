from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import glob

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 2,  # Increased retry count for robustness
    'retry_delay': timedelta(minutes=5),
}

# Consider externalizing these paths as Airflow Variables in a production setting.
CSV_DIR = '/data/local/extracted/stock-market-dataset/stocks'
PIPELINE_SCRIPTS_DIR = '/data/local/pipeline_scripts'

def count_csv_files():
    files = glob.glob(os.path.join(CSV_DIR, '*.csv'))
    print(f"Found {len(files)} CSV files to process.")

def count_accuracy_files():
    accuracy_files = glob.glob(os.path.join(CSV_DIR, '*_accuracy.txt'))
    for file in accuracy_files:
        with open(file) as f:
            accuracy = f.read().strip()
            print(f"{os.path.basename(file)}: {accuracy}")
    print(f"Total accuracy files generated: {len(accuracy_files)}")

with DAG(
    'stock_prediction_dag',
    default_args=default_args,
    description='Run stock LSTM prediction using PySpark',
    schedule_interval=None,  # Change to a cron string if you need scheduled runs
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
            'PYSPARK_PYTHON': '/usr/bin/python',  # 👈 explicitly use the working Python
            'PATH': '/usr/lib/jvm/java-11-openjdk/bin:/opt/spark/bin:/usr/bin:/bin'
        }
    )


    verify_outputs = BashOperator(
        task_id='check_accuracy_files_exist',
        bash_command=f'ls {CSV_DIR}/*_accuracy.txt',
    )

    parse_accuracies = PythonOperator(
        task_id='parse_accuracy_outputs',
        python_callable=count_accuracy_files,
    )

    # Define task dependencies
    check_data >> count_input_files >> verify_scripts >> run_spark >> verify_outputs >> parse_accuracies
