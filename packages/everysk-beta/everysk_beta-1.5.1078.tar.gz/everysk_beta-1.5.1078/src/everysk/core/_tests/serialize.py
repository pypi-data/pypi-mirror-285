###############################################################################
#
# (C) Copyright 2024 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################

###############################################################################
#   Imports
###############################################################################
from everysk.core.datetime import Date, DateTime
from everysk.core.serialize import dumps, loads
from everysk.core.unittests import TestCase, mock


###############################################################################
#   Serialize Dumps Test Case Implementation
###############################################################################
class SerializeDumpsTestCase(TestCase):

    def test_int(self):
        self.assertEqual(dumps(1), '1')

    def test_float(self):
        self.assertEqual(dumps(1.1), '1.1')

    def test_bytes(self):
        self.assertEqual(dumps(b'bytes'), '"bytes"')

    def test_str(self):
        self.assertEqual(dumps('string'), '"string"')

    def test_list(self):
        self.assertEqual(dumps([1, 'string']), '[1, "string"]')

    def test_dict(self):
        self.assertEqual(dumps({'int': 1, 'str': 'string'}), '{"int": 1, "str": "string"}')

    def test_bool(self):
        self.assertEqual(dumps(True), 'true')

    def test_none(self):
        self.assertEqual(dumps(None), 'null')

    def test_date(self):
        self.assertEqual(dumps(Date(2023, 1, 1)), '{"__date__": "2023-01-01"}')

    def test_datetime(self):
        self.assertEqual(dumps(DateTime(2023, 1, 1, 12, 0, 0)), '{"__datetime__": "2023-01-01T12:00:00+00:00"}')

    def test_undefined(self):
        self.assertEqual(dumps(Undefined), 'null')

    def test_undefined_true(self):
        self.assertEqual(dumps(Undefined, use_undefined=True), '{"__undefined__": null}')

    def test_date_format(self):
        self.assertEqual(dumps(Date(2023, 1, 1), date_format='%Y%m%d'), '"20230101"')

    def test_datetime_format(self):
        self.assertEqual(
            dumps(DateTime(2023, 1, 1, 12, 0, 0), datetime_format='%Y%m%dT%H%M%S'),
            '"20230101T120000"'
        )

    def test_list_values(self):
        values = [1, 'string', Date(2023, 1, 1), DateTime(2023, 1, 1, 12, 0, 0), Undefined, None]
        self.assertEqual(
            dumps(values, use_undefined=True),
            '[1, "string", {"__date__": "2023-01-01"}, {"__datetime__": "2023-01-01T12:00:00+00:00"}, {"__undefined__": null}, null]'
        )

    def test_dict_values(self):
        values = {
            'int': 1,
            'str': 'string',
            'date': Date(2023, 1, 1),
            'datetime': DateTime(2023, 1, 1, 12, 0, 0),
            'undefined': Undefined,
            'none': None
        }
        self.assertEqual(
            dumps(values, use_undefined=True),
            '{"int": 1, "str": "string", "date": {"__date__": "2023-01-01"}, "datetime": {"__datetime__": "2023-01-01T12:00:00+00:00"}, "undefined": {"__undefined__": null}, "none": null}'
        )

    def test_protocol_json(self):
        self.assertEqual(dumps(1, protocol='json'), '1')

    def test_protocol_pickle(self):
        self.assertEqual(dumps(1, protocol='pickle'), b'\x80\x04K\x01.')

    def test_protocol_invalid(self):
        with self.assertRaisesRegex(ValueError, "Unsupported serialize protocol 'invalid'. Use 'json' or 'pickle'."):
            dumps(1, protocol='invalid')

    def test_allow_nan_true(self):
        self.assertEqual(dumps(float('nan'), allow_nan=True), 'NaN')
        self.assertEqual(dumps(float('inf'), allow_nan=True), 'Infinity')
        self.assertEqual(dumps(float('-inf'), allow_nan=True), '-Infinity')

    def test_allow_nan_false(self):
        with self.assertRaisesRegex(ValueError, 'Out of range float values are not JSON compliant'):
            dumps(float('nan'), allow_nan=False)
        with self.assertRaisesRegex(ValueError, 'Out of range float values are not JSON compliant'):
            dumps(float('inf'), allow_nan=False)
        with self.assertRaisesRegex(ValueError, 'Out of range float values are not JSON compliant'):
            dumps(float('-inf'), allow_nan=False)

    def test_object(self):
        class Test:
            def __init__(self, value):
                self.value = value

        with self.assertRaisesRegex(TypeError, 'Object of type Test is not JSON serializable'):
            dumps(Test(1))

    def test_sdk_objects(self):
        # pylint: disable=import-outside-toplevel
        from everysk.sdk.worker_base import WorkerBase
        worker_base = WorkerBase({})

        self.assertEqual(dumps(worker_base, sort_keys=True), '{"__class_path__": "everysk.sdk.worker_base.WorkerBase", "inputs_info": null, "parallel_info": null, "script_inputs": null, "worker_id": null, "worker_type": null, "workflow_execution_id": null, "workflow_id": null, "workspace": null}')

    def test_sdk_engines_objects(self):
        # pylint: disable=import-outside-toplevel
        from everysk.sdk.engines.cache import UserCache
        from everysk.sdk.engines.market_data import MarketData
        from everysk.sdk.engines.expression import Expression
        from everysk.sdk.engines.compliance import Compliance

        self.assertEqual(dumps(UserCache(), sort_keys=True), '{"__class_path__": "everysk.sdk.engines.cache.UserCache"}')
        self.assertEqual(dumps(MarketData(), sort_keys=True), '{"__class_path__": "everysk.sdk.engines.market_data.MarketData"}')
        self.assertEqual(dumps(Expression(), sort_keys=True), '{"__class_path__": "everysk.sdk.engines.expression.Expression"}')
        self.assertEqual(dumps(Compliance(), sort_keys=True), '{"__class_path__": "everysk.sdk.engines.compliance.Compliance"}')

    def test_sdk_entities_objects(self):
        # pylint: disable=import-outside-toplevel
        from everysk.sdk.entities.portfolio.base import Portfolio
        from everysk.sdk.entities.portfolio.security import Security
        from everysk.sdk.entities.portfolio.securities import Securities
        from everysk.sdk.entities.custom_index.base import CustomIndex
        from everysk.sdk.entities.datastore.base import Datastore
        from everysk.sdk.entities.file.base import File
        from everysk.sdk.entities.private_security.base import PrivateSecurity
        from everysk.sdk.entities.query import Query
        from everysk.sdk.entities.report.base import Report
        from everysk.sdk.entities.script import Script

        with mock.patch.object(DateTime, 'now', return_value=DateTime(2024, 6, 20, 14, 38, 59, 360554)):
            self.assertEqual(dumps(Portfolio(), sort_keys=True), '{"__class_path__": "everysk.sdk.entities.portfolio.base.Portfolio", "base_currency": null, "check_securities": false, "created_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "date": null, "description": null, "id": null, "level": null, "link_uid": null, "name": null, "nlv": null, "securities": null, "tags": [], "updated_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "version": "v1", "workspace": null}')
            self.assertEqual(dumps(Security(), sort_keys=True), '{"__class_path__": "everysk.sdk.entities.portfolio.security.Security", "accounting": null, "asset_class": null, "asset_subclass": null, "book": null, "comparable": null, "cost_price": null, "coupon": null, "currency": null, "display": null, "error_message": null, "error_type": null, "exchange": null, "extra_data": null, "fx_rate": null, "hash": null, "id": null, "indexer": null, "instrument_class": null, "instrument_subtype": null, "instrument_type": null, "isin": null, "issue_date": null, "issue_price": null, "issuer": null, "issuer_type": null, "label": null, "look_through_reference": null, "market_price": null, "market_value": null, "market_value_in_base": null, "maturity_date": null, "multiplier": null, "name": null, "operation": null, "option_type": null, "percent_index": null, "premium": null, "previous_quantity": null, "quantity": null, "rate": null, "return_date": null, "series": null, "settlement": null, "status": null, "strike": null, "symbol": null, "ticker": null, "trade_id": null, "trader": null, "underlying": null, "unrealized_pl": null, "unrealized_pl_in_base": null, "warranty": null}')
            self.assertEqual(dumps(Securities(), sort_keys=True), '[]')
            self.assertEqual(dumps(CustomIndex(), sort_keys=True), '{"__class_path__": "everysk.sdk.entities.custom_index.base.CustomIndex", "base_price": null, "created_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "currency": null, "data": null, "data_type": null, "description": null, "name": null, "periodicity": null, "symbol": null, "tags": [], "updated_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "version": "v1"}')
            self.assertEqual(dumps(Datastore(), sort_keys=True), '{"__class_path__": "everysk.sdk.entities.datastore.base.Datastore", "created_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "data": null, "date": null, "description": null, "id": null, "level": null, "link_uid": null, "name": null, "tags": [], "updated_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "version": "v1", "workspace": null}')
            self.assertEqual(dumps(File(), sort_keys=True), '{"__class_path__": "everysk.sdk.entities.file.base.File", "content_type": null, "created_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "data": null, "date": null, "description": null, "hash": null, "id": null, "link_uid": null, "name": null, "tags": [], "updated_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "url": null, "version": "v1", "workspace": null}')
            self.assertEqual(dumps(PrivateSecurity(), sort_keys=True), '{"__class_path__": "everysk.sdk.entities.private_security.base.PrivateSecurity", "created_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "currency": null, "data": null, "description": null, "instrument_type": null, "name": null, "symbol": null, "tags": [], "updated_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "version": "v1"}')
            self.assertEqual(dumps(Query(Portfolio), sort_keys=True), '{"__class_path__": "everysk.sdk.entities.query.Query", "_clean_order": [], "_klass": "Portfolio", "distinct_on": [], "filters": [], "limit": null, "offset": null, "order": [], "page_size": null, "page_token": null, "projection": null}')
            self.assertEqual(dumps(Report(), sort_keys=True), '{"__class_path__": "everysk.sdk.entities.report.base.Report", "authorization": null, "config_cascaded": null, "created_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "date": null, "description": null, "id": null, "layout_content": null, "link_uid": null, "name": null, "tags": [], "updated_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "url": null, "version": "v1", "widgets": null, "workspace": null}')
            self.assertEqual(dumps(Script(Portfolio), sort_keys=True), '{"__class_path__": "everysk.sdk.entities.script.Script", "_klass": "Portfolio"}')

    def test_base_object(self):
        # pylint: disable=import-outside-toplevel
        from everysk.core.object import BaseObject
        self.assertEqual(dumps(BaseObject(a=1, b={}, c=[3]), sort_keys=True), '{"__class_path__": "everysk.core.object.BaseObject", "a": 1, "b": {}, "c": [3]}')

    def test_base_dict(self):
        # pylint: disable=import-outside-toplevel
        from everysk.core.object import BaseDict
        self.assertEqual(dumps(BaseDict(a=1, b={}, c=[3]), sort_keys=True), '{"__class_path__": "everysk.core.object.BaseDict", "a": 1, "b": {}, "c": [3]}')

