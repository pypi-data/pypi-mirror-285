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
from requests import Response
from everysk.core.fields import BoolField, ChoiceField, DictField, StrField
from everysk.core.http import HttpPOSTConnection

###############################################################################
#   Slack Class Implementation
###############################################################################
class Slack(HttpPOSTConnection):
    ## Private attributes
    _color_map = DictField(default={
        'danger': '#a90a05',
        'success': '#138138',
        'warning': '#e9932d'
    }, readonly=True)
    is_json = BoolField(default=True, readonly=True)

    ## Public attributes
    color = ChoiceField(default=None, choices=(None, 'danger', 'success', 'warning'))
    message = StrField(default=None, required=True)
    title = StrField(default=None, required=True)

    def get_payload(self) -> dict:
        """
        Convert all key/value on self to a dict object and apply some conversions.
        """
        return {
            'attachments': [{
                'color': self._color_map.get(self.color, '#000000'),
                'blocks': [
                    {
                        'type': 'header',
                        'text': {
                            'type': 'plain_text',
                            'text': self.title,
                            'emoji': True
                        }
                    },
                    {
                        'type': 'divider'
                    },
                    {
                        'type': 'section',
                        'text': {
                            'type': 'mrkdwn',
                            'text': self.message
                        }
                    },
                    {
                        'type': 'divider'
                    }
                ]
            }]
        }

    def send(self) -> Response:
        """ Sends the message to the Slack Channel """
        return self.get_response()
