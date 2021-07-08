import logging
import os
from app.main import db
from flask import Response
from sqlalchemy import exc
from app.main.base_logger import logger

logger = logger.getLogger(__name__)


def update(obj, data):
    obj.update(data)
    save_changes(obj)
    response_object = {
        'status': 'success',
        'message': 'Successfully updated.'
    }
    return response_object, 200


def delete(obj):
    db.session.delete(obj)
    save_changes(obj)
    response_object = {
        'status': 'success',
        'message': 'Successfully deleted.'
    }
    return response_object, 200

def save_changes(data):
    try:
        db.session.add(data)
        db.session.commit()
    except exc.SQLAlchemyError as e:
        logger.error(e)
        return Response(response="Operation failed, check logs", status=500, mimetype='text/plain')
