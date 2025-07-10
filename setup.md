find openwisp_test_management/ -name "*.py" | sort | while read file; do echo "# File: $file"; cat "$file"; echo; done > all_code.txt


tree -I 'venv'

tree . -I 'venv|openwisp_monitoring|openwisp_controller.egg-info|openwisp_firmware_upgrader'



docker volume prune -f
docker volume ls

docker volume rm openwisp-controller_postgres_data
docker volume rm openwisp-controller_redis_data
docker volume rm openwisp-firmware-upgrader_postgres-data
docker volume rm openwisp-firmware-upgrader_redis-data

docker container stop $(docker ps -aq)
docker container rm -f $(docker ps -aq)
docker volume prune -f



 docker rmi -f $(docker images -aq)
docker volume rm -f openwisp-controller_influxdb-data openwisp-controller_postgres_data openwisp-controller_redis_data 
docker volume rm openwisp-controller_media_files
docker volume rm openwisp-controller_static_files





docker volume rm $(docker volume ls -q) 

# monitoring
    sudo apt update
    sudo apt install -y sqlite3 libsqlite3-dev openssl libssl-dev
    sudo apt install -y gdal-bin libproj-dev libgeos-dev libspatialite-dev libsqlite3-mod-spatialite
    sudo apt install -y fping
    sudo apt install -y chromium

# Deactivate and remove venv
deactivate || true
rm -rf venv/

# Recreate, activate, and upgrade pip
python3.11 -m venv venv
source venv/bin/activate
pip install -U pip setuptools wheel


# 4. Now install controller dependencies 
    pip install -e .   
    pip install -r requirements.txt
    pip install -r requirements-test.txt    

<!-- pip install 'Twisted[tls,http2]' -->
  pip uninstall -y django-sendsms sendsms
  pip install sendsms==0.2.0 twilio
  pip install sendsms==0.2.0 django-sendsms==0.5

docker exec -u root -it openwisp-controller-controller-1 /bin/sh




# 5. Install the controller itself in editable mode (optional but recommended):
pip install -e ../django-loci
pip install -e ../django-x509
pip install -e ../netjsonconfig
pip install -e ../openwisp-notifications
pip install -e ../openwisp-ipam
pip install -e ../openwisp-users
pip install -e ../openwisp-utils
pip install -e ../netdiff



docker compose up -d redis postgres 

# run docker services   
docker compose up -d redis postgres influxdb





# goto test directory
cd tests
./manage.py migrate
./manage.py createsuperuser

cd tests
python manage.py makemigrations 
DJANGO_SETTINGS_MODULE=openwisp2.postgresql_settings ./manage.py migrate
DJANGO_SETTINGS_MODULE=openwisp2.postgresql_settings ./manage.py createsuperuser


# run celery
cd tests
celery -A openwisp2 worker -l info &


source venv/bin/activate && cd tests && celery -A openwisp2 worker -l info 
celery -A openwisp2 worker -l info --concurrency=1

source venv/bin/activate && cd tests && celery -A openwisp2 beat -l info


source venv/bin/activate && cd tests &&  ./manage.py runserver 0.0.0.0:8000 



# openwrt






# upgrade latest packages
pip uninstall -y openwisp-users
pip install --upgrade https://github.com/sachinspanidea8484/openwisp-users-spanidea/tarball/main






pip install --upgrade -r requirements.txt





















# requirement freeze commands
# Generate requirements.txt with all installed packages
pip freeze > requirements.txt
pip freeze > requirements-test.txt


# Or if using pip-tools
pip list --format=freeze > requirements.txt


















 1. Make Migrations for Specific App
python manage.py makemigrations test_management

2. Apply Migrations for Specific App
python manage.py migrate test_management 




# unmigratedock
docker exec -it openwisp-controller-postgres-1 psql -U openwisp2 -d openwisp2

DELETE FROM django_migrations WHERE app = 'test_management';

find openwisp_test_management/migrations -type f ! -name '__init__.py' -delete


DELETE FROM auth_group_permissions 
WHERE permission_id IN (
    SELECT id FROM auth_permission WHERE content_type_id IN (84, 85)
);

DELETE FROM auth_permission WHERE content_type_id IN (84, 85);







python manage.py collectstatic 


















































docker-compose -f docker-compose-prod.yml up -d
docker-compose -f docker-compose-prod.yml down 
docker-compose -f docker-compose-prod.yml build 




# Watch container status in real-time
watch -n 2 'docker-compose -f docker-compose-prod.yml ps'

# Monitor logs in separate terminal windows
# Terminal 1:
docker-compose -f docker-compose-prod.yml logs -f controller

# Terminal 2:
docker-compose -f docker-compose-prod.yml logs -f celery celery-beat

# Terminal 3:
docker-compose -f docker-compose-prod.yml logs -f postgres redis influxdb










docker rmi openwisp/controller-production:latest







# Stop all containers
docker-compose -f docker-compose-prod.yml down

# Remove the old image to force a clean build
docker rmi openwisp/controller-production:latest

# Build fresh
docker-compose -f docker-compose-prod.yml build --no-cache

# Start services
docker-compose -f docker-compose-prod.yml up -d

# Check logs
docker-compose -f docker-compose-prod.yml logs -f controller


docker-compose -f docker-compose-prod.yml up -d --build
docker-compose -f docker-compose-prod.yml up --build

docker-compose -f docker-compose-prod.yml restart