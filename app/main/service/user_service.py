from datetime import datetime
from app.main import db
from app.main.model.user import User, UserStat
from . import save_changes


def create_new_user(data):
    user = db.session.query(User).filter_by(email=data.get('email'))
    if not user:
        new_user = User(
            fname=data.get('fname'),
            lname=data.get('lname'),
            wallet_address=data.get('wallet_address'),
            username=data.get('username'),
            email=data.get('email'),
            password=data.get('password'),
            registered_on=datetime.utcnow(),
        )
        save_changes(new_user)
        response_object = {
            'status': 'success',
            'message': 'Successfully registered.'
        }
        return response_object, 201
    else:
        response_object = {
            'status': 'fail',
            'message': 'User already exists. Please Log in.',
        }
        return response_object, 409


def get_all_users():
    return db.session.query(User).all()


def get_user(username):
    return db.session.query(User).filter_by(username=username).first()


#def get_user(user_id):
#    return db.session.query(User).filter_by(id=user_id).first()


def get_stats_by_user(user, start, end):
    query = db.session.query(UserStat).filter_by(user=user)
    if start:
        query = query.filter(UserStat.time >= start)
    if end:
        query = query.filter(UserStat.time <= end)

    return query.all()

