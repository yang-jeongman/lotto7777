#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# DB가 비어있으면 초기 데이터 적재
python manage.py loaddata initial_draws || echo "Fixture load skipped"
