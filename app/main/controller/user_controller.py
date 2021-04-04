from flask import request
from flask_restplus import Resource
from ..util.dto import UserDto
from ..service.user_service import (
    save_new_user,
    update_user,
    delete_user,
    get_all_users,
    get_a_user,
    get_a_users_stats,
)

api = UserDto.api
_user = UserDto.user
_stat = UserDto.stat
stats_schema = UserDto.StatsQuerySchema()


@api.route('/')
class UserList(Resource):
    @api.doc('list_of_registered_users')
    @api.marshal_list_with(_user, envelope='data')
    def get(self):
        """List all registered users"""
        return get_all_users()

    @api.response(201, 'User successfully created.')
    @api.doc('create a new user')
    @api.expect(_user, validate=True)
    def post(self):
        """Creates a new User """
        data = request.json
        return save_new_user(data=data)


@api.route('/<wallet_addr>/')
@api.param('wallet_addr', "User's wallet address")
@api.response(404, 'No user with that address.')
class User(Resource):
    @api.doc('get a user')
    @api.marshal_with(_user)
    def get(self, wallet_addr):
        """Get a User by their wallet address"""
        user = get_a_user(wallet_addr)
        if not user:
            api.abort(404)
        else:
            return user

    @api.response(200, 'User successfully updated.')
    @api.doc('update a users information')
    @api.expect(_user, validate=True)
    def put(self, wallet_addr):
        """Updates a User """
        user = get_a_user(wallet_addr)
        if not user:
            api.abort(404)
        else:
            data = request.json
            return update_user(user, data)

    @api.response(200, 'User successfully deleted.')
    @api.doc('delete a user')
    def delete(self, wallet_addr):
        """ Delete a User """
        user = get_a_user(wallet_addr)
        if not user:
            api.abort(404)
        else:
            return delete_user(user)


# found on SO, "trailing slash -> there might be more after this, no slash -> this is the final endpoint"
@api.route('/<wallet_addr>/stats')
@api.doc(body="Not specifying start or end will return the past 7 days of stats")
@api.param('end', "Optional time after which to retrieve stats")
@api.param('start', "Optional time before which to retrieve stats")
@api.param('wallet_addr', "User's wallet address")
@api.response(404, 'No user with that address.')
class UserStats(Resource):
    @api.marshal_list_with(_stat)
    def get(self, wallet_addr):
        """Get a User's stats"""
        user = get_a_user(wallet_addr)
        if not user:
            api.abort(404)
        else:
            """validate the query params"""
            errors = stats_schema.validate(request.args)
            if errors:
                api.abort(400, error="Start/end datetime param improperly formatted")
            return get_a_users_stats(user, request.args.get('start'), request.args.get('end'))