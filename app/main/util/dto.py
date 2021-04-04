from flask_restplus import Namespace, fields
from marshmallow import Schema


class UserDto:
    api = Namespace('user', description='user related operations')
    user = api.model('user', {
        'wallet_addr': fields.String(required=True, description='wallet address'),
        'username': fields.String(required=True, description='username'),
        'password': fields.String(required=True, description='password'),
        'email': fields.String(required=True, description='email address'),
    })

    stat = api.model('userStat', {
        'time': fields.DateTime(required=True, description="time that the stats were queried"),
        'wallet_addr': fields.String(required=True, description="which wallet address the stats are for"),
        'balance': fields.Float(required=False, description="total balance in wei"),
        'est_revenue': fields.Float(required=False, description="flexpools estimated daily revenue in wei"),
        'valid_shares': fields.Float(required=False, description="total valid shares over past 24hrs"),
        'stale_shares': fields.Float(required=False, description="total stale shares over past 24hrs"),
        'invalid_shares': fields.Float(required=False, description="total invalid shares over past 24hrs"),
        'round_share_percent': fields.Float(required=False, description="share percentage of the current round"),
        'effective_hashrate': fields.Float(required=False, description="current effective hashrate reported by flexpool"),
    })

    class StatsQuerySchema(Schema):
        start = fields.DateTime(required=False)
        end = fields.DateTime(required=False)
