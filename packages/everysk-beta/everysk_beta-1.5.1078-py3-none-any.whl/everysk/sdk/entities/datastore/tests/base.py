###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################

###############################################################################
#   Imports
###############################################################################
from everysk.config import settings
from everysk.core.compress import compress
from everysk.core.datetime import DateTime
from everysk.core.exceptions import RequiredError, FieldValueError
from everysk.core.http import HttpSDKPOSTConnection
from everysk.core.unittests import TestCase, mock

from everysk.sdk.entities.datastore.base import Datastore


###############################################################################
#   Datastore TestCase Implementation
###############################################################################
class DatastoreTestCase(TestCase):

    def setUp(self):
        self.sample_data = {
            'id': 'dats_12345678',
            'name': 'My Datastore',
            'description': 'This is a sample datastore.',
            'tags': ['tag1', 'tag2'],
            'link_uid': None,
            'workspace': 'my_workspace',
            'date': DateTime(2023, 9, 9, 9, 9, 9, 9),
            'level': '1',
            'data': {'key1': 'value1', 'key2': 'value2'},
            'version': 'v1',
            'created_on': DateTime(2023, 9, 9, 9, 9, 9, 9),
            'updated_on': DateTime(2023, 9, 9, 9, 9, 9, 9)
        }
        self.datastore = Datastore(**self.sample_data)
        self.headers = HttpSDKPOSTConnection().get_headers()
        self.api_url = HttpSDKPOSTConnection().get_url()

    def test_get_id_prefix(self):
        self.assertEqual(Datastore.get_id_prefix(), settings.DATASTORE_ID_PREFIX)

    def test_validate(self):
        expected_data = compress({'class_name': 'Datastore', 'method_name': 'validate', 'self_obj': {'data': {'key1': 'value1', 'key2': 'value2'}, 'id': 'dats_12345678', 'name': 'My Datastore', 'description': 'This is a sample datastore.', 'tags': ['tag1', 'tag2'], 'link_uid': None, 'workspace': 'my_workspace', 'date': '20230909', 'level': '1', 'version': 'v1', 'created_on': {'__datetime__': '2023-09-09T09:09:09.000009+00:00'}, 'updated_on': {'__datetime__': '2023-09-09T09:09:09.000009+00:00'}, '__class_path__': 'everysk.sdk.entities.datastore.base.Datastore'}, 'params': {}}, protocol='gzip', serialize='json')
        datastore: Datastore = self.datastore.copy()

        with mock.patch('requests.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            datastore.validate()

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            verify=settings.HTTP_DEFAULT_SSL_VERIFY,
            timeout=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT,
            data=expected_data
        )

    def test_validate_error(self):
        datastore: Datastore = self.datastore.copy()
        datastore.data = DateTime.now()
        with self.assertRaisesRegex(FieldValueError, "Datastore data is not a valid json"):
            datastore.validate()

        datastore.data = None
        with self.assertRaisesRegex(RequiredError, "The data attribute is required"):
            datastore.validate()

    def test_query_load_with_id(self):
        expected_data = compress({'class_name': 'Datastore', 'method_name': 'retrieve', 'self_obj': None, 'params': {'entity_id': 'dats_1234567891011211234567890'}}, protocol='gzip', serialize='json')

        with mock.patch('requests.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            Datastore(id='dats_1234567891011211234567890', workspace='SampleWorkspace').load()

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            verify=settings.HTTP_DEFAULT_SSL_VERIFY,
            timeout=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT,
            data=expected_data
        )

    def test_query_load(self):
        expected_data = compress({'class_name': 'Query', 'method_name': 'load', 'self_obj': {'_klass': 'Datastore', 'filters': [['workspace', '=', 'SampleWorkspace'], ['link_uid', '=', 'SampleLinkUID']], 'order': [], 'projection': None, 'distinct_on': [], 'limit': None, 'offset': None, 'page_size': None, 'page_token': None, '_clean_order': [], '__class_path__': 'everysk.sdk.entities.query.Query'}, 'params': {'offset': None}}, protocol='gzip', serialize='json')

        with mock.patch('requests.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            Datastore(link_uid='SampleLinkUID', workspace='SampleWorkspace').load()

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            verify=settings.HTTP_DEFAULT_SSL_VERIFY,
            timeout=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT,
            data=expected_data
        )
