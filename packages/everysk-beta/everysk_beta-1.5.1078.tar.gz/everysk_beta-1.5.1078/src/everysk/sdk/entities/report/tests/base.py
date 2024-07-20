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
from everysk.core.datetime import DateTime, ZoneInfo
from everysk.core.exceptions import SDKValueError
from everysk.core.http import HttpSDKPOSTConnection
from everysk.core.unittests import TestCase, mock

from everysk.sdk.entities.report.base import Report


###############################################################################
#   Report TestCase Implementation
###############################################################################
class ReportTestCase(TestCase):

    def setUp(self):
        self.sample_data = {
            'created_on': DateTime(2023, 9, 9, 9, 9, 9, 9),
            'updated_on': DateTime(2023, 9, 9, 9, 9, 9, 9),
            'version': 'v1',
            'id': 'repo_12345678',
            'name': 'My Report',
            'description': 'This is a sample report.',
            'tags': ['tag1',
            'tag2'],
            'link_uid': None,
            'workspace': 'my_workspace',
            'date': DateTime(2022, 1, 1, 12, 0, tzinfo=ZoneInfo(key='UTC')),
            'widgets': [{'type': 'chart', 'data': {}}],
            'url': '/sefdsf5s54sdfsksdfs5',
            'authorization': 'private',
            'config_cascaded': {'setting1': 'value1',
            'setting2': 'value2'},
            'layout_content': {'section1': {}}
        }
        self.report = Report(**self.sample_data)
        self.headers = HttpSDKPOSTConnection().get_headers()
        self.api_url = HttpSDKPOSTConnection().get_url()

    def test_get_id_prefix(self):
        self.assertEqual(Report.get_id_prefix(), settings.REPORT_ID_PREFIX)

    def test_validate(self):
        expected_data = compress({'class_name': 'Report', 'method_name': 'validate', 'self_obj': {'created_on': {'__datetime__': '2023-09-09T09:09:09.000009+00:00'}, 'updated_on': {'__datetime__': '2023-09-09T09:09:09.000009+00:00'}, 'version': 'v1', 'id': 'repo_12345678', 'name': 'My Report', 'description': 'This is a sample report.', 'tags': ['tag1', 'tag2'], 'link_uid': None, 'workspace': 'my_workspace', 'date': '20220101', 'widgets': [{'type': 'chart', 'data': {}}], 'url': '/sefdsf5s54sdfsksdfs5', 'authorization': 'private', 'config_cascaded': {'setting1': 'value1', 'setting2': 'value2'}, 'layout_content': {'section1': {}}, '__class_path__': 'everysk.sdk.entities.report.base.Report'}, 'params': {}}, protocol='gzip', serialize='json')
        report: Report = self.report.copy()

        with mock.patch('requests.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            report.validate()

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            verify=settings.HTTP_DEFAULT_SSL_VERIFY,
            timeout=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT,
            data=expected_data
        )

    def test_query_load_with_id(self):
        expected_data = compress({'class_name': 'Report', 'method_name': 'retrieve', 'self_obj': None, 'params': {'entity_id': 'repo_1234567891011211234567890'}}, protocol='gzip', serialize='json')

        with mock.patch('requests.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            Report(id='repo_1234567891011211234567890', workspace='SampleWorkspace').load()

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            verify=settings.HTTP_DEFAULT_SSL_VERIFY,
            timeout=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT,
            data=expected_data
        )

    def test_query_load(self):
        expected_data = compress({'class_name': 'Query', 'method_name': 'load', 'self_obj': {'_klass': 'Report', 'filters': [['workspace', '=', 'SampleWorkspace'], ['link_uid', '=', 'SampleLinkUID']], 'order': [], 'projection': None, 'distinct_on': [], 'limit': None, 'offset': None, 'page_size': None, 'page_token': None, '_clean_order': [], '__class_path__': 'everysk.sdk.entities.query.Query'}, 'params': {'offset': None}}, protocol='gzip', serialize='json')

        with mock.patch('requests.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            Report(link_uid='SampleLinkUID', workspace='SampleWorkspace').load()

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            verify=settings.HTTP_DEFAULT_SSL_VERIFY,
            timeout=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT,
            data=expected_data
        )

    def test_entity_to_query(self):
        cmp_query = Report.query.where('url', self.report.url)
        query = Report(url=self.report.url).to_query() #pylint: disable=protected-access

        self.assertDictEqual(query, cmp_query)

    def test_check_query_raises_sdk_error(self):
        with self.assertRaises(SDKValueError) as context:
            Report(url=self.report.url, name='report_name').to_query()

        self.assertEqual(str(context.exception), "Can't filter by URL and Name, Tags or Link UID at the same time")
