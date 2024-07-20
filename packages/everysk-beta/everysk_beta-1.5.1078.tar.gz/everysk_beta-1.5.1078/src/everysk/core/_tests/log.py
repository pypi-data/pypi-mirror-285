###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
# pylint: disable=protected-access
import sys
from logging import Logger as PythonLogger, DEBUG, INFO, StreamHandler
from everysk.config import settings
from everysk.core import log as log_module, slack as slack_module
from everysk.core.log import Logger, LoggerManager
from everysk.core.unittests import TestCase, mock


class LoggerManagerTestCase(TestCase):

    def test_context_manager(self):
        with LoggerManager(labels={'key': 'out'}):
            self.assertEqual(LoggerManager.labels.get(), {'key': 'out'})
            with LoggerManager(labels={'key': 'in'}):
                self.assertEqual(LoggerManager.labels.get(), {'key': 'in'})
            self.assertEqual(LoggerManager.labels.get(), {'key': 'out'})


class LoggerTestCase(TestCase):

    def test_logger_return(self):
        log = Logger('everysk-log-stdout-test')
        self.assertIsInstance(log.log, PythonLogger)

    def test_log_level(self):
        log = Logger(name='everysk-log-stdout-test', level=INFO)
        self.assertEqual(log.log.level, INFO)
        log = Logger(name='everysk-log-stdout-test', level=DEBUG)
        self.assertEqual(log.log.level, DEBUG)

    def test_log_propagate(self):
        log = Logger('everysk-log-stdout-test')
        self.assertFalse(log.log.propagate)

    def test_stdout_handler(self):
        log = Logger('everysk-log-stdout-test')
        handler = log.log.handlers[0]
        self.assertEqual(type(handler), StreamHandler)

    @mock.patch.object(log_module, 'StructuredLogHandler')
    def test_gcp_handler(self, StructuredLogHandler: mock.MagicMock): # pylint: disable=invalid-name
        log = Logger('everysk-log-gcp-test', google_project='test', labels={'request_id': 'uuid'})
        StructuredLogHandler.assert_called_once_with(project_id='test', labels={'request_id': 'uuid'})
        handler = log.log.handlers[0]
        self.assertEqual(handler, StructuredLogHandler.return_value)

    def test_handler_level(self):
        log = Logger(name='everysk-log-stdout-test', level=INFO)
        handler = log.log.handlers[0]
        self.assertEqual(handler.level, INFO)
        log = Logger(name='everysk-log-stdout-test', level=DEBUG)
        handler = log.log.handlers[0]
        self.assertEqual(handler.level, DEBUG)

    def test_handler_format(self):
        log = Logger(name='everysk-log-stdout-test', level=INFO)
        handler = log.log.handlers[0]
        self.assertEqual(
            handler.formatter._fmt,
            '%(asctime)s - %(levelname)s - %(labels)s - %(message)s'
        )

    @mock.patch.object(log_module.logging, 'getLogger')
    def test_context_manager_logger(self, getLogger: mock.MagicMock): # pylint: disable=invalid-name
        log = Logger(name='everysk-log-context-test')
        log.debug('MSG')
        with LoggerManager(labels={'key': 'out'}):
            log.debug('MSG')

            with LoggerManager(labels={'key': 'in'}):
                log.debug('MSG')

            log.debug('MSG')

        log.debug('MSG')

        getLogger.return_value.debug.assert_has_calls([
            mock.call('MSG', extra={'labels': {}}, stacklevel=2),
            mock.call('MSG', extra={'labels': {'key': 'out'}}, stacklevel=2),
            mock.call('MSG', extra={'labels': {'key': 'in'}}, stacklevel=2),
            mock.call('MSG', extra={'labels': {'key': 'out'}}, stacklevel=2),
            mock.call('MSG', extra={'labels': {}}, stacklevel=2),
        ])

    def test_get_labels_default(self):
        log = Logger(name='everysk-log-context-test')
        self.assertDictEqual(log.get_labels(), {})

    def test_get_labels_init(self):
        log = Logger(name='everysk-log-context-test', labels={'key': 'out'})
        self.assertDictEqual(log.get_labels(), {'key': 'out'})

    def test_get_labels_context(self):
        log = Logger(name='everysk-log-context-test', labels={'key': 'out'})
        with LoggerManager(labels={'key': 'in'}):
            self.assertDictEqual(log.get_labels(), {'key': 'in'})

        self.assertDictEqual(log.get_labels(), {'key': 'out'})

    def test_set_value_error(self):
        log = Logger(name='everysk-log-set-value-test')
        with self.assertRaisesRegex(ValueError, r"The \"attr\" attribute must be a \<class 'str'\>."):
            log._set_value(name='attr', value=1, default='def', klass=str)

    def test_set_value_default(self):
        log = Logger(name='everysk-log-set-value-test')
        log._set_value(name='attr', value=Undefined, default='def', klass=str)
        self.assertEqual(log.attr, 'def') # pylint: disable=no-member

    @mock.patch.object(log_module.logging, 'getLogger')
    def test_critical(self, getLogger: mock.MagicMock): # pylint: disable=invalid-name
        log = Logger(name='everysk-log-msg-test')
        log.critical('msg %s', 1)
        getLogger.return_value.critical.assert_called_once_with('msg %s', 1, extra={'labels': {}}, stacklevel=2)

    @mock.patch.object(log_module.logging, 'getLogger')
    def test_debug(self, getLogger: mock.MagicMock): # pylint: disable=invalid-name
        log = Logger(name='everysk-log-msg-test')
        log.debug('msg %s', 1)
        getLogger.return_value.debug.assert_called_once_with('msg %s', 1, extra={'labels': {}}, stacklevel=2)

    @mock.patch.object(log_module.logging, 'getLogger')
    def test_error(self, getLogger: mock.MagicMock): # pylint: disable=invalid-name
        log = Logger(name='everysk-log-msg-test')
        log.error('msg %s', 1)
        getLogger.return_value.error.assert_called_once_with('msg %s', 1, extra={'labels': {}}, stacklevel=2)

    @mock.patch.object(log_module.logging, 'getLogger')
    def test_exception(self, getLogger: mock.MagicMock): # pylint: disable=invalid-name
        log = Logger(name='everysk-log-msg-test')
        log.exception('msg %s', 1)
        getLogger.return_value.exception.assert_called_once_with('msg %s', 1, extra={'labels': {}}, stacklevel=2)

    @mock.patch.object(log_module.logging, 'getLogger')
    def test_info(self, getLogger: mock.MagicMock): # pylint: disable=invalid-name
        log = Logger(name='everysk-log-msg-test')
        log.info('msg %s', 1)
        getLogger.return_value.info.assert_called_once_with('msg %s', 1, extra={'labels': {}}, stacklevel=2)

    @mock.patch.object(log_module.logging, 'getLogger')
    def test_warning(self, getLogger: mock.MagicMock): # pylint: disable=invalid-name
        log = Logger(name='everysk-log-msg-test')
        log.warning('msg %s', 1)
        getLogger.return_value.warning.assert_called_once_with('msg %s', 1, extra={'labels': {}}, stacklevel=2)

    def test_default_value_name(self):
        # https://everysk.atlassian.net/browse/COD-3212
        log = Logger()
        self.assertEqual(log.name, 'everysk-root-log')
        with self.assertRaisesRegex(ValueError, 'The name of the log could not be "root".'):
            log = Logger(name='root')

    def test_get_kwargs(self):
        log = Logger('everysk-log-kwargs')
        self.assertDictEqual(log._get_kwargs(), {'extra': {'labels': {}}, 'stacklevel': 2})
        log = Logger('everysk-log-kwargs', labels={'key': 'value'})
        self.assertDictEqual(log._get_kwargs(), {'extra': {'labels': {'key': 'value'}}, 'stacklevel': 2})


