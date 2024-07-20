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
import logging
import sys
from contextlib import AbstractContextManager
from contextvars import ContextVar
from types import TracebackType
from threading import Thread
from typing import Any
from everysk.config import settings


# This only makes sense in Production
try:
    # Imports the Cloud Logging client library
    from google.cloud.logging.handlers import StructuredLogHandler # type: ignore
except ImportError:
    StructuredLogHandler = None

###############################################################################
#   LoggerManager Class Implementation
###############################################################################
class LoggerManager(AbstractContextManager):
    labels: ContextVar = ContextVar('everysk-log-labels', default={})
    token: str = None

    def __init__(self, labels: dict) -> None:
        """
        Context class to create a context manager for the Logger object.

        Args:
            labels (dict): The extra labels sent to Google Logging.

        Example:

            >>> from everysk.core.log import Logger, LoggerManager
            >>> log = Logger(name='log-test')
            >>> log.debug('Test')
            2024-02-07 12:49:10,640 - DEBUG - {} - Test
            >>> with LoggerManager(labels={'user_id': 1}):
            ...     log.debug('Test')
            2024-02-07 12:52:07,319 - DEBUG - {'user_id': 1} - Test
        """
        self.token = self.labels.set(labels)

    def __exit__(self, __exc_type: type[BaseException] | None, __exc_value: BaseException | None, __traceback: TracebackType | None) -> bool | None:
        """
        https://docs.python.org/3/library/stdtypes.html#contextmanager.__exit__

        Returns:
            bool | None: If return is False any exception will be raised.
        """
        self.labels.reset(self.token)
        return False

