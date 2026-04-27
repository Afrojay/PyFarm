## PyFarm

PyFarm is a Django-based agricultural planning application. It allows farm users to manage fields, farming projects, and project tasks.

The main required use case is Productivity: Projects and Tasks.

## Main Features

- View farm projects
- View tasks linked to projects
- Create fields
- Create farm projects
- Create tasks
- Mark tasks as done
- User roles: Farm Manager, Field Worker, Agronomist
- Basic login protection
- Sample fixture data
- Basic automated tests

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata pyfarm_data
python manage.py runserver

Open http://127.0.0.1:8000/ to view the app.
