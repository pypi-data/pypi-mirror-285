###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
import json
from os import environ
from everysk.config import settings
from everysk.core.compress import compress
from everysk.core.exceptions import HttpError, InvalidArgumentError
from everysk.core.http import HttpConnection, HttpConnectionConfig, HttpGETConnection, HttpPOSTConnection, HttpSDKPOSTConnection, HttpPOSTCompressedConnection, requests, time,log
from everysk.core.unittests import TestCase, mock


class FakeResponse:
    # https://everysk.atlassian.net/browse/COD-1047
    def __bool__(self):
        return False


class HttpConnectionConfigTestCase(TestCase):

    def test_default_attributes(self):
        obj = HttpConnectionConfig()
        self.assertEqual(obj.retry_end_seconds, 30)
        self.assertEqual(obj.retry_limit, 5)
        self.assertEqual(obj.retry_start_seconds, 5)
        self.assertIsInstance(HttpConnection._config, HttpConnectionConfig)

    def test_get_ssl_verify(self):
        obj = HttpConnectionConfig()
        self.assertTrue(obj.get_ssl_verify())
        obj.ssl_verify = False
        self.assertFalse(obj.get_ssl_verify())

    def test_get_ssl_verify_environment(self):
        obj = HttpConnectionConfig()
        self.assertTrue(obj.get_ssl_verify())
        environ['HTTP_REQUESTS_VERIFY'] = 'False'
        self.assertFalse(obj.get_ssl_verify())
        obj.ssl_verify = False
        environ['HTTP_REQUESTS_VERIFY'] = 'True'
        self.assertTrue(obj.get_ssl_verify())
        environ.pop('HTTP_REQUESTS_VERIFY')

    def test_user_agent_list(self):
        obj = HttpConnectionConfig()
        with open(obj.user_agents_file, 'r', encoding='utf-8') as fd:
            user_agents = json.load(fd)

        self.assertListEqual(obj.user_agents, user_agents)

    def test_get_random_agent(self):
        obj = HttpConnectionConfig()
        self.assertIn(obj.get_random_agent(), obj.user_agents)
        self.assertNotEqual(obj.get_random_agent(), obj.get_random_agent())


class HttpConnectionTestCase(TestCase):

    def test_get_url(self):
        http = HttpConnection(url='https://test.com')
        self.assertEqual(http.url, 'https://test.com')
        self.assertEqual(http.get_url(), 'https://test.com')

    def test_clean_response_200(self):
        response = mock.MagicMock()
        response.status_code = 200
        http = HttpConnection()
        self.assertEqual(http._clean_response(response), response) # pylint: disable=protected-access

    def test_clean_response_201(self):
        response = mock.MagicMock()
        response.status_code = 201
        http = HttpConnection()
        self.assertEqual(http._clean_response(response), response) # pylint: disable=protected-access

    def test_clean_response_202(self):
        response = mock.MagicMock()
        response.status_code = 200
        http = HttpConnection()
        self.assertEqual(http._clean_response(response), response) # pylint: disable=protected-access

    def test_clean_response_303(self):
        response = mock.MagicMock()
        response.status_code = 303
        http = HttpConnection()
        self.assertEqual(http._clean_response(response), response) # pylint: disable=protected-access

    def test_clean_response_500(self):
        response = mock.MagicMock()
        response.status_code = 500
        http = HttpConnection()
        self.assertRaises(HttpError, http._clean_response, response) # pylint: disable=protected-access

    def test_clean_without_status_code(self):
        # https://everysk.atlassian.net/browse/COD-1047
        response = FakeResponse()
        self.assertFalse(response)
        http = HttpConnection()
        http._clean_response(response) # pylint: disable=protected-access

    def test_get_headers(self):
        http = HttpConnection()
        self.assertDictEqual(
            http.get_headers(),
            {
                'Accept-Encoding': 'gzip, deflate;q=0.9',
                'Accept-Language': 'en-US, en;q=0.9, pt-BR;q=0.8, pt;q=0.7',
                'Cache-control': 'no-cache',
                'Connection': 'close',
                'Content-Type': 'text/html; charset=UTF-8',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
            }
        )

    def test_get_headers_attribute(self):
        http = HttpConnection(headers={'key': 'value'})
        self.assertDictEqual(
            http.get_headers(),
            {
                'Accept-Encoding': 'gzip, deflate;q=0.9',
                'Accept-Language': 'en-US, en;q=0.9, pt-BR;q=0.8, pt;q=0.7',
                'Cache-control': 'no-cache',
                'Connection': 'close',
                'Content-Type': 'text/html; charset=UTF-8',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                'key': 'value'
            }
        )

    def test_get_random_agent(self):
        obj = HttpConnection()
        self.assertEqual(obj.get_headers()['User-Agent'], obj.get_headers()['User-Agent'])
        with mock.patch('os.environ', {'HTTP_USE_RANDOM_USER_AGENT': 1}):
            self.assertNotEqual(obj.get_headers()['User-Agent'], obj.get_headers()['User-Agent'])

    def test_message_error_check(self):
        self.assertFalse(HttpConnection().message_error_check('text', 500))

    def test_get_response_from_url(self):
        self.assertIsNone(HttpConnection()._get_response_from_url()) # pylint: disable=protected-access

    @mock.patch.object(HttpConnection, '_clean_response', return_value='response')
    def test_get_response(self, _clean_response: mock.MagicMock):
        self.assertEqual(HttpConnection().get_response(), 'response')
        _clean_response.assert_called_once_with(None)

    @mock.patch.object(HttpConnection, '_clean_response', side_effect=HttpError('Error'))
    @mock.patch.object(HttpConnection, 'message_error_check', return_value=True)
    @mock.patch.object(time, 'sleep')
    def test_get_response_error(
        self, sleep: mock.MagicMock, message_error_check: mock.MagicMock, _clean_response: mock.MagicMock
    ):
        self.assertRaises(HttpError, HttpConnection().get_response)
        self.assertEqual(sleep.call_count, 4)
        self.assertEqual(message_error_check.call_count, 5)
        self.assertEqual(_clean_response.call_count, 5)


