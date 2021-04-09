from flask import request
from flask_restplus import Resource

from app.main.service.auth_helper import Auth
from ..util.dto import AuthDto
from ..util.decorators import token_required

api = AuthDto.namespace
user_auth = AuthDto.user_auth


@api.route('/login')
class UserLogin(Resource):
    """
        User Login Resource
    """
    @api.doc('user login')
    @api.expect(user_auth, validate=True)
    def post(self):
        # get the post data
        post_data = request.json
        return Auth.login_user(data=post_data)


@api.route('/logout')
class LogoutAPI(Resource):
    """
    Logout Resource
    """
    @api.doc('logout a user')
    def post(self):
        # get auth token
        auth_header = request.headers.get('Authorization')
        if auth_header:
            # fair warning, this line is taken from realpython.com and it is very ugly
            # it is meant to remove the "Bearer " part of the auth header
            auth_token = auth_header.split(' ')[1]
        else:
            auth_token = ''
        return Auth.logout_user(token=auth_token)