from flask_restplus import Namespace, fields
from marshmallow import Schema


class UserDto:
    api = Namespace('user', description='user related operations')
    user = api.model('user', {
        'username': fields.String(required=True, description='username'),
        'password': fields.String(required=True, description='password'),
        'wallet_address': fields.String(required=True, description='wallet address'),
        'fname': fields.String(description='First name'),
        'lname': fields.String(description='Last name'),
        'email': fields.String(required=True, description='email address'),
    })

    stat = api.model('userStat', {
        'time': fields.DateTime(required=True, description="time that the stats were queried"),
        'user_id': fields.String(required=True, description="which user the stats are for"),
        'balance': fields.Float(required=False, description="total balance in wei"),
        'est_revenue': fields.Float(required=False, description="flexpools estimated daily revenue in wei"),
        'valid_shares': fields.Integer(required=False, description="total valid shares over past 24hrs"),
        'stale_shares': fields.Integer(required=False, description="total stale shares over past 24hrs"),
        'invalid_shares': fields.Integer(required=False, description="total invalid shares over past 24hrs"),
        'round_share_percent': fields.Float(required=False, description="share percentage of the current round"),
        'effective_hashrate': fields.Float(required=False,
                                           description="current effective hashrate reported by flexpool"),
    })

    class StatsQuerySchema(Schema):
        start = fields.DateTime(required=False)
        end = fields.DateTime(required=False)


class MinerDto:
    api = Namespace('miner', description='miner related operations')

    miner = api.model('miner', {
        'miner_id': fields.String(required=True, description="the miners UUID"),
        'name': fields.Float(required=False, description="name of the miner set by the user"),
        'user_id': fields.Float(required=False, description="user id of the user that the miner belongs to"),
    })

    stats = api.model('minerStat', {

    })

    class StatsQuerySchema(Schema):
        start = fields.DateTime(required=False)
        end = fields.DateTime(required=False)
