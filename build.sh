#!/usr/bin/env bash
set -euo pipefail

# Install dependencies (support both root and nested requirements)
if [ -f requirements.txt ]; then
	echo "Installing dependencies from requirements.txt"
	pip install -r requirements.txt
elif [ -f alx_travel_app/requirements.txt ]; then
	echo "Installing dependencies from alx_travel_app/requirements.txt"
	pip install -r alx_travel_app/requirements.txt
else
	echo "ERROR: requirements.txt not found in repo root or alx_travel_app/" >&2
	exit 1
fi

cd alx_travel_app
python manage.py collectstatic --noinput
python manage.py migrate --noinput
