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
from everysk.core.datetime import Date, DateTime
from everysk.core.exceptions import FieldValueError
from everysk.core.object import BaseDict
from everysk.core.unittests import TestCase

from everysk.sdk.entities.portfolio.security import Security


###############################################################################
#   Security TestCase Implementation
###############################################################################
class TestSecurity(TestCase):

    def setUp(self):
        # Sample data for valid initialization
        self.valid_data = {
            'status': 'OK',
            'symbol': 'AAPL',
            'id': 'unique123',
            'quantity': 100.0,
            'instrument_class': 'Equity',
            'maturity_date': Date(2025, 5, 1),
            'issue_date': Date(2020, 1, 1),
            'return_date': Date(2025, 12, 31),
            'settlement': Date(2020, 1, 2),
            'display': 'Apple Inc.',
            'comparable': 'Yes',
            'previous_quantity': 50.0,
            'extra_field1': 'extra_value1',  # This should be placed in `extra_data`
            'extra_field2': 'extra_value2'   # This should also be placed in `extra_data`
        }
        self.security = Security(**self.valid_data)

    def test_initialization(self):
        base_security = {
            'return_date': None,
            'status': None,
            'label': None,
            'ticker': None,
            'underlying': None,
            'symbol': None,
            'coupon': None,
            'issuer': None,
            'cost_price': None,
            'book': None,
            'warranty': None,
            'instrument_class': None,
            'maturity_date': None,
            'percent_index': None,
            'issuer_type': None,
            'fx_rate': None,
            'operation': None,
            'market_value_in_base': None,
            'asset_subclass': None,
            'id': None,
            'exchange': None,
            'premium': None,
            'instrument_type': None,
            'isin': None,
            'indexer': None,
            'unrealized_pl_in_base': None,
            'accounting': None,
            'hash': None,
            'comparable': None,
            'error_message': None,
            'asset_class': None,
            'issue_date': None,
            'display': None,
            'market_price': None,
            'multiplier': None,
            'unrealized_pl': None,
            'series': None,
            'trader': None,
            'name': None,
            'error_type': None,
            'strike': None,
            'settlement': None,
            'option_type': None,
            'market_value': None,
            'previous_quantity': None,
            'quantity': None,
            'trade_id': None,
            'issue_price': None,
            'rate': None,
            'instrument_subtype': None,
            'extra_data': None,
            'currency': None,
            'look_through_reference': None
        }

        self.assertDictEqual(Security().to_dict(), base_security)
        cmp_dict = base_security.copy()
        cmp_dict.update(extra_data={'var1': 2, 'var4': '20230102', 'var5': '20230102 02:03:04', 'var6': None})

        self.assertDictEqual(
            Security(
                extra_data={
                    'var1': 1,
                    'var2': [1,2,3],
                    'var3': {'a': 1},
                    'var4': Date(2023, 1, 1),
                    'var5': DateTime(2023, 1, 1, 2, 3, 4),
                    'var6': Undefined
                },
                var1=2,
                var2=[1,2,3],
                var3={'a': 1},
                var4= Date(2023, 1, 2),
                var5=DateTime(2023, 1, 2, 2, 3, 4),
                var6=None
            ).to_legacy_dict(),
            cmp_dict
        )

    def test_initialization_with_valid_data(self):
        security = Security(**self.valid_data)
        self.assertEqual(security.status, 'OK')
        self.assertEqual(security.id, 'unique123')
        self.assertEqual(security.extra_data['extra_field1'], 'extra_value1')
        self.assertEqual(security.extra_data['extra_field2'], 'extra_value2')

    def test_from_list_conversion(self):
        headers = list(self.valid_data.keys())
        values = list(self.valid_data.values())
        security = Security.from_list(values, headers)
        self.assertEqual(security.status, 'OK')
        self.assertEqual(security.id, 'unique123')
        self.assertEqual(security.extra_data['extra_field1'], 'extra_value1')

    def test_initialization_with_extra_data(self):
        data_with_extra = self.valid_data.copy()
        data_with_extra['random_key'] = 'random_value'
        security = Security(**data_with_extra)
        self.assertEqual(security.extra_data['random_key'], 'random_value')

    def test_symbol_length_validation(self):
        invalid_data = self.valid_data.copy()
        invalid_data['symbol'] = 'A' * (settings.SYMBOL_ID_MAX_LEN + 1)
        with self.assertRaisesRegex(FieldValueError, "The length '101' for attribute 'symbol' must be between '0' and '100'."):
            Security(**invalid_data)

    def test_security_id_length_validation(self):
        invalid_data = self.valid_data.copy()
        invalid_data['id'] = '1' * (settings.SYMBOL_ID_MAX_LEN + 1)
        with self.assertRaisesRegex(FieldValueError, "The length '101' for attribute 'id' must be between '1' and '100'."):
            Security(**invalid_data)

    def test_extra_data_initialization(self):
        # Test that fields not in the class annotations are moved to `extra_data`
        data_with_extra = self.valid_data.copy()
        data_with_extra['extra_data'] = {'random_field': 'random_value'}
        security = Security(**data_with_extra)
        self.assertIn('random_field', security.extra_data)
        self.assertEqual(security.extra_data['random_field'], 'random_value')

    def test_extra_data_empty_after_initialization(self):
        # Test that if no extra data is present, `extra_data` is set to None
        data_without_extra = self.valid_data.copy()
        data_without_extra.pop('extra_field1')
        data_without_extra.pop('extra_field2')
        security = Security(**data_without_extra)
        self.assertIsNone(security.extra_data)

    def test_generate_security_id(self):
        security_id1 = Security.generate_security_id()
        security_id2 = Security.generate_security_id()

        self.assertIsInstance(security_id1, str)
        self.assertIsInstance(security_id2, str)
        self.assertNotEqual(security_id1, security_id2)

    def test_sort_header(self):
        headers = ['status', 'symbol', 'quantity', 'instrument_class']
        headers_cmp = ['quantity', 'instrument_class', 'status', 'symbol']
        sorted_headers = Security.sort_header(headers_cmp)
        self.assertListEqual(sorted_headers, headers)

    def test_validate_required_fields_without_id(self):
        # Test if ID gets auto-generated if not provided
        data_without_id = self.valid_data.copy()
        data_without_id.pop('id')
        security = Security(**data_without_id)
        security.validate_required_fields()
        self.assertIsNotNone(security.id)

    def test_validate_required_fields_with_id(self):
        # Test if provided ID is not changed
        data_with_id = self.valid_data.copy()
        data_with_id['id'] = 'test_id'
        security = Security(**data_with_id)
        security.validate_required_fields()
        self.assertEqual(security.id, "test_id")

    def test_get_attr(self):
        ret = Security._get_attr(self.security, 'symbol') # pylint: disable=protected-access
        self.assertEqual(ret, 'AAPL')

    def test_get_attr_in_extra_data(self):
        valid_data = self.valid_data.copy()
        valid_data['extra_data'] = {'other_key': 'other_value'}
        security = Security(**valid_data)
        ret = Security._get_attr(security, 'other_key') # pylint: disable=protected-access
        self.assertEqual(ret, 'other_value')

    def test_get_attr_fallback(self):
        ret = Security._get_attr(self.security, 'inexistent_key', Security.generate_security_id) # pylint: disable=protected-access
        self.assertIsInstance(ret, str)

    def test_get_attr_inexistent(self):
        ret = Security._get_attr(self.security, 'inexistent_key') # pylint: disable=protected-access
        self.assertIsNone(ret)

    def test_generate_consolidation_key(self):
        ret = self.security.generate_consolidation_key(['symbol', 'instrument_class'])
        self.assertEqual(ret, 'AAPL_Equity')

    def test_to_list_without_headers(self):
        ret = self.security.to_list()
        self.assertListEqual(ret, ['OK', 'unique123', 'AAPL', 100.0, 'Equity', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, '20250501', None, None, None, None, None, None, None, None, None, None, '20200101', None, None, None, None, None, None, None, None, None, None, None, '20251231', '20200102', None, BaseDict(**{'extra_field1': 'extra_value1', 'extra_field2': 'extra_value2'}), None, 'Yes', 'Apple Inc.', None, None, 50.0])
