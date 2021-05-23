import unittest
from datetime import datetime

from app.test.base import BaseTestCase
from app.main.model import User, Miner, Gpu
from app.main.model.gpu import Share, ShareType
from app.main.service.socket_service import update_shares
from app.main import db


class TestShareSocket_EverythingExists(BaseTestCase):
    test_user = User()
    test_miner = Miner()

    def setUp(self):
        db.create_all()

        new_user = User(
            wallet_address='0xc9cFdce5F5DF8e07443Ac2117D462050C8B9d225',
            fname='nathan',
            lname='plow',
            username='plown10',
            email='plown10@gmail.com',
            registered_on=datetime.now()
        )
        self.test_user = new_user

        new_miner = Miner(
            name='money-printer',
            user_id=new_user.id,
            user=new_user,
        )
        self.test_miner = new_miner

        new_miner.gpus.append(
            Gpu(
                gpu_no=0,
                miner_id=new_miner.id,
                miner=new_miner
            )
        )

        db.session.add(new_user)
        db.session.add(new_miner)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_add_one_invalid_share(self):
        """Test adding one new invalid share data for a miners gpu"""
        share_data = {
            'gpu_no': '0',
            'share_type': 'invalid',
            'timestamp': '1621540877'
        }
        response = update_shares(self.test_miner.id, share_data)
        status_code = response[1]
        body = response[0]

        # test the response for errors in updating the db
        self.assertTrue("SUCCESS" in body.get('message').upper(), body.get('message'))
        self.assertEqual(body.get('status'), 'success')
        self.assertEqual(status_code, 201)

        # query the db to make sure the changes are reflected/correct
        exp_share_type = ShareType.invalid
        exp_num_entries = 1

        query = db.session.query(Share).filter_by(miner_id=self.test_miner.id, gpu_no=0)
        # query.all() removes duplicates so use count() to test properly
        act_num_entries = query.count()
        self.assertEqual(act_num_entries, exp_num_entries,
                         f"expected {exp_num_entries} entries, got {act_num_entries}")

        act_share_type = query.first().type
        self.assertEqual(act_share_type, exp_share_type,
                         f"expected {exp_share_type}, got {act_share_type}")

    def test_add_multiple_invalid_share_same_gpu(self):
        """Test adding a lot of invalid shares for the same gpu"""
        share_data = [
            {
                'gpu_no': '0',
                'share_type': 'invalid',
                'timestamp': '1621540817'
            },
            {
                'gpu_no': '0',
                'share_type': 'invalid',
                'timestamp': '1621540870'
            },
            {
                'gpu_no': '0',
                'share_type': 'invalid',
                'timestamp': '1621540877'
            }
        ]

        for datum in share_data:
            response = update_shares(self.test_miner.id, datum)
            status_code = response[1]
            body = response[0]

            # test the response for errors in updating the db
            self.assertTrue("SUCCESS" in body.get('message').upper(), body.get('message'))
            self.assertEqual(body.get('status'), 'success')
            self.assertEqual(status_code, 201)

        # query the db to make sure the changes are reflected/correct
        exp_share_type = ShareType.invalid
        exp_num_entries = len(share_data)

        query = db.session.query(Share).filter_by(miner_id=self.test_miner.id, gpu_no=0)
        # query.all() removes duplicates so use count() to test properly
        act_num_entries = query.count()
        self.assertEqual(act_num_entries, exp_num_entries,
                         f"expected {exp_num_entries} entries, got {act_num_entries}")

        # go through all entries in the db for the specified gpu and map them to their PK -> timestamp
        ts_to_share = {}
        for share in query.all():
            ts = int(share.time.timestamp())
            ts_to_share[ts] = share

        # check through exp items and compare them against the map
        for datum in share_data:
            exp_share_type = ShareType[datum['share_type']]
            act_share_type = ts_to_share[int(datum['timestamp'])].type
            self.assertEqual(exp_share_type, act_share_type,
                             f"expected {exp_share_type}, got {act_share_type}")


    def test_add_multiple_invalid_and_valid_share_same_gpu(self):
        """Test adding a lot of invalid and valid shares for the same gpu"""
        share_data = [
            {
                'gpu_no': '0',
                'share_type': 'invalid',
                'timestamp': '1621540817'
            },
            {
                'gpu_no': '0',
                'share_type': 'invalid',
                'timestamp': '1621540870'
            },
            {
                'gpu_no': '0',
                'share_type': 'invalid',
                'timestamp': '1621540877'
            },
            {
                'gpu_no': '0',
                'share_type': 'valid',
                'timestamp': '1621540872'
            },
            {
                'gpu_no': '0',
                'share_type': 'valid',
                'timestamp': '1621540873'
            }
        ]

        for datum in share_data:
            response = update_shares(self.test_miner.id, datum)
            status_code = response[1]
            body = response[0]

            # test the response for errors in updating the db
            self.assertTrue("SUCCESS" in body.get('message').upper(), body.get('message'))
            self.assertEqual(body.get('status'), 'success')
            self.assertEqual(status_code, 201)

        # query the db to make sure the changes are reflected/correct
        exp_share_type = ShareType.invalid
        exp_num_entries = len(share_data)

        query = db.session.query(Share).filter_by(miner_id=self.test_miner.id, gpu_no=0)
        # query.all() removes duplicates so use count() to test properly
        act_num_entries = query.count()
        self.assertEqual(act_num_entries, exp_num_entries,
                         f"expected {exp_num_entries} entries, got {act_num_entries}")

        # go through all entries in the db for the specified gpu and map them to their PK -> timestamp
        ts_to_share = {}
        for share in query.all():
            ts = int(share.time.timestamp())
            ts_to_share[ts] = share

        # check through exp items and compare them against the map
        for datum in share_data:
            exp_share_type = ShareType[datum['share_type']]
            act_share_type = ts_to_share[int(datum['timestamp'])].type
            self.assertEqual(exp_share_type, act_share_type,
                             f"expected {exp_share_type}, got {act_share_type}")

if __name__ == '__main__':
    unittest.main()
