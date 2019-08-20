# MLM System

## Description

TODO

## Installation

Be sure that Python 3.5+ is installed globally or in a Python virtualenv.

1. Clone repository in a local directory
2. Enter the project root directory and run following commands
    * `pip install -r requirements` to install dependencies
    * `python manage.py migrate` to sync with database
    * `python manage.py runserver` to run the development server.

3. Put initial data following these steps:
    * run `python manage.py createsuperuser` for having a super user
    * import and call function for creating a client in the shell `from mlm.apps.main.utils.base import create_adminclient`
4. Follow instructions in **Contribute** section to contribute to the code

## Contribute

TODO

## Deploy

TODO
