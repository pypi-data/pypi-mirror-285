======
django-signals-conf
======

The library helps configure signals for django projects faster and easier

Requirements
-----------
- Python 3
- Django


Quick start
-----------
1. Install using `pip`


    (venv) $ pip install django-signals-conf
2. Add `django_signals_conf` to your INSTALLED_APPS setting like this:


    INSTALLED_APPS = [

        ...
        'django_signals_conf', # new
    ]


3. Run command:

    
    (venv) $ python manage.py createsignals --app=<your_app>
