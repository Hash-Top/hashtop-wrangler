from flask_restplus import Namespace, fields
from marshmallow import Schema
from ..model.share import ShareType

class UserDto:
    namespace = Namespace('user', description='user related operations')
    user = namespace.model('user', {
        'id': fields.String(description='users UUID'),
        'username': fields.String(required=True, description='username'),
        'password': fields.String(required=True, description='password'),
        'wallet_address': fields.String(description='wallet address'),
        'fname': fields.String(description='First name'),
        'lname': fields.String(description='Last name'),
        'email': fields.String(required=True, description='email address'),
    })

    stat = namespace.model('userStat', {
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
    namespace = Namespace('miner', description='miner related operations')

    miner = namespace.model('miner', {
        'id': fields.String(required=False, description="the miners UUID"),
        'name': fields.String(required=False, description="name of the miner set by the user"),
        'user_id': fields.String(required=False, description="user id of the user that the miner belongs to"),
    })

    share = namespace.model('share', {
        'miner_id': fields.String(required=False, description="the miners UUID"),
        'gpu_no': fields.Integer(required=True, description="the gpu that the share was generated on"),
        'time': fields.DateTime(required=True, description="the time at which the share was generated"),
        'type': fields.String(enum=[enum.name for enum in ShareType], description="invalid, valid or stale"),
    })

    share_aggregate = namespace.model('share_aggregate', {
        'start': fields.DateTime(required=True, description="the time at which the aggregation starts"),
        'duration': fields.Integer(required=True, description="the length of the aggregation period, in minutes"),
        'gpu_no': fields.Integer(required=True, description="the gpu that the share was generated on"),
        'valid': fields.Integer(required=False, description="# of shares generated of this type"),
        'invalid': fields.Integer(required=False, description="# of shares generated of this type"),
    })

    health = namespace.model('health', {
        'miner_id': fields.String(required=False, description="the miners UUID"),
        'gpu_no': fields.Integer(required=True, description="the gpu that the share was generated on"),
        'time': fields.DateTime(required=True, description="the time at which the share was generated"),
        'temperature': fields.Integer(required=False, description="the gpus temperature in C"),
        'power': fields.Integer(required=False, description="the gpus power usage in watts"),
        'hashrate': fields.Float(required=False, description="the gpus hashrate in megahash"),
    })

    class StatsQuerySchema(Schema):
        start = fields.DateTime(required=False)
        end = fields.DateTime(required=False)


class AuthDto:
    namespace = Namespace('auth', description='authentication related operations')
    user_auth = namespace.model('auth_details', {
        'username': fields.String(required=True, description='The user name'),
        'password': fields.String(required=True, description='The user password '),
    })