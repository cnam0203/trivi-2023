### Development
docker-compose -f docker-compose.yml up -d --build \
docker-compose -f docker-compose.yml exec web python manage.py makemigrations --no-input  
docker-compose -f docker-compose.yml exec web python manage.py migrate --noinput  \
docker-compose -f docker-compose.yml exec web python manage.py collectstatic --no-input --clear

docker-compose -f docker-compose.yml exec airflow airflow db upgrade
docker-compose -f docker-compose.yml exec airflow airflow users create --role Admin --username admin --password admin --firstname admin  --lastname admin --email admin@vng.com.vn
docker-compose -f docker-compose.yml exec airflow airflow scheduler

docker-compose down -v

### Production
docker-compose -f docker-compose.prod.yml up -d --build \
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput \
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input --clear
docker-compose down -v 