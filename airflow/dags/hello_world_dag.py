#datetime
from datetime import timedelta, datetime
import os

# The DAG object
from airflow import DAG

# Operators
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator


# python callable function
def print_hello():
	print(os.environ.get("AIRFLOW_DB_USER"))
	print(os.environ.get("AIRFLOW_DB_PASSWORD"))
	print(os.environ.get("AIRFLOW_DB_HOST"))
	print(os.environ.get("AIRFLOW_DB_PORT"))
	return 'Hello World!'

# initializing the default arguments
default_args = {
		'owner': 'Ranga',
		'start_date': datetime(2022, 3, 4),
		'retries': 3,
		'retry_delay': timedelta(minutes=5)
}

# Instantiate a DAG object
hello_world_dag = DAG('hello_world_dag',
		default_args=default_args,
		description='Hello World DAG',
		schedule_interval='* * * * *', 
		catchup=False,
		tags=['example, helloworld']
)

# Creating first task
start_task = DummyOperator(task_id='start_task', dag=hello_world_dag)

# Creating second task
hello_world_task = PythonOperator(task_id='hello_world_task', python_callable=print_hello, dag=hello_world_dag)

# Creating third task
end_task = DummyOperator(task_id='end_task', dag=hello_world_dag)

start_task >> hello_world_task >> end_task