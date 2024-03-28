#!/usr/bin/env python
import os
import sys

'''
SANTOSH's edit for calling manage.py from module rather than command line
<start>
'''
def mrigserverstart():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mrigweb.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(['manage.py','runserver'])

'''
SANTOSH's edit for calling manage.py from module rather than command line
<end>
'''

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mrigweb.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
