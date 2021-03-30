from datetime import timedelta
from sqlalchemy import exc
from timeloop import Timeloop
from models import *
from wrangler import select_from_db
import requests
import logging
from sqlalchemy.orm import (
    Session,
)
from sqlalchemy import (
    select,
)

def setup_logger():
    log_dir = os.path.dirname(os.path.abspath(__file__)) + "/logs/"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging.basicConfig(filename=log_dir + "hashtop-updater-svc.log", filemode='w', level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(name)s %(message)s')
    logger = logging.getLogger(__name__)

    return logger
logger = setup_logger()

update_loop = Timeloop()
flexpool_url = "https://flexpool.io/api/v1/miner/{}/{}"


@update_loop.job(interval=timedelta(minutes=10))
def update_all_users_stats():
    query = select(User)
    users = select_from_db(query)
    for u in users:
        upsert_new_stat(u)


# this is called every update interval to query flexpool and update the users stats
def upsert_new_stat(user):
    address = user.wallet_addr
    balance = flexpool_balance(address)
    est_revenue = flexpool_est_revenue(address)
    shares = flexpool_shares(address)
    round_share_percent = flexpool_round_share_percent(address)
    hashrate = flexpool_hashrate(address)

    stat = UserStat(wallet_addr=address,
                    balance=balance,
                    est_revenue=est_revenue,
                    valid_shares=shares['valid'],
                    stale_shares=shares['stale'],
                    invalid_shares=shares['invalid'],
                    round_share_percent=round_share_percent,
                    effective_hashrate=hashrate
                    )
    session = Session(engine)
    session.add(stat)
    try:
        session.commit()
    except exc.SQLAlchemyError as e:
        logger.error(e)


# query flexpool for balance in wei
def flexpool_balance(wallet_addr):
    try:
        response = requests.get(flexpool_url.format(wallet_addr, "balance"))
        balance = response.json()['result']
        return balance
    except requests.exceptions.RequestException as e:
        logger.error(e)


# query flexpool for current estimated daily revenue in wei
def flexpool_est_revenue(wallet_addr):
    try:
        response = requests.get(flexpool_url.format(wallet_addr, "estimatedDailyRevenue"))
        revenue = response.json()['result']
        return revenue
    except requests.exceptions.RequestException as e:
        logger.error(e)


# query flexpool for shares data over 24hrs
def flexpool_shares(wallet_addr):
    try:
        response = requests.get(flexpool_url.format(wallet_addr, "daily"))
        result = response.json()['result']
        shares = {
            'valid': result['valid_shares'],
            'stale': result['stale_shares'],
            'invalid': result['invalid_shares']
        }
        return shares
    except requests.exceptions.RequestException as e:
        logger.error(e)


# query flexpool for current round share percent
def flexpool_round_share_percent(wallet_addr):
    try:
        response = requests.get(flexpool_url.format(wallet_addr,"roundShare"))
        share_percent = response.json()['result']
        return share_percent
    except requests.exceptions.RequestException as e:
        logger.error(e)


# query flexpool for current effective hashrate
def flexpool_hashrate(wallet_addr):
    try:
        response = requests.get(flexpool_url.format(wallet_addr, "current"))
        result = response.json()['result']
        return result['effective_hashrate']
    except requests.exceptions.RequestException as e:
        logger.error(e)

if __name__ == '__main__':
    update_loop.start(block=True)
