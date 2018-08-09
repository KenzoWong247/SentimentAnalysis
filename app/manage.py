import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import run, db


run.config.from_object(os.environ['APP_SETTINGS'])

migrate = Migrate(run, db)
manager = Manager(run)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