class HttpGETConnectionTestCase(TestCase):

    def setUp(self) -> None:
        self.old_get = requests.get
        self.response = mock.MagicMock()
        self.response.status_code = 200
        requests.get = mock.create_autospec(requests.get)
        requests.get.return_value = self.response

    def tearDown(self) -> None:
        requests.get = self.old_get

    def test_get_params(self):
        http = HttpGETConnection(url='https://test.com')
        self.assertIsNone(http.get_params())
        http.params = {'key': 'value'}
        self.assertDictEqual(http.get_params(), {'key': 'value'})

    def test_get_response(self):
        http = HttpGETConnection(url='https://test.com', params={'p1': 1, 'p2': 2})
        response = http.get_response()
        requests.get.assert_called_once_with(
            url='https://test.com',
            headers=http.get_headers(),
            params={'p1': 1, 'p2': 2},
            verify=True,
            timeout=30
        )
        self.assertEqual(response, requests.get.return_value)

    def test_user(self):
        http = HttpGETConnection(
            url='https://test.com',
            params={'p1': 1, 'p2': 2},
            user='user',
            password='pass'
        )
        response = http.get_response()
        requests.get.assert_called_once_with(
            url='https://test.com',
            headers=http.get_headers(),
            params={'p1': 1, 'p2': 2},
            timeout=30,
            verify=True,
            auth=('user', 'pass')
        )
        self.assertEqual(response, requests.get.return_value)

    @mock.patch.object(log, 'debug')
    def test_http_log_response(self, debug: mock.MagicMock):
        http = HttpGETConnection(url='https://test.com', params={'p1': 1, 'p2': 2}, user='user', password='pass')
        settings.HTTP_LOG_RESPONSE = True
        response = http.get_response()
        settings.HTTP_LOG_RESPONSE = False
        debug.assert_has_calls([
            mock.call('HTTP GET request: %s', {'url': 'https://test.com', 'headers': http.get_headers(), 'params': {'p1': 1, 'p2': 2}, 'verify': True, 'timeout': 30, 'auth': ('user', '***********')}),
            mock.call('HTTP GET response: %s', {'status_code': 200, 'time': self.response.elapsed.total_seconds.return_value, 'headers': self.response.headers, 'content': self.response.content})
        ])
        self.assertEqual(response, requests.get.return_value)