###############################################################################
#   Logger Class Implementation
###############################################################################
class Logger:
    """ The Logger cannot be a BaseObject class because it could be used inside base things """
    ## Private attributes
    # This needs to be initialized with an empty set because it will be a global list
    _deprecated_hash: set[str] = set()

    ## Public attributes
    google_project: str = None
    labels: dict = None
    level: int = None
    log: logging.Logger = None
    name: str = None
    output_format: str = None
    slack_url: str = None
    stacklevel: int = None

    def __init__(self, name: str = Undefined, google_project: str = Undefined, labels: dict = Undefined, level: int = Undefined, output_format: str = Undefined, slack_url: str = Undefined, stacklevel: int = Undefined) -> None:
        """
        Logger class used to send messages to STDOUT or Google CLoud Logging.

        Args:
            name (str, optional): The name of the log. Defaults to "root".
            google_project (str, optional): The name of the project inside Google. Defaults to Undefined.
            labels (dict, optional): Extra information sent to the log. Defaults to {}.
            level (int, optional): The level of the messages that this log will handle. Defaults to DEBUG.
            output_format (str, optional): The string that represents the output format for the log. Defaults to "%(asctime)s - %(levelname)s - %(labels)s - %(message)s".
            stacklevel (int, optional): The position used to show what file generated the message. Defaults to 2.

        Example:

            >>> from everysk.core.log import Logger
            >>> log = Logger(name='log-test')
            >>> log.debug('Test')
            2024-02-07 12:49:10,640 - DEBUG - {} - Test
        """
        if name == 'root':
            raise ValueError('The name of the log could not be "root".')

        self._set_value(name='name', value=name, default='everysk-root-log', klass=str)
        self._set_value(name='google_project', value=google_project, default=settings.EVERYSK_GOOGLE_CLOUD_PROJECT, klass=str)
        self._set_value(name='labels', value=labels, default={}, klass=dict)
        self._set_value(name='level', value=level, default=logging.DEBUG, klass=int)
        self._set_value(name='output_format', value=output_format, default='%(asctime)s - %(levelname)s - %(labels)s - %(message)s', klass=str)
        self._set_value(name='slack_url', value=slack_url, default=None, klass=str)
        self._set_value(name='stacklevel', value=stacklevel, default=2, klass=int)
        self.log = self.get_python_logger()

    ## Private methods
    def _set_value(self, name: str, value: Any, default: Any, klass: type) -> None:
        """
        Method used to validate the type and set the value.

        Args:
            name (str): Attribute name.
            value (Any): Value that should be validated.
            default (Any): Default value if "value" is Undefined.
            klass (type): Class used to check if the "value" is an instance.

        Raises:
            ValueError: If the value is not of the klass type.

        Returns:
            None

        Usage:
            >>> from everysk.core.log import Logger
            >>> obj = Logger()
            >>> obj._set_value(name='example_attribute', value=42, default=0, klass=int)
            >>> print(obj.example_attribute)
            >>> 42

        """
        if value is Undefined:
            value = default
        elif not isinstance(value, klass):
            raise ValueError(f'The "{name}" attribute must be a {klass}.')

        setattr(self, name, value)

    ## Methods
    def get_python_logger(self) -> logging.Logger:
        """
        Method that creates/get the Python Logger object and attach the correct handler.
        If you need to deactivate the Google Logging Handler, set the settings.EVERYSK_GOOGLE_CLOUD_LOGGING_INTEGRATION
        to False or do not install the Handler pip package.
        The default handler will be the stdout.

        Returns:
            logging.Logger: The Python Logger object.

        Usage:
            >>> logger = Logger(name='example_log')
            >>> python_logger = logger.get_python_logger()
            >>> print(python_logger)
            <Logger example_log (DEBUG)>

        """
        # Create the log
        log = logging.getLogger(self.name)
        log.setLevel(self.level)
        log.propagate = False # Don't pass message to others loggers

        # We should only have one handler per log name
        if not hasattr(log, 'handler'):
            if settings.EVERYSK_GOOGLE_CLOUD_LOGGING_INTEGRATION and self.google_project and StructuredLogHandler:
                log.handler = StructuredLogHandler(project_id=self.google_project, labels=self.labels)
            else:
                log.handler = logging.StreamHandler(stream=sys.stdout)

                # Set the format that the message is displayed
                log.handler.setFormatter(logging.Formatter(self.output_format))

            # Add the handler inside the log
            log.addHandler(log.handler)

        # Set the level that the handler will be using.
        log.handler.setLevel(self.level)

        return log

    def get_labels(self) -> dict:
        """
        The labels are extra information that the Google Logging uses to create filters.

        Normally we set one at every request to be able to filter all logs from one request.
        If they are not set an empty dict will be the default value.

        Returns:
            dict: The labels dictionary

        Usage:
            >>> from everysk.core.log import Logger
            >>> logger = Logger()
            >>> labels = logger.get_labels()
        """
        labels = self.labels.copy()
        context_labels = LoggerManager.labels.get()
        if context_labels:
            labels.update(context_labels)

        return labels

    def _get_kwargs(self) -> dict:
        """
        Method that create a dict to be used as **kwargs for all logs.
        """
        return {
            'extra': {'labels': self.get_labels()}, # Set extra labels for Google
            'stacklevel': self.stacklevel, # Change the source to be one of the "parents" caller
        }

    def _show_deprecated(self, _id: str, show_once: bool) -> bool:
        """
        If show_once is False this always return True, otherwise
        checks if this _id is in the self._deprecated_hash set.

        Args:
            _id (str): String that will be stored to be checked later
            show_once (bool): Flag to store or not the id.
        """
        if show_once:
            if _id in self._deprecated_hash:
                return False

            self._deprecated_hash.add(_id)

        return True

    ## Helpers
    def critical(self, msg: str, *args) -> None:
        """ Log 'msg % args' with severity 'CRITICAL'. """
        self.log.critical(msg, *args, **self._get_kwargs())

    def debug(self, msg: str, *args) -> None:
        """ Log 'msg % args' with severity 'DEBUG'. """
        self.log.debug(msg, *args, **self._get_kwargs())

    def error(self, msg: str, *args) -> None:
        """ Log 'msg % args' with severity 'ERROR'. """
        self.log.error(msg, *args, **self._get_kwargs())

    def exception(self, msg: str, *args) -> None:
        """ Log 'msg % args' with severity 'ERROR' with exception information. """
        self.log.exception(msg, *args, **self._get_kwargs())

    def info(self, msg: str, *args) -> None:
        """ Log 'msg % args' with severity 'INFO'. """
        self.log.info(msg, *args, **self._get_kwargs())

    def warning(self, msg: str, *args) -> None:
        """ Log 'msg % args' with severity 'WARNING'. """
        self.log.warning(msg, *args, **self._get_kwargs())

    def deprecated(self, msg: str, *args, show_once: bool = True) -> None:
        """
        Shows a DeprecationWarning message with severity 'WARNING'.
        If show_once is True, then the message will be showed only once.

        Args:
            msg (str): The message that must be showed.
            show_once (bool, optional): If the message must be showed only once. Defaults to True.
        """
        _id = hash(f'{msg}, {args}')
        if self._show_deprecated(_id=_id, show_once=show_once):
            msg = f'DeprecationWarning: {msg}'
            self.warning(msg, *args)

    def slack(self, title: str, message: str, color: str, url: str = None) -> None:
        """
        Send a message to a Slack channel using Slack WebHooks.
        https://api.slack.com/messaging/webhooks
        The same message will be sent to the default log:
            danger -> error
            success -> info
            warning -> warning

        Args:
            title (str): The title of the message.
            message (str): The body of the message.
            color (str): 'danger' | 'success' | 'warning'
            url (str, optional): The slack webhook url. Defaults to self.slack_url.
        """
        if url is None:
            if self.slack_url is None:
                url = settings.SLACK_URL
            else:
                url = self.slack_url

        # We send the message only if url is set and we are in PROD
        if url and settings.PROFILE == 'PROD' and 'unittest' not in sys.modules:
            # The import must be here to avoid circular import inside http module
            from everysk.core.slack import Slack # pylint: disable=import-outside-toplevel
            client = Slack(title=title, message=message, color=color, url=url)
            # This will send the message to Slack without block the request
            Thread(target=client.send).start()

        log_message = f'Slack message: {title} -> {message}'
        if color == 'danger':
            self.error(log_message)

        elif color == 'success':
            self.info(log_message)

        elif color == 'warning':
            self.warning(log_message)
