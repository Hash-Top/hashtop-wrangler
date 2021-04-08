# bugfix for importing flask_restplus
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property

from flask_restplus import Api
from flask import Blueprint

from .main.controller.user_controller import api as user_ns
from .main.controller.miner_controller import api as miner_ns
from .main.controller.auth_controller import api as auth_ns


blueprint = Blueprint('api', __name__)

api = Api(blueprint,
          title='HashTop Wrangler',
          version='1.0',
          description='API for fully managed cryptomining'
          )

api.add_namespace(user_ns, path='/user')
api.add_namespace(miner_ns, path='/miner')
api.add_namespace(auth_ns, path='/auth')