class HttpPOSTConnectionTestCase(TestCase):

    def setUp(self) -> None:
        self.old_post = requests.post
        self.response = mock.MagicMock()
        self.response.status_code = 200
        requests.post = mock.create_autospec(requests.post)
        requests.post.return_value = self.response

    def tearDown(self) -> None:
        requests.post = self.old_post

    def test_get_headers(self):
        http = HttpPOSTConnection(url='https://test.com')
        self.assertDictEqual(
            http.get_headers(),
            {
                'Accept-Encoding': 'gzip, deflate;q=0.9',
                'Accept-Language': 'en-US, en;q=0.9, pt-BR;q=0.8, pt;q=0.7',
                'Cache-control': 'no-cache',
                'Connection': 'close',
                'Content-Type': 'application/json; charset=utf-8',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
            }
        )

    def test_get_payload(self):
        http = HttpPOSTConnection(url='https://test.com')
        self.assertIsNone(http.get_payload())
        http.payload = {'key': 'value'}
        self.assertDictEqual(http.get_payload(), {'key': 'value'})

    def test_get_response(self):
        http = HttpPOSTConnection(url='https://test.com', payload={'p1': 1, 'p2': 2})
        response = http.get_response()
        requests.post.assert_called_once_with(
            headers=http.get_headers(),
            json={'p1': 1, 'p2': 2},
            url='https://test.com',
            verify=True,
            timeout=30
        )
        self.assertEqual(response, requests.post.return_value)

    def test_post_not_json(self):
        http = HttpPOSTConnection(url='https://test.com', is_json=False, payload={'p1': 1, 'p2': 2})
        response = http.get_response()
        self.assertDictEqual(
            http.get_headers(),
            {
                'Accept-Encoding': 'gzip, deflate;q=0.9',
                'Accept-Language': 'en-US, en;q=0.9, pt-BR;q=0.8, pt;q=0.7',
                'Cache-control': 'no-cache',
                'Connection': 'close',
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
            }
        )
        requests.post.assert_called_once_with(
            headers=http.get_headers(),
            data={'p1': 1, 'p2': 2},
            url='https://test.com',
            verify=True,
            timeout=30
        )

        self.assertEqual(response, requests.post.return_value)

    @mock.patch.object(log, 'debug')
    def test_http_log_response(self, debug: mock.MagicMock):
        http = HttpPOSTConnection(url='https://test.com', is_json=False, payload={'p1': 1, 'p2': 2})
        settings.HTTP_LOG_RESPONSE = True
        response = http.get_response()
        settings.HTTP_LOG_RESPONSE = False
        debug.assert_has_calls([
            mock.call('HTTP POST request: %s', {'url': 'https://test.com', 'headers': http.get_headers(), 'data': {'p1': 1, 'p2': 2}, 'verify': True, 'timeout': 30}),
            mock.call('HTTP POST response: %s', {'status_code': 200, 'time': self.response.elapsed.total_seconds.return_value, 'headers': self.response.headers, 'content': self.response.content})
        ])
        self.assertEqual(response, requests.post.return_value)

class HttpSDKPOSTConnectionTestCase(TestCase):

    def setUp(self) -> None:
        self.old_post = requests.post
        response = mock.MagicMock()
        response.status_code = 200
        requests.post = mock.create_autospec(requests.post)
        requests.post.return_value = response
        settings.EVERYSK_API_SID = 'SID'
        settings.EVERYSK_API_TOKEN = 'TOKEN'
        self.class_name = 'class_name'
        self.method_name = 'method_name'
        self.self_obj = 'self_obj'
        self.param = 'params'

    def tearDown(self) -> None:
        requests.post = self.old_post

    def test_init_without_url(self):
        http = HttpSDKPOSTConnection()
        self.assertIsNone(http.url)
        self.assertEqual(http.get_url(), 'https://api.everysk.com/v1/sdk_function')

    def test_get_headers_without_SID(self):
        settings.EVERYSK_API_SID = None
        http = HttpSDKPOSTConnection()
        with self.assertRaisesRegex(InvalidArgumentError, 'Invalid API SID'):
            http.get_headers()

    def test_get_headers_without_token(self):
        settings.EVERYSK_API_TOKEN = None
        http = HttpSDKPOSTConnection()
        with self.assertRaisesRegex(InvalidArgumentError, 'Invalid API TOKEN'):
            http.get_headers()

    def test_get_headers(self):
        http = HttpSDKPOSTConnection(url='https://test.com')
        self.assertDictEqual(
            http.get_headers(),
            {
                'Accept-Encoding': 'gzip, deflate;q=0.9',
                'Accept-Language': 'en-US, en;q=0.9, pt-BR;q=0.8, pt;q=0.7',
                'Authorization': 'Bearer SID:TOKEN',
                'Cache-control': 'no-cache',
                'Connection': 'close',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Content-Encoding': 'gzip',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
            }
        )

    def test_get_payload(self):
        http = HttpSDKPOSTConnection(url='https://test.com', class_name='class_name', method_name='method_name', self_obj={'self_obj': 'obj'}, params={})
        self.assertEqual(http.get_payload(), compress({'class_name': 'class_name', 'method_name': 'method_name', 'self_obj': {'self_obj': 'obj'}, 'params': {}}, protocol='gzip', serialize='json'))

    def test_get_url(self):
        http = HttpSDKPOSTConnection()
        expected_url = f'{settings.EVERYSK_SDK_URL}/{settings.EVERYSK_SDK_VERSION}/{settings.EVERYSK_SDK_ROUTE}'
        ret = http.get_url()

        self.assertEqual(ret, expected_url)

class HttpPOSTCompressedConnectionTestCase(TestCase):

    def test_get_payload(self):
        http = HttpPOSTCompressedConnection(url='https://test.com', payload={'p1': 1, 'p2': 2})
        self.assertEqual(http.get_payload(),  compress({'p1': 1, 'p2': 2}, protocol='gzip', serialize='json'))