@mock.patch.object(log_module.logging, 'getLogger')
class LoggerDeprecatedTestCase(TestCase):
    # pylint: disable=invalid-name

    def test_send_message(self, getLogger: mock.MagicMock):
        log = Logger(name='everysk-log-deprecated')
        log.deprecated('Teste')
        getLogger.return_value.warning.assert_called_once_with('DeprecationWarning: Teste', extra={'labels': {}}, stacklevel=2)

    def test_send_message_once(self, getLogger: mock.MagicMock):
        log = Logger(name='everysk-log-deprecated')
        log.deprecated('Teste 1', show_once=True)
        log.deprecated('Teste 1', show_once=True)
        getLogger.return_value.warning.assert_called_once_with('DeprecationWarning: Teste 1', extra={'labels': {}}, stacklevel=2)

    def test_send_message_twice(self, getLogger: mock.MagicMock):
        log = Logger(name='everysk-log-deprecated')
        log.deprecated('Teste 2', show_once=False)
        log.deprecated('Teste 2', show_once=False)
        getLogger.return_value.warning.assert_has_calls([
            mock.call('DeprecationWarning: Teste 2', extra={'labels': {}}, stacklevel=2),
            mock.call('DeprecationWarning: Teste 2', extra={'labels': {}}, stacklevel=2),
        ])


