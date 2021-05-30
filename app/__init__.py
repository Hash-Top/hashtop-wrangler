# bugfix for importing flask_restplus

import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property

from flask_restplus import Api
from flask import Blueprint

from .main.apis.user import api as user_ns
from .main.apis.miner import api as miner_ns
from .main.apis.auth import api as auth_ns
from .main.apis import miner_socket



blueprint = Blueprint('api', __name__)#, url_prefix='/api')

api = Api(blueprint,
          title='HashTop Wrangler',
          version='1.0',
          description='API for fully managed cryptomining',
          #doc='/doc/'
          )

api.add_namespace(user_ns, path='/user')
api.add_namespace(miner_ns, path='/miner')
api.add_namespace(auth_ns, path='/auth')