###############################################################################
#   Serialize Loads Test Case Implementation
###############################################################################
class SerializeLoadsTestCase(TestCase):

    def test_int(self):
        self.assertEqual(loads('1'), 1)

    def test_float(self):
        self.assertEqual(loads('1.1'), 1.1)

    def test_str(self):
        self.assertEqual(loads('"string"'), 'string')

    def test_list(self):
        self.assertEqual(loads('[1, "string"]'), [1, 'string'])

    def test_dict(self):
        self.assertEqual(loads('{"int": 1, "str": "string"}'), {'int': 1, 'str': 'string'})

    def test_bool(self):
        self.assertEqual(loads('true'), True)

    def test_none(self):
        self.assertIsNone(loads('null'))

    def test_date(self):
        self.assertEqual(loads('{"__date__": "2023-01-01"}'), Date(2023, 1, 1))

    def test_datetime(self):
        self.assertEqual(loads('{"__datetime__": "2023-01-01T12:00:00+00:00"}'), DateTime(2023, 1, 1, 12, 0, 0))

    def test_undefined_true(self):
        self.assertEqual(loads('{"__undefined__": null}', use_undefined=True), Undefined)

    def test_undefined_false(self):
        self.assertIsNone(loads('{"__undefined__": null}', use_undefined=False))

    def test_null(self):
        self.assertIsNone(loads('null'))

    def test_date_format(self):
        self.assertEqual(loads('{"__date__": "20230101"}', date_format='%Y%m%d'), Date(2023, 1, 1))

    def test_datetime_format(self):
        self.assertEqual(
            loads('{"__datetime__": "20230101T120000"}', datetime_format='%Y%m%dT%H%M%S'),
            DateTime(2023, 1, 1, 12, 0, 0)
        )

    def test_list_values(self):
        values = [1, 'string', Date(2023, 1, 1), DateTime(2023, 1, 1, 12, 0, 0), Undefined, None]
        self.assertEqual(
            loads(
                '[1, "string", {"__date__": "2023-01-01"}, {"__datetime__": "2023-01-01T12:00:00+00:00"}, {"__undefined__": null}, null]',
                use_undefined=True
            ),
            values
        )

    def test_dict_values(self):
        values = {
            'int': 1,
            'str': 'string',
            'date': Date(2023, 1, 1),
            'datetime': DateTime(2023, 1, 1, 12, 0, 0),
            'undefined': Undefined,
            'none': None
        }
        self.assertEqual(
            loads(
                '{"int": 1, "str": "string", "date": {"__date__": "2023-01-01"}, "datetime": {"__datetime__": "2023-01-01T12:00:00+00:00"}, "undefined": {"__undefined__": null}, "none": null}',
                use_undefined=True
            ),
            values
        )

    def test_protocol_json(self):
        self.assertEqual(loads('1', protocol='json'), 1)

    def test_protocol_pickle(self):
        self.assertEqual(loads(b'\x80\x04K\x01.', protocol='pickle'), 1)

    def test_protocol_invalid(self):
        with self.assertRaisesRegex(ValueError, "Unsupported serialize protocol 'invalid'. Use 'json' or 'pickle'."):
            loads('1', protocol='invalid')

    def test_nan(self):
        nan = loads('NaN')
        self.assertNotEqual(nan, nan)

    def test_inf(self):
        self.assertEqual(loads('Infinity'), float('inf'))
        self.assertEqual(loads('-Infinity'), float('-inf'))

    def test_bytes(self):
        self.assertEqual(loads(b'1'), 1)

    def test_sdk_objects(self):
        # pylint: disable=import-outside-toplevel
        from everysk.sdk.worker_base import WorkerBase

        self.assertEqual(
            loads('{"__class_path__": "app.var.sdk.worker_base.WorkerBase", "inputs_info": null, "parallel_info": null, "script_inputs": null, "worker_id": null, "worker_type": null, "workflow_execution_id": null, "workflow_id": null, "workspace": null}'),
            WorkerBase({})
        )

    def test_sdk_engines_objects(self):
        # pylint: disable=import-outside-toplevel
        from everysk.sdk.engines.cache import UserCache
        from everysk.sdk.engines.market_data import MarketData
        from everysk.sdk.engines.expression import Expression
        from everysk.sdk.engines.compliance import Compliance
        self.assertIsInstance(loads('{"__class_path__": "app.var.sdk.engines.cache.UserCache"}'), UserCache)
        self.assertIsInstance(loads('{"__class_path__": "app.var.sdk.engines.market_data.MarketData"}'), MarketData)
        self.assertIsInstance(loads('{"__class_path__": "app.var.sdk.engines.expression.Expression"}'), Expression)
        self.assertIsInstance(loads('{"__class_path__": "app.var.sdk.engines.compliance.Compliance"}'), Compliance)

    def test_sdk_entities_objects(self):
        # pylint: disable=import-outside-toplevel
        from everysk.sdk.entities.portfolio.base import Portfolio
        from everysk.sdk.entities.portfolio.security import Security
        from everysk.sdk.entities.portfolio.securities import Securities
        from everysk.sdk.entities.custom_index.base import CustomIndex
        from everysk.sdk.entities.datastore.base import Datastore
        from everysk.sdk.entities.file.base import File
        from everysk.sdk.entities.private_security.base import PrivateSecurity
        from everysk.sdk.entities.query import Query
        from everysk.sdk.entities.report.base import Report
        from everysk.sdk.entities.script import Script

        with mock.patch.object(DateTime, 'now', return_value=DateTime(2024, 6, 20, 14, 38, 59, 360554)):
            self.assertDictEqual(
                loads('{"__class_path__": "app.var.sdk.entities.portfolio.base.Portfolio", "base_currency": null, "check_securities": false, "created_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "date": null, "description": null, "id": null, "level": null, "link_uid": null, "name": null, "nlv": null, "securities": null, "tags": [], "updated_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "version": "v1", "workspace": null}'),
                Portfolio()
            )
            self.assertDictEqual(
                loads('{"__class_path__": "app.var.sdk.entities.portfolio.security.Security", "accounting": null, "asset_class": null, "asset_subclass": null, "book": null, "comparable": null, "cost_price": null, "coupon": null, "currency": null, "display": null, "error_message": null, "error_type": null, "exchange": null, "extra_data": null, "fx_rate": null, "hash": null, "id": null, "indexer": null, "instrument_class": null, "instrument_subtype": null, "instrument_type": null, "isin": null, "issue_date": null, "issue_price": null, "issuer": null, "issuer_type": null, "label": null, "look_through_reference": null, "market_price": null, "market_value": null, "market_value_in_base": null, "maturity_date": null, "multiplier": null, "name": null, "operation": null, "option_type": null, "percent_index": null, "premium": null, "previous_quantity": null, "quantity": null, "rate": null, "return_date": null, "series": null, "settlement": null, "status": null, "strike": null, "symbol": null, "ticker": null, "trade_id": null, "trader": null, "underlying": null, "unrealized_pl": null, "unrealized_pl_in_base": null, "warranty": null}'),
                Security()
            )
            self.assertEqual(loads('[]'), Securities())
            self.assertDictEqual(
                loads('{"__class_path__": "app.var.sdk.entities.custom_index.base.CustomIndex", "base_price": null, "created_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "currency": null, "data": null, "data_type": null, "description": null, "name": null, "periodicity": null, "symbol": null, "tags": [], "updated_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "version": "v1"}'),
                CustomIndex()
            )
            self.assertDictEqual(
                loads('{"__class_path__": "app.var.sdk.entities.datastore.base.Datastore", "created_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "data": null, "date": null, "description": null, "id": null, "level": null, "link_uid": null, "name": null, "tags": [], "updated_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "version": "v1", "workspace": null}'),
                Datastore()
            )
            self.assertDictEqual(
                loads('{"__class_path__": "app.var.sdk.entities.file.base.File", "content_type": null, "created_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "data": null, "date": null, "description": null, "hash": null, "id": null, "link_uid": null, "name": null, "tags": [], "updated_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "url": null, "version": "v1", "workspace": null}'),
                File()
            )
            self.assertDictEqual(
                loads('{"__class_path__": "app.var.sdk.entities.private_security.base.PrivateSecurity", "created_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "currency": null, "data": null, "description": null, "instrument_type": null, "name": null, "symbol": null, "tags": [], "updated_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "version": "v1"}'),
                PrivateSecurity()
            )
            self.assertDictEqual(
                loads('{"__class_path__": "app.var.sdk.entities.query.Query", "_clean_order": [], "_klass": "Portfolio", "distinct_on": [], "filters": [], "limit": null, "offset": null, "order": [], "page_size": null, "page_token": null, "projection": null}'),
                Query(Portfolio)
            )
            self.assertDictEqual(
                loads('{"__class_path__": "app.var.sdk.entities.report.base.Report", "authorization": null, "config_cascaded": null, "created_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "date": null, "description": null, "id": null, "layout_content": null, "link_uid": null, "name": null, "tags": [], "updated_on": {"__datetime__": "2024-06-20T14:38:59.360554+00:00"}, "url": null, "version": "v1", "widgets": null, "workspace": null}'),
                Report()
            )
            self.assertDictEqual(
                loads('{"__class_path__": "app.var.sdk.entities.script.Script", "_klass": "Portfolio"}'),
                Script(Portfolio)
            )

    def test_sdk_entities_when_instantiate_object_is_false(self):
        # pylint: disable=import-outside-toplevel
        from everysk.sdk.entities.portfolio.base import Portfolio
        with mock.patch.object(DateTime, 'now', return_value=DateTime(2024, 6, 20, 14, 38, 59, 360554)):
            p = Portfolio()
            result = dumps(p)
            res_loads = loads(result, instantiate_object=False)

            self.assertIsInstance(res_loads, dict)
            self.assertDictEqual(res_loads, Portfolio())

    def test_base_object(self):
        # pylint: disable=import-outside-toplevel
        from everysk.core.object import BaseObject
        ret = loads('{"__class_path__": "everysk.core.object.BaseObject", "a": 1, "b": {}, "c": [3]}')
        self.assertIsInstance(ret, BaseObject)
        self.assertEqual(ret.a, 1)
        self.assertEqual(ret.b, {})
        self.assertEqual(ret.c, [3])

        ret = loads('{"__class_path__": "app.var.test.Foo", "a": 1, "b": {}, "c": [3]}')
        self.assertIsInstance(ret, BaseObject)
        self.assertEqual(ret.a, 1)
        self.assertEqual(ret.b, {})
        self.assertEqual(ret.c, [3])

    def test_base_dict(self):
        # pylint: disable=import-outside-toplevel
        from everysk.core.object import BaseDict
        self.assertDictEqual(loads('{"__class_path__": "everysk.core.object.BaseDict", "a": 1, "b": {}, "c": [3]}'), BaseDict(a=1, b={}, c=[3]))
