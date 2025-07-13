import os
from pathlib import Path
from django.core.management import call_command

def create_database():
    BASE_DIR = Path('/app')
    DB_PATH = BASE_DIR / 'db' / 'db.sqlite3'
    os.makedirs(BASE_DIR / 'db', exist_ok=True)
    with open(DB_PATH, 'w') as db_file:
        pass  # Create an empty file

def create_superuser():
    print("Creating superuser...")
    call_command('createsuperuser', interactive=True)

if __name__ == "__main__":
    create_database()
    create_superuser()
