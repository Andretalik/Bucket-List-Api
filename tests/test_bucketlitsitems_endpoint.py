from flask import url_for
import json
from werkzeug.security import generate_password_hash

from test_base import BaseTestCase
from app.models import User, BucketList, BucketListItems
from app.database import session

from faker import Factory

fake = Factory.create()


class TestBucketLists(BaseTestCase):
    """Tests against bucketlist creation and retrieval."""

    def setUp(self):
        """Instantiate dummy bucketlist details for testing."""
        # create a dummy user
        self.username = fake.user_name()
        self.password = fake.password()
        password_hash = generate_password_hash(self.password)
        self.user = User(username=self.username, password_hash=password_hash)
        session.add(self.user)
        session.commit()

        # create a dummy bucketlist
        self.list_name = 'Ein Schatz finden'
        self.bucketlist = BucketList(list_name=self.list_name,
                                     creator=self.user.user_id)
        session.add(self.bucketlist)
        session.commit()

        # create a dummy bucketlistitem
        self.item_name = 'Ein bisschen Bier trinken'
        self.bucketlistitem = BucketListItems(item_name=self.item_name,
                                              bucket_id=self.bucketlist
                                              .list_id)
        session.add(self.bucketlistitem)
        session.commit()

        # log in a user to retrieve token
        self.response = self.client.post(url_for('login'),
                                         data=json.dumps({
                                             'username': self.username,
                                             'password': self.password}),
                                         content_type='application/json')
        self.token = json.loads(self.response.data)['token']

    def tearDown(self):
        """Clean up test db after testing."""
        session.remove()
        del self.bucketlist
        del self.bucketlistitem
        del self.user

    def test_bucketlist_item_creation(self):
        """Test bucketlist items creation."""
        bucketlist1 = {
            'list_name': fake.name()
        }
        item = {
            'item_name': fake.name()
        }
        self.client.post(url_for('bucketlists'), data=bucketlist1,
                         headers={'token': self.token})

        bucketlist = session.query(BucketList).first()
        url = '/bucketlists/{}/items/'.format(bucketlist.list_id)

        # Test unsuccesful unauthorized creation
        response = self.client.post(url)
        self.assertEqual(response.status_code, 401)

        # Test successful bucketlist creation
        response = self.client.post(url,
                                    data=item,
                                    headers={'token': self.token})
        self.assertEqual(response.status_code, 201)
        self.assertIn('{} has been added to Bucketlist {}'
                      .format(item['item_name'], bucketlist.list_id),
                      response.data)

    def test_bucketlist_item_edition(self):
        """Test bucketlist edition and deletion methods."""
        bucketlist = session.query(BucketList).first()
        bucketlistitem = session.query(BucketListItems).first()
        url = '/bucketlists/{}/items/{}/'.format(bucketlist.list_id,
                                               bucketlistitem.item_id)

        # Test unauthorized edition
        response = self.client.put(url)
        self.assertEqual(response.status_code, 401)

        # Test unsauthorized deletion
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 401)

        # Test successful item update
        item2 = {
            'item_name': fake.name()
        }
        response = self.client.put(url, data=item2,
                                   headers={'token': self.token})
        self.assertEqual(response.status_code, 200)

        # Test successful item delete
        response = self.client.delete(url, headers={'token': self.token})
        self.assertEqual(response.status_code, 204)
