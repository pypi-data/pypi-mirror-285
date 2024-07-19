# -*- coding: utf-8; -*-

import sys
from unittest import TestCase
from unittest.mock import patch, MagicMock

import pytest

from wuttjamaican import util


class TestLoadEntryPoints(TestCase):

    def test_empty(self):
        # empty set returned for unknown group
        result = util.load_entry_points('this_should_never_exist!!!!!!')
        self.assertEqual(result, {})

    def test_basic(self):
        # load some entry points which should "always" be present,
        # even in a testing environment.  basic sanity check
        result = util.load_entry_points('console_scripts', ignore_errors=True)
        self.assertTrue(len(result) >= 1)
        self.assertIn('pip', result)

    def test_basic_pre_python_3_10(self):

        # the goal here is to get coverage for code which would only
        # run on python 3,9 and older, but we only need that coverage
        # if we are currently testing python 3.10+
        if sys.version_info.major == 3 and sys.version_info.minor < 10:
            pytest.skip("this test is not relevant before python 3.10")

        import importlib.metadata
        real_entry_points = importlib.metadata.entry_points()

        class FakeEntryPoints(dict):
            def get(self, group, default):
                return real_entry_points.select(group=group)

        importlib = MagicMock()
        importlib.metadata.entry_points.return_value = FakeEntryPoints()

        with patch.dict('sys.modules', **{'importlib': importlib}):

            # load some entry points which should "always" be present,
            # even in a testing environment.  basic sanity check
            result = util.load_entry_points('console_scripts', ignore_errors=True)
            self.assertTrue(len(result) >= 1)
            self.assertIn('pytest', result)

    def test_basic_pre_python_3_8(self):

        # the goal here is to get coverage for code which would only
        # run on python 3.7 and older, but we only need that coverage
        # if we are currently testing python 3.8+
        if sys.version_info.major == 3 and sys.version_info.minor < 8:
            pytest.skip("this test is not relevant before python 3.8")

        from importlib.metadata import entry_points
        real_entry_points = entry_points()

        class FakeEntryPoints(dict):
            def get(self, group, default):
                if hasattr(real_entry_points, 'select'):
                    return real_entry_points.select(group=group)
                return real_entry_points.get(group, [])

        importlib_metadata = MagicMock()
        importlib_metadata.entry_points.return_value = FakeEntryPoints()

        orig_import = __import__

        def mock_import(name, *args, **kwargs):
            if name == 'importlib.metadata':
                raise ImportError
            if name == 'importlib_metadata':
                return importlib_metadata
            return orig_import(name, *args, **kwargs)

        with patch('builtins.__import__', side_effect=mock_import):

            # load some entry points which should "always" be present,
            # even in a testing environment.  basic sanity check
            result = util.load_entry_points('console_scripts', ignore_errors=True)
            self.assertTrue(len(result) >= 1)
            self.assertIn('pytest', result)

    def test_error(self):

        # skip if < 3.8
        if sys.version_info.major == 3 and sys.version_info.minor < 8:
            pytest.skip("this requires python 3.8 for entry points via importlib")

        entry_point = MagicMock()
        entry_point.load.side_effect = NotImplementedError

        entry_points = MagicMock()
        entry_points.select.return_value = [entry_point]

        importlib = MagicMock()
        importlib.metadata.entry_points.return_value = entry_points

        with patch.dict('sys.modules', **{'importlib': importlib}):

            # empty set returned if errors suppressed
            result = util.load_entry_points('wuttatest.thingers', ignore_errors=True)
            self.assertEqual(result, {})
            importlib.metadata.entry_points.assert_called_once_with()
            entry_points.select.assert_called_once_with(group='wuttatest.thingers')
            entry_point.load.assert_called_once_with()

            # error is raised, if not suppressed
            importlib.metadata.entry_points.reset_mock()
            entry_points.select.reset_mock()
            entry_point.load.reset_mock()
            self.assertRaises(NotImplementedError, util.load_entry_points, 'wuttatest.thingers')
            importlib.metadata.entry_points.assert_called_once_with()
            entry_points.select.assert_called_once_with(group='wuttatest.thingers')
            entry_point.load.assert_called_once_with()


