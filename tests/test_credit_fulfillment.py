"""Credits for one paid Stripe checkout session must be granted once, to the buyer only.

The Flask app, database and credit logic are real (a throwaway SQLite file in a temp
directory, never the app's own database). Only the Stripe network calls are replaced
by a local fake of a paid checkout session.
"""
import os
import sys
import types
import unittest
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR', '/tmp/mpl-test')
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import tempfile  # noqa: E402

import config  # noqa: E402

# The app reads its database URI once, at import time. Point it at a temp file first
# so the test can never touch (or drop tables in) a real database.
_TMP = tempfile.TemporaryDirectory()
config.SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_TMP.name, 'test.db')

import stripe  # noqa: E402
import app_enhanced  # noqa: E402
from database_models import db, User, CreditTransaction  # noqa: E402


def paid_session(user_id, credits=30, session_id='cs_test_1'):
    return types.SimpleNamespace(
        id=session_id, payment_status='paid',
        metadata={'user_id': str(user_id), 'credits': str(credits), 'package_name': 'Standard'})


class CreditFulfillment(unittest.TestCase):
    def setUp(self):
        app = app_enhanced.app
        app.config.update(TESTING=True)
        self.app = app
        self.ctx = app.app_context()
        self.ctx.push()
        self.assertIn(_TMP.name, str(db.engine.url))
        db.drop_all()
        db.create_all()
        for name in ('alice', 'mallory'):
            user = User(username=name, email=f'{name}@example.com', credits=0)
            user.set_password('x')
            db.session.add(user)
        db.session.commit()
        self.alice = User.query.filter_by(username='alice').one().id
        self.mallory = User.query.filter_by(username='mallory').one().id
        self.checkout = paid_session(self.alice)
        self.real_retrieve = stripe.checkout.Session.retrieve
        stripe.checkout.Session.retrieve = staticmethod(lambda sid: self.checkout)
        self.addCleanup(self.restore)

    def restore(self):
        stripe.checkout.Session.retrieve = self.real_retrieve
        db.session.remove()
        self.ctx.pop()

    def client_for(self, user_id):
        client = self.app.test_client()
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user_id)
            sess['_fresh'] = True
        return client

    def credits(self, user_id):
        db.session.expire_all()
        return db.session.get(User, user_id).credits

    def test_reloading_the_success_url_does_not_add_credits_again(self):
        client = self.client_for(self.alice)
        for _ in range(3):
            client.get('/mcp/payment-success?session_id=cs_test_1')
        self.assertEqual(self.credits(self.alice), 30)

    def test_success_url_then_webhook_grants_once(self):
        self.client_for(self.alice).get('/mcp/payment-success?session_id=cs_test_1')
        app_enhanced.fulfill_order(self.checkout)
        self.assertEqual(self.credits(self.alice), 30)

    def test_other_users_cannot_claim_someone_elses_paid_session(self):
        self.client_for(self.mallory).get('/mcp/payment-success?session_id=cs_test_1')
        self.assertEqual(self.credits(self.mallory), 0)
        self.assertEqual(CreditTransaction.query.filter_by(user_id=self.mallory).count(), 0)

    def test_buyer_still_gets_credits_on_first_visit(self):
        response = self.client_for(self.alice).get('/mcp/payment-success?session_id=cs_test_1')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.credits(self.alice), 30)


if __name__ == '__main__':
    unittest.main()
