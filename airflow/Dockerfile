FROM python:3.8-slim-buster

# Set environment variables
ENV AIRFLOW_HOME=/usr/local/airflow
ENV PYTHONPATH=/usr/local/airflow:$PYTHONPATH

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libssl-dev \
        libffi-dev \
        libpq-dev \
        git && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

# Copy DAGs and plugins
COPY . $AIRFLOW_HOME/.

# Set the entrypoint
WORKDIR $AIRFLOW_HOME

ENTRYPOINT ["airflow"]
CMD ["webserver"]