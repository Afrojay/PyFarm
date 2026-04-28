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
- Upload task images (field worker feature)
- User roles: Farm Manager, Field Worker, Agronomist
- Role-based access control
- Login and logout system
- Sample fixture data
- Automated testing

## Demo Users

After loading fixtures, each demo user has the password `password`.

| Username | Role |
| --- | --- |
| `admin` | Django admin |
| `manager` | Farm Manager |
| `worker` | Field Worker |
| `agronomist` | Agronomist |

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata pyfarm_data
python manage.py runserver
```

## Checks

```bash
python manage.py check
python manage.py test
```
