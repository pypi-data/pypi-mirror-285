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
from everysk.core.exceptions import FieldValueError, ReadonlyError, RequiredError
from everysk.core import slack
from everysk.core.unittests import TestCase, mock


class SlackTestCase(TestCase):

    def test_is_json(self):
        message = "The field 'is_json' value cannot be changed."
        self.assertRaisesRegex(
            FieldValueError,
            message,
            slack.Slack,
            title='Test',
            message='Message',
            is_json=False
        )
        with self.assertRaisesRegex(FieldValueError, message):
            obj = slack.Slack(title='Test', message='Message')
            obj.is_json = False

    def test_title(self):
        message = 'The title attribute is required.'
        self.assertRaisesRegex(RequiredError, message, slack.Slack, message='Message')

    def test_message(self):
        message = 'The message attribute is required.'
        self.assertRaisesRegex(RequiredError, message, slack.Slack, title='Title')

    def test_choices(self):
        message = r"The value 'banana' for field 'color' must be in this list \(None, 'danger', 'success', 'warning'\)."
        self.assertRaisesRegex(
            FieldValueError,
            message,
            slack.Slack,
            title='Test',
            message='Message',
            color='banana'
        )
        with self.assertRaisesRegex(FieldValueError, message):
            obj = slack.Slack(title='Test', message='Message')
            obj.color = 'banana'

    def test_color_map(self):
        message = "The field '_color_map' value cannot be changed."
        self.assertRaisesRegex(
            FieldValueError,
            message,
            slack.Slack,
            title='Test',
            message='Message',
            _color_map={'banana': '#f3f3f3'}
        )
        with self.assertRaisesRegex(FieldValueError, message):
            obj = slack.Slack(title='Test', message='Message')
            obj._color_map = {'banana': '#f3f3f3'}

        with self.assertRaisesRegex(ReadonlyError, 'This field value cannot be changed.'):
            obj = slack.Slack(title='Test', message='Message')
            obj._color_map['banana'] = '#f3f3f3'

    def test_get_payload(self):
        obj = slack.Slack(title='Test', message='Message')
        self.assertDictEqual(
            obj.get_payload(),
            {
                'attachments': [{
                    'color': '#000000',
                    'blocks': [
                        {
                            'text': {'emoji': True, 'text': 'Test', 'type': 'plain_text'},
                            'type': 'header'
                        },
                        {'type': 'divider'},
                        {
                            'text': {'text': 'Message', 'type': 'mrkdwn'},
                            'type': 'section'
                        },
                        {'type': 'divider'}
                    ],
                }]
            }
        )

    @mock.patch.object(slack.Slack, 'get_response')
    def test_send(self, get_response: mock.MagicMock):
        slack.Slack(title='Test', message='Message').send()
        get_response.assert_called_once_with()
