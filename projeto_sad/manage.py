#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projeto_sad.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

# 1. Abrir o terminal NA PASTA RAIZ (onde está manage.py)
cd /caminho/para/seu/projeto

# 2. Criar o app Django chamado "weka"
python manage.py startapp weka

# 3. Verificar se a pasta foi criada:
ls -la weka/
#mostrar: __init__.py, admin.py, apps.py, models.py, tests.py, views.py
