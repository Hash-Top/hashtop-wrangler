import os
import unittest

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from app import blueprint
from app.main import create_app, db
from app.main.model import user, miner, gpu

app = create_app(os.getenv('STAGE_ENV') or 'dev')
app.register_blueprint(blueprint)
app.app_context().push()

manager = Manager(app)

migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)


@manager.command
def run():
    app.run(threaded=True, port=5000)


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
    import urllib
    from sqlalchemy import create_engine
    load_dotenv()
    AZURE_CONNECT_STRING = os.getenv("AZURE_CONNECT_STRING")
    params = urllib.parse.quote(AZURE_CONNECT_STRING)
    conn_str = 'mssql+pyodbc:///?odbc_connect={}'.format(params)
    engine = create_engine(conn_str, echo=True)
    Base.metadata.drop_all(engine)


if __name__ == '__main__':
    manager.run()