@mock.patch.object(slack_module, 'Slack')
class LoggerSlackTestCase(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.log = Logger(name='everysk-lib-test-slack-message')

    def setUp(self) -> None:
        self.old_profile = settings.PROFILE
        self.old_slack_url = settings.SLACK_URL
        settings.PROFILE = 'PROD'
        settings.SLACK_URL = 'http://localhost'
        # This removes the module from the cache
        sys.modules.pop('unittest')

    def tearDown(self) -> None:
        settings.PROFILE = self.old_profile
        settings.SLACK_URL = self.old_slack_url
        # Put back the module
        import unittest # pylint: disable=unused-import, import-outside-toplevel

    def test_danger(self, slack: mock.MagicMock):
        with mock.patch.object(self.log.log, 'error') as error:
            self.log.slack(title='Error', message='Error message', color='danger')
            error.assert_called_once_with('Slack message: Error -> Error message', extra={'labels': {}}, stacklevel=2)
        slack.assert_called_once_with(title='Error', message='Error message', color='danger', url=settings.SLACK_URL)

    def test_warning(self, slack: mock.MagicMock):
        with mock.patch.object(self.log.log, 'warning') as warning:
            self.log.slack(title='Warning', message='Warning message', color='warning')
            warning.assert_called_once_with('Slack message: Warning -> Warning message', extra={'labels': {}}, stacklevel=2)
        slack.assert_called_once_with(title='Warning', message='Warning message', color='warning', url=settings.SLACK_URL)

    def test_success(self, slack: mock.MagicMock):
        with mock.patch.object(self.log.log, 'info') as info:
            self.log.slack(title='Success', message='Success message', color='success')
            info.assert_called_once_with('Slack message: Success -> Success message', extra={'labels': {}}, stacklevel=2)
        slack.assert_called_once_with(title='Success', message='Success message', color='success', url=settings.SLACK_URL)

    def test_not_url(self, slack: mock.MagicMock):
        settings.SLACK_URL = None
        with mock.patch.object(self.log.log, 'error') as error:
            self.log.slack(title='Error', message='Error message', color='danger')
            error.assert_called_once_with('Slack message: Error -> Error message', extra={'labels': {}}, stacklevel=2)
        slack.assert_not_called()

    def test_not_prod(self, slack: mock.MagicMock):
        settings.PROFILE = 'DEV'
        with mock.patch.object(self.log.log, 'error') as error:
            self.log.slack(title='Error', message='Error message', color='danger')
            error.assert_called_once_with('Slack message: Error -> Error message', extra={'labels': {}}, stacklevel=2)
        slack.assert_not_called()

    def test_in_tests(self, slack: mock.MagicMock):
        import unittest # pylint: disable=unused-import, import-outside-toplevel
        with mock.patch.object(self.log.log, 'error') as error:
            self.log.slack(title='Error', message='Error message', color='danger')
            error.assert_called_once_with('Slack message: Error -> Error message', extra={'labels': {}}, stacklevel=2)
        slack.assert_not_called()

    def test_init_url(self, slack: mock.MagicMock):
        with mock.patch.object(self.log.log, 'error') as error:
            log = Logger(name='everysk-lib-test-slack-message', slack_url='http://example.com')
            log.slack(title='Error', message='Error message', color='danger')
            error.assert_called_once_with('Slack message: Error -> Error message', extra={'labels': {}}, stacklevel=2)
        slack.assert_called_once_with(title='Error', message='Error message', color='danger', url='http://example.com')

    def test_method_url(self, slack: mock.MagicMock):
        with mock.patch.object(self.log.log, 'error') as error:
            self.log.slack(title='Error', message='Error message', color='danger', url='http://google.com')
            error.assert_called_once_with('Slack message: Error -> Error message', extra={'labels': {}}, stacklevel=2)
        slack.assert_called_once_with(title='Error', message='Error message', color='danger', url='http://google.com')
