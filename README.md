### Development
docker-compose -f docker-compose.yml up -d --build \
docker-compose -f docker-compose.yml exec web python manage.py migrate --noinput  \
docker-compose -f docker-compose.yml exec web python manage.py collectstatic --no-input --clear
docker-compose down -v

### Production
docker-compose -f docker-compose.prod.yml up -d --build \
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput \
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input --clear
docker-compose down -v