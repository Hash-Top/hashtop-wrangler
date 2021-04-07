from datetime import datetime
from flask import Response
from app.main import db
from app.main.model.user import User, UserStat
from . import logger
from sqlalchemy import exc


def save_new_user(data):
    user = get_a_user_by_username(data.get('username'))
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


def update_user(user, data):
    user.update(data)
    save_changes(user)
    response_object = {
        'status': 'success',
        'message': 'Successfully updated.'
    }
    return response_object, 200


def delete_user(user):
    db.session.delete(user)
    save_changes(user)
    response_object = {
        'status': 'success',
        'message': 'Successfully deleted.'
    }
    return response_object, 200


def get_all_users():
    return db.session.query(User).all()


def get_a_user_by_username(username):
    return db.session.query(User).filter_by(username=username).first()


def get_a_users_stats(user, start, end):
    query = db.session.query(UserStat).filter_by(user=user)
    if start:
        query = query.filter(UserStat.time >= start)
    if end:
        query = query.filter(UserStat.time <= end)

    return query.all()


def save_changes(data):
    try:
        db.session.add(data)
        db.session.commit()
    except exc.SQLAlchemyError as e:
        logger.error(e)
        return Response(response="Operation failed, check logs", status=500, mimetype='text/plain')
