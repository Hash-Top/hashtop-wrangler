import logging
import os

log_dir = os.path.dirname(os.path.abspath(__file__)) + "/logs/"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(filename=log_dir + "hashtop-svc.log", filemode='w', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)