class TestLoadObject(TestCase):

    def test_missing_spec(self):
        self.assertRaises(ValueError, util.load_object, None)

    def test_basic(self):
        result = util.load_object('unittest:TestCase')
        self.assertIs(result, TestCase)


class TestMakeUUID(TestCase):

    def test_basic(self):
        uuid = util.make_uuid()
        self.assertEqual(len(uuid), 32)


class TestParseBool(TestCase):

    def test_null(self):
        self.assertIsNone(util.parse_bool(None))

    def test_bool(self):
        self.assertTrue(util.parse_bool(True))
        self.assertFalse(util.parse_bool(False))

    def test_string_true(self):
        self.assertTrue(util.parse_bool('true'))
        self.assertTrue(util.parse_bool('yes'))
        self.assertTrue(util.parse_bool('y'))
        self.assertTrue(util.parse_bool('on'))
        self.assertTrue(util.parse_bool('1'))

    def test_string_false(self):
        self.assertFalse(util.parse_bool('false'))
        self.assertFalse(util.parse_bool('no'))
        self.assertFalse(util.parse_bool('n'))
        self.assertFalse(util.parse_bool('off'))
        self.assertFalse(util.parse_bool('0'))
        # nb. assume false for unrecognized input
        self.assertFalse(util.parse_bool('whatever-else'))


class TestParseList(TestCase):

    def test_null(self):
        value = util.parse_list(None)
        self.assertIsInstance(value, list)
        self.assertEqual(len(value), 0)

    def test_list_instance(self):
        mylist = []
        value = util.parse_list(mylist)
        self.assertIs(value, mylist)

    def test_single_value(self):
        value = util.parse_list('foo')
        self.assertEqual(len(value), 1)
        self.assertEqual(value[0], 'foo')

    def test_single_value_padded_by_spaces(self):
        value = util.parse_list('   foo   ')
        self.assertEqual(len(value), 1)
        self.assertEqual(value[0], 'foo')

    def test_slash_is_not_a_separator(self):
        value = util.parse_list('/dev/null')
        self.assertEqual(len(value), 1)
        self.assertEqual(value[0], '/dev/null')

    def test_multiple_values_separated_by_whitespace(self):
        value = util.parse_list('foo bar baz')
        self.assertEqual(len(value), 3)
        self.assertEqual(value[0], 'foo')
        self.assertEqual(value[1], 'bar')
        self.assertEqual(value[2], 'baz')

    def test_multiple_values_separated_by_commas(self):
        value = util.parse_list('foo,bar,baz')
        self.assertEqual(len(value), 3)
        self.assertEqual(value[0], 'foo')
        self.assertEqual(value[1], 'bar')
        self.assertEqual(value[2], 'baz')

    def test_multiple_values_separated_by_whitespace_and_commas(self):
        value = util.parse_list('  foo,   bar   baz')
        self.assertEqual(len(value), 3)
        self.assertEqual(value[0], 'foo')
        self.assertEqual(value[1], 'bar')
        self.assertEqual(value[2], 'baz')

    def test_multiple_values_separated_by_whitespace_and_commas_with_some_quoting(self):
        value = util.parse_list("""
        foo
        "C:\\some path\\with spaces\\and, a comma",
        baz
        """)
        self.assertEqual(len(value), 3)
        self.assertEqual(value[0], 'foo')
        self.assertEqual(value[1], 'C:\\some path\\with spaces\\and, a comma')
        self.assertEqual(value[2], 'baz')

    def test_multiple_values_separated_by_whitespace_and_commas_with_single_quotes(self):
        value = util.parse_list("""
        foo
        'C:\\some path\\with spaces\\and, a comma',
        baz
        """)
        self.assertEqual(len(value), 3)
        self.assertEqual(value[0], 'foo')
        self.assertEqual(value[1], 'C:\\some path\\with spaces\\and, a comma')
        self.assertEqual(value[2], 'baz')
