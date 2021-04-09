import os
import unittest

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from app import blueprint
from app.main import create_app, db, config
from app.main.model import user, miner, gpu
app = create_app()
app.register_blueprint(blueprint)
app.app_context().push()

manager = Manager(app)

migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)


@manager.command
def run():
    app.run(threaded=True, port=5000)
    return app


@manager.command
def test():
    """Runs the unit tests."""
    tests = unittest.TestLoader().discover('app/test', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


@manager.command
def drop_all():
    from app.main.model import Base
    from dotenv import load_dotenv
    from sqlalchemy import create_engine
    load_dotenv()
    engine = create_engine(config.SQLALCHEMY_DATABASE_URI, echo=True)
    Base.metadata.drop_all(engine)


@manager.command
def create_all():
    from app.main.model import Base
    from dotenv import load_dotenv
    from sqlalchemy import create_engine
    load_dotenv()
    engine = create_engine(config.SQLALCHEMY_DATABASE_URI, echo=True)
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    manager.run()
