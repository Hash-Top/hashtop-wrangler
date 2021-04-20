from flask import request
from flask_restplus import Resource

from ..service.user_service import get_stats_by_user
from ..util.dto import MinerDto
from ..service.miner_service import (
    create_new_miner,
    get_all_miners,
    get_user,
    get_miner,
    get_stats_by_miner,
)
from ..service import update, delete
from ..util.decorators import token_required, admin_token_required

api = MinerDto.namespace
_miner = MinerDto.miner
_minerStats = MinerDto.stats
stats_schema = MinerDto.StatsQuerySchema()


@api.route('/<username>/')
class MinerList(Resource):
    @api.doc('list_of_miners_owned_by_this_user')
    @api.marshal_list_with(_miner, envelope='data')
    @token_required
    def get(self, username):
        """List all miners owned by this user"""
        user = get_user(username=username)
        return get_all_miners(user)

    @api.response(201, 'Miner successfully created.')
    @api.doc('create a new miner')
    @api.expect(_miner, validate=True)
    @token_required
    def post(self):
        """Creates a new Miner """
        data = request.json
        create_new_miner(data=data)


@api.route('/<username>/<miner_id>')
@api.param('username', "User's username")
@api.param('miner_id', "The miner's id")
@api.response(404, 'No User/Miner with that id.')
class MinerStats(Resource):
    @api.doc('get a miners stats')
    @api.doc(body="Not specifying start or end will return the past 7 days of stats")
    @api.param('end', "Optional time after which to retrieve stats")
    @api.param('start', "Optional time before which to retrieve stats")
    @api.marshal_with(_minerStats)
    @token_required
    def get(self, username, miner_id):
        """ Get a miner's stats """
        user = get_user(username)
        miner = get_miner(miner_id)
        if not user:
            api.abort(404)
        else:
            """validate the query params"""
            errors = stats_schema.validate(request.args)
            if errors:
                api.abort(400, error="Start/end datetime param improperly formatted")

        return get_stats_by_miner(miner, request.args.get('start'), request.args.get('end'))

    @api.response(200, 'Miner successfully updated.')
    @api.doc('update a miners information')
    @api.expect(_miner, validate=True)
    @token_required
    def put(self, username, miner_id):
        """Updates a User's miner """
        user = get_user(username, miner_id)
        miner = get_miner(miner_id)
        if not user or not miner:
            api.abort(404)
        else:
            data = request.json
            return update(miner, data)

    @api.response(200, 'Miner successfully deleted.')
    @api.doc("delete a user's miner")
    @token_required
    def delete(self, username, miner_id):
        """ Delete a user's miner """
        miner = get_miner(miner_id)
        if not miner:
            api.abort(404)
        else:
            return delete(miner)