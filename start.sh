#!/bin/bash

set -o errexit # Exit on error
set -o pipefail # Exit on error in pipe
set -o nounset # Exit on using undeclared variables

python manage.py migrate
python manage.py runserver

