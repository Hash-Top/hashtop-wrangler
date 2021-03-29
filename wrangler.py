from flask import Flask, request, jsonify
from dotenv import load_dotenv
import hashtop_miner
import models
from models import *
import uuid
import urllib
import os
from sqlalchemy.orm import (
    Session,
    exc,

)
from sqlalchemy import (
    select
)
import logging

def setup_logger():
    log_dir = os.path.dirname(os.path.abspath(__file__)) + "/logs/"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging.basicConfig(filename=log_dir + "hashtop-wrangler-svc.log", filemode='w', level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(name)s %(message)s')
    logger = logging.getLogger(__name__)

    return logger
logger = setup_logger()

app = Flask(__name__)
load_dotenv()
nathan = User(lname='nathan',
              fname='plow',
              wallet_addr='0xc9cFdce5F5DF8e07443Ac2117D462050C8B9d225')
session = Session(engine)
# session.add(nathan)
session.commit()


@app.route('/test', methods=['GET'])
def test():
    query = select(User)

    with Session(engine) as session:
        results = []
        for row in session.execute(query):
            print(row)
            results.append(row[0].as_dict())
        return jsonify(results)


@app.route('/user', methods=['POST', 'PUT'])
def user():
    if request.method == 'POST':
        new_user = User(fname=request.args['fname'],
                        lname=request.args['lname'],
                        wallet_addr=request.args['wallet_addr'],
                        )
        session.add(new_user)
    try:
        session.commit()
        return 200
    except exc.SQLAlchemyError as e:
        logger.error(e)


@app.route('/user/stats/<wallet_addr>', methods=['GET', 'POST'])
def user_stats(wallet_addr):
    if request.method == 'GET':
        query = select(UserStat).\
            where(UserStat.wallet_addr == wallet_addr)
        with Session(engine) as session:
            results = []
            for row in session.execute(query):
                print(row)
                results.append(row[0].as_dict())
            return jsonify(results)


@app.route('/miner/stats/<miner_uuid>', methods=['GET'])
def miner_stats(miner_uuid):
    params = {
        ""
    }
    if request.method == 'POST':
        # if the miner is already there, return its stats
        if Miner.objects(id=miner_uuid):
            Miner.objects()
            request.json

    else:
        jsonify({

        })


# endpoint for the daemon to update the health of the miner
# and for the daemon to set any new configurations
@app.route('/minerd/<miner_uuid>', methods=['GET', 'POST'])
def hashtop_daemon_wrangler(miner_uuid):
    return 200


# update miners health from the last 10 secs
def update_miner_health(miner_uuid, temps):
    miner = Miner.objects(id=miner_uuid).update()


if __name__ == '__main__':
    app.run(threaded=True, port=5000)
