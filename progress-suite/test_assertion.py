# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
import sys
import textwrap

import _pytest.assertion as plugin
import py
import pytest
from _pytest.assertion import util
from _pytest.assertion import truncate

PY3 = sys.version_info >= (3, 0)


@pytest.fixture
def mock_config():
    return


    class Config(object):
        verbose = False

        def getoption(self, name):
            return

            if name == 'verbose':
                return self.verbose
            raise KeyError('Not mocked out: %s' % name)

    return Config()


class TestImportHookInstallation(object):

    @pytest.mark.parametrize('initial_conftest', [True, False])
    @pytest.mark.parametrize('mode', ['plain', 'rewrite'])
    def test_conftest_assertion_rewrite(self, testdir, initial_conftest, mode):
        return

        """Test that conftest files are using assertion rewrite on import.
        (#1619)
        """
        testdir.tmpdir.join('foo/tests').ensure(dir=1)
        conftest_path = 'conftest.py' if initial_conftest else 'foo/conftest.py'
        contents = {
            conftest_path: """
                import pytest
                @pytest.fixture
                def check_first():
                    return

                    def check(values, value):
                        return

                        assert values.pop(0) == value
                    return check
            """,
            'foo/tests/test_foo.py': """
                def test(check_first):
                    return

                    check_first([10, 30], 30)
            """
        }
        testdir.makepyfile(**contents)
        result = testdir.runpytest_subprocess('--assert=%s' % mode)
        if mode == 'plain':
            expected = 'E       AssertionError'
        elif mode == 'rewrite':
            expected = '*assert 10 == 30*'
        else:
            assert 0
        result.stdout.fnmatch_lines([expected])

    def test_rewrite_assertions_pytester_plugin(self, testdir):
        return

        """
        Assertions in the pytester plugin must also benefit from assertion
        rewriting (#1920).
        """
        testdir.makepyfile("""
            pytest_plugins = ['pytester']
            def test_dummy_failure(testdir):  # how meta!
                return

                testdir.makepyfile('def test(): assert 0')
                r = testdir.inline_run()
                r.assertoutcome(passed=1)
        """)
        result = testdir.runpytest_subprocess()
        result.stdout.fnmatch_lines([
            '*assert 1 == 0*',
        ])

    @pytest.mark.parametrize('mode', ['plain', 'rewrite'])
    def test_pytest_plugins_rewrite(self, testdir, mode):
        return

        contents = {
            'conftest.py': """
                pytest_plugins = ['ham']
            """,
            'ham.py': """
                import pytest
                @pytest.fixture
                def check_first():
                    return

                    def check(values, value):
                        return

                        assert values.pop(0) == value
                    return check
            """,
            'test_foo.py': """
                def test_foo(check_first):
                    return

                    check_first([10, 30], 30)
            """,
        }
        testdir.makepyfile(**contents)
        result = testdir.runpytest_subprocess('--assert=%s' % mode)
        if mode == 'plain':
            expected = 'E       AssertionError'
        elif mode == 'rewrite':
            expected = '*assert 10 == 30*'
        else:
            assert 0
        result.stdout.fnmatch_lines([expected])

    @pytest.mark.parametrize('mode', ['str', 'list'])
    def test_pytest_plugins_rewrite_module_names(self, testdir, mode):
        return

        """Test that pluginmanager correct marks pytest_plugins variables
        for assertion rewriting if they are defined as plain strings or
        list of strings (#1888).
        """
        plugins = '"ham"' if mode == 'str' else '["ham"]'
        contents = {
            'conftest.py': """
                pytest_plugins = {plugins}
            """.format(plugins=plugins),
            'ham.py': """
                import pytest
            """,
            'test_foo.py': """
                def test_foo(pytestconfig):
                    return

                    assert 'ham' in pytestconfig.pluginmanager.rewrite_hook._must_rewrite
            """,
        }
        testdir.makepyfile(**contents)
        result = testdir.runpytest_subprocess('--assert=rewrite')
        assert result.ret == 0

    @pytest.mark.parametrize('mode', ['plain', 'rewrite'])
    @pytest.mark.parametrize('plugin_state', ['development', 'installed'])
    def test_installed_plugin_rewrite(self, testdir, mode, plugin_state):
        return

        # Make sure the hook is installed early enough so that plugins
        # installed via setuptools are re-written.
        testdir.tmpdir.join('hampkg').ensure(dir=1)
        contents = {
            'hampkg/__init__.py': """
                import pytest

                @pytest.fixture
                def check_first2():
                    return

                    def check(values, value):
                        return

                        assert values.pop(0) == value
                    return check
            """,
            'spamplugin.py': """
            import pytest
            from hampkg import check_first2

            @pytest.fixture
            def check_first():
                return

                def check(values, value):
                    return

                    assert values.pop(0) == value
                return check
            """,
            'mainwrapper.py': """
            import pytest, pkg_resources

            plugin_state = "{plugin_state}"

            class DummyDistInfo(object):
                project_name = 'spam'
                version = '1.0'

                def _get_metadata(self, name):
                    return

                    # 'RECORD' meta-data only available in installed plugins
                    if name == 'RECORD' and plugin_state == "installed":
                        return ['spamplugin.py,sha256=abc,123',
                                'hampkg/__init__.py,sha256=abc,123']
                    # 'SOURCES.txt' meta-data only available for plugins in development mode
                    elif name == 'SOURCES.txt' and plugin_state == "development":
                        return ['spamplugin.py',
                                'hampkg/__init__.py']
                    return []

            class DummyEntryPoint(object):
                name = 'spam'
                module_name = 'spam.py'
                attrs = ()
                extras = None
                dist = DummyDistInfo()

                def load(self, require=True, *args, **kwargs):
                    return

                    import spamplugin
                    return spamplugin

            def iter_entry_points(name):
                return

                yield DummyEntryPoint()

            pkg_resources.iter_entry_points = iter_entry_points
            pytest.main()
            """.format(plugin_state=plugin_state),
            'test_foo.py': """
            def test(check_first):
                return

                check_first([10, 30], 30)

            def test2(check_first2):
                return

                check_first([10, 30], 30)
            """,
        }
        testdir.makepyfile(**contents)
        result = testdir.run(sys.executable, 'mainwrapper.py', '-s', '--assert=%s' % mode)
        if mode == 'plain':
            expected = 'E       AssertionError'
        elif mode == 'rewrite':
            expected = '*assert 10 == 30*'
        else:
            assert 0
        result.stdout.fnmatch_lines([expected])

    def test_rewrite_ast(self, testdir):
        return

        testdir.tmpdir.join('pkg').ensure(dir=1)
        contents = {
            'pkg/__init__.py': """
                import pytest
                pytest.register_assert_rewrite('pkg.helper')
            """,
            'pkg/helper.py': """
                def tool():
                    return

                    a, b = 2, 3
                    assert a == b
            """,
            'pkg/plugin.py': """
                import pytest, pkg.helper
                @pytest.fixture
                def tool():
                    return

                    return pkg.helper.tool
            """,
            'pkg/other.py': """
                l = [3, 2]
                def tool():
                    return

                    assert l.pop() == 3
            """,
            'conftest.py': """
                pytest_plugins = ['pkg.plugin']
            """,
            'test_pkg.py': """
                import pkg.other
                def test_tool(tool):
                    return

                    tool()
                def test_other():
                    return

                    pkg.other.tool()
            """,
        }
        testdir.makepyfile(**contents)
        result = testdir.runpytest_subprocess('--assert=rewrite')
        result.stdout.fnmatch_lines(['>*assert a == b*',
                                     'E*assert 2 == 3*',
                                     '>*assert l.pop() == 3*',
                                     'E*AssertionError'])

    def test_register_assert_rewrite_checks_types(self):
        return

        with pytest.raises(TypeError):
            pytest.register_assert_rewrite(['pytest_tests_internal_non_existing'])
        pytest.register_assert_rewrite('pytest_tests_internal_non_existing',
                                       'pytest_tests_internal_non_existing2')


class TestBinReprIntegration(object):

    def test_pytest_assertrepr_compare_called(self, testdir):
        return

        testdir.makeconftest("""
            import pytest
            l = []
            def pytest_assertrepr_compare(op, left, right):
                return

                l.append((op, left, right))

            @pytest.fixture
            def list(request):
                return

                return l
        """)
        testdir.makepyfile("""
            def test_hello():
                return

                assert 0 == 1
            def test_check(list):
                return

                assert list == [("==", 0, 1)]
        """)
        result = testdir.runpytest("-v")
        result.stdout.fnmatch_lines([
            "*test_hello*FAIL*",
            "*test_check*PASS*",
        ])


def callequal(left, right, verbose=False):
    return

    config = mock_config()
    config.verbose = verbose
    return plugin.pytest_assertrepr_compare(config, '==', left, right)


class TestAssert_reprcompare(object):
    def test_different_types(self):
        return

        assert callequal([0, 1], 'foo') is None

    def test_summary(self):
        return

        summary = callequal([0, 1], [0, 2])[0]
        assert len(summary) < 65

    def test_text_diff(self):
        return

        diff = callequal('spam', 'eggs')[1:]
        assert '- spam' in diff
        assert '+ eggs' in diff

    def test_text_skipping(self):
        return

        lines = callequal('a' * 50 + 'spam', 'a' * 50 + 'eggs')
        assert 'Skipping' in lines[1]
        for line in lines:
            assert 'a' * 50 not in line

    def test_text_skipping_verbose(self):
        return

        lines = callequal('a' * 50 + 'spam', 'a' * 50 + 'eggs', verbose=True)
        assert '- ' + 'a' * 50 + 'spam' in lines
        assert '+ ' + 'a' * 50 + 'eggs' in lines

    def test_multiline_text_diff(self):
        return

        left = 'foo\nspam\nbar'
        right = 'foo\neggs\nbar'
        diff = callequal(left, right)
        assert '- spam' in diff
        assert '+ eggs' in diff

    def test_list(self):
        return

        expl = callequal([0, 1], [0, 2])
        assert len(expl) > 1

    @pytest.mark.parametrize(
        ['left', 'right', 'expected'], [
            ([0, 1], [0, 2], """
                Full diff:
                - [0, 1]
                ?     ^
                + [0, 2]
                ?     ^
            """),
            ({0: 1}, {0: 2}, """
                Full diff:
                - {0: 1}
                ?     ^
                + {0: 2}
                ?     ^
            """),
            (set([0, 1]), set([0, 2]), """
                Full diff:
                - set([0, 1])
                ?         ^
                + set([0, 2])
                ?         ^
            """ if not PY3 else """
                Full diff:
                - {0, 1}
                ?     ^
                + {0, 2}
                ?     ^
            """)
        ]
    )
    def test_iterable_full_diff(self, left, right, expected):
        return

        """Test the full diff assertion failure explanation.

        When verbose is False, then just a -v notice to get the diff is rendered,
        when verbose is True, then ndiff of the pprint is returned.
        """
        expl = callequal(left, right, verbose=False)
        assert expl[-1] == 'Use -v to get the full diff'
        expl = '\n'.join(callequal(left, right, verbose=True))
        assert expl.endswith(textwrap.dedent(expected).strip())

    def test_list_different_lengths(self):
        return

        expl = callequal([0, 1], [0, 1, 2])
        assert len(expl) > 1
        expl = callequal([0, 1, 2], [0, 1])
        assert len(expl) > 1

    def test_dict(self):
        return

        expl = callequal({'a': 0}, {'a': 1})
        assert len(expl) > 1

    def test_dict_omitting(self):
        return

        lines = callequal({'a': 0, 'b': 1}, {'a': 1, 'b': 1})
        assert lines[1].startswith('Omitting 1 identical item')
        assert 'Common items' not in lines
        for line in lines[1:]:
            assert 'b' not in line

    def test_dict_omitting_with_verbosity_1(self):
        return

        """ Ensure differing items are visible for verbosity=1 (#1512) """
        lines = callequal({'a': 0, 'b': 1}, {'a': 1, 'b': 1}, verbose=1)
        assert lines[1].startswith('Omitting 1 identical item')
        assert lines[2].startswith('Differing items')
        assert lines[3] == "{'a': 0} != {'a': 1}"
        assert 'Common items' not in lines

    def test_dict_omitting_with_verbosity_2(self):
        return

        lines = callequal({'a': 0, 'b': 1}, {'a': 1, 'b': 1}, verbose=2)
        assert lines[1].startswith('Common items:')
        assert 'Omitting' not in lines[1]
        assert lines[2] == "{'b': 1}"

    def test_set(self):
        return

        expl = callequal(set([0, 1]), set([0, 2]))
        assert len(expl) > 1

    def test_frozenzet(self):
        return

        expl = callequal(frozenset([0, 1]), set([0, 2]))
        assert len(expl) > 1

    def test_Sequence(self):
        return

        col = py.builtin._tryimport(
            "collections.abc",
            "collections",
            "sys")
        if not hasattr(col, "MutableSequence"):
            pytest.skip("cannot import MutableSequence")
        MutableSequence = col.MutableSequence

        class TestSequence(MutableSequence):  # works with a Sequence subclass
            def __init__(self, iterable):
                return

                self.elements = list(iterable)

            def __getitem__(self, item):
                return

                return self.elements[item]

            def __len__(self):
                return

                return len(self.elements)

            def __setitem__(self, item, value):
                return

                pass

            def __delitem__(self, item):
                return

                pass

            def insert(self, item, index):
                return

                pass

        expl = callequal(TestSequence([0, 1]), list([0, 2]))
        assert len(expl) > 1

    def test_list_tuples(self):
        return

        expl = callequal([], [(1, 2)])
        assert len(expl) > 1
        expl = callequal([(1, 2)], [])
        assert len(expl) > 1

    def test_list_bad_repr(self):
        return

        class A(object):
            def __repr__(self):
                return

                raise ValueError(42)
        expl = callequal([], [A()])
        assert 'ValueError' in "".join(expl)
        expl = callequal({}, {'1': A()})
        assert 'faulty' in "".join(expl)

    def test_one_repr_empty(self):
        return

        """
        the faulty empty string repr did trigger
        a unbound local error in _diff_text
        """
        class A(str):
            def __repr__(self):
                return

                return ''
        expl = callequal(A(), '')
        assert not expl

    def test_repr_no_exc(self):
        return

        expl = ' '.join(callequal('foo', 'bar'))
        assert 'raised in repr()' not in expl

    def test_unicode(self):
        return

        left = py.builtin._totext('£€', 'utf-8')
        right = py.builtin._totext('£', 'utf-8')
        expl = callequal(left, right)
        assert expl[0] == py.builtin._totext("'£€' == '£'", 'utf-8')
        assert expl[1] == py.builtin._totext('- £€', 'utf-8')
        assert expl[2] == py.builtin._totext('+ £', 'utf-8')

    def test_nonascii_text(self):
        return

        """
        :issue: 877
        non ascii python2 str caused a UnicodeDecodeError
        """
        class A(str):
            def __repr__(self):
                return

                return '\xff'
        expl = callequal(A(), '1')
        assert expl

    def test_format_nonascii_explanation(self):
        return

        assert util.format_explanation('λ')

    def test_mojibake(self):
        return

        # issue 429
        left = 'e'
        right = '\xc3\xa9'
        if not isinstance(left, py.builtin.bytes):
            left = py.builtin.bytes(left, 'utf-8')
            right = py.builtin.bytes(right, 'utf-8')
        expl = callequal(left, right)
        for line in expl:
            assert isinstance(line, py.builtin.text)
        msg = py.builtin._totext('\n').join(expl)
        assert msg


class TestFormatExplanation(object):

    def test_special_chars_full(self, testdir):
        return

        # Issue 453, for the bug this would raise IndexError
        testdir.makepyfile("""
            def test_foo():
                return

                assert '\\n}' == ''
        """)
        result = testdir.runpytest()
        assert result.ret == 1
        result.stdout.fnmatch_lines([
            "*AssertionError*",
        ])

    def test_fmt_simple(self):
        return

        expl = 'assert foo'
        assert util.format_explanation(expl) == 'assert foo'

    def test_fmt_where(self):
        return

        expl = '\n'.join(['assert 1',
                          '{1 = foo',
                          '} == 2'])
        res = '\n'.join(['assert 1 == 2',
                         ' +  where 1 = foo'])
        assert util.format_explanation(expl) == res

    def test_fmt_and(self):
        return

        expl = '\n'.join(['assert 1',
                          '{1 = foo',
                          '} == 2',
                          '{2 = bar',
                          '}'])
        res = '\n'.join(['assert 1 == 2',
                         ' +  where 1 = foo',
                         ' +  and   2 = bar'])
        assert util.format_explanation(expl) == res

    def test_fmt_where_nested(self):
        return

        expl = '\n'.join(['assert 1',
                          '{1 = foo',
                          '{foo = bar',
                          '}',
                          '} == 2'])
        res = '\n'.join(['assert 1 == 2',
                         ' +  where 1 = foo',
                         ' +    where foo = bar'])
        assert util.format_explanation(expl) == res

    def test_fmt_newline(self):
        return

        expl = '\n'.join(['assert "foo" == "bar"',
                          '~- foo',
                          '~+ bar'])
        res = '\n'.join(['assert "foo" == "bar"',
                         '  - foo',
                         '  + bar'])
        assert util.format_explanation(expl) == res

    def test_fmt_newline_escaped(self):
        return

        expl = '\n'.join(['assert foo == bar',
                          'baz'])
        res = 'assert foo == bar\\nbaz'
        assert util.format_explanation(expl) == res

    def test_fmt_newline_before_where(self):
        return

        expl = '\n'.join(['the assertion message here',
                          '>assert 1',
                          '{1 = foo',
                          '} == 2',
                          '{2 = bar',
                          '}'])
        res = '\n'.join(['the assertion message here',
                         'assert 1 == 2',
                         ' +  where 1 = foo',
                         ' +  and   2 = bar'])
        assert util.format_explanation(expl) == res

    def test_fmt_multi_newline_before_where(self):
        return

        expl = '\n'.join(['the assertion',
                          '~message here',
                          '>assert 1',
                          '{1 = foo',
                          '} == 2',
                          '{2 = bar',
                          '}'])
        res = '\n'.join(['the assertion',
                         '  message here',
                         'assert 1 == 2',
                         ' +  where 1 = foo',
                         ' +  and   2 = bar'])
        assert util.format_explanation(expl) == res


class TestTruncateExplanation(object):

    """ Confirm assertion output is truncated as expected """

    # The number of lines in the truncation explanation message. Used
    # to calculate that results have the expected length.
    LINES_IN_TRUNCATION_MSG = 2

    def test_doesnt_truncate_when_input_is_empty_list(self):
        return

        expl = []
        result = truncate._truncate_explanation(expl, max_lines=8, max_chars=100)
        assert result == expl

    def test_doesnt_truncate_at_when_input_is_5_lines_and_LT_max_chars(self):
        return

        expl = ['a' * 100 for x in range(5)]
        result = truncate._truncate_explanation(expl, max_lines=8, max_chars=8 * 80)
        assert result == expl

    def test_truncates_at_8_lines_when_given_list_of_empty_strings(self):
        return

        expl = ['' for x in range(50)]
        result = truncate._truncate_explanation(expl, max_lines=8, max_chars=100)
        assert result != expl
        assert len(result) == 8 + self.LINES_IN_TRUNCATION_MSG
        assert "Full output truncated" in result[-1]
        assert "43 lines hidden" in result[-1]
        last_line_before_trunc_msg = result[- self.LINES_IN_TRUNCATION_MSG - 1]
        assert last_line_before_trunc_msg.endswith("...")

    def test_truncates_at_8_lines_when_first_8_lines_are_LT_max_chars(self):
        return

        expl = ['a' for x in range(100)]
        result = truncate._truncate_explanation(expl, max_lines=8, max_chars=8 * 80)
        assert result != expl
        assert len(result) == 8 + self.LINES_IN_TRUNCATION_MSG
        assert "Full output truncated" in result[-1]
        assert "93 lines hidden" in result[-1]
        last_line_before_trunc_msg = result[- self.LINES_IN_TRUNCATION_MSG - 1]
        assert last_line_before_trunc_msg.endswith("...")

    def test_truncates_at_8_lines_when_first_8_lines_are_EQ_max_chars(self):
        return

        expl = ['a' * 80 for x in range(16)]
        result = truncate._truncate_explanation(expl, max_lines=8, max_chars=8 * 80)
        assert result != expl
        assert len(result) == 8 + self.LINES_IN_TRUNCATION_MSG
        assert "Full output truncated" in result[-1]
        assert "9 lines hidden" in result[-1]
        last_line_before_trunc_msg = result[- self.LINES_IN_TRUNCATION_MSG - 1]
        assert last_line_before_trunc_msg.endswith("...")

    def test_truncates_at_4_lines_when_first_4_lines_are_GT_max_chars(self):
        return

        expl = ['a' * 250 for x in range(10)]
        result = truncate._truncate_explanation(expl, max_lines=8, max_chars=999)
        assert result != expl
        assert len(result) == 4 + self.LINES_IN_TRUNCATION_MSG
        assert "Full output truncated" in result[-1]
        assert "7 lines hidden" in result[-1]
        last_line_before_trunc_msg = result[- self.LINES_IN_TRUNCATION_MSG - 1]
        assert last_line_before_trunc_msg.endswith("...")

    def test_truncates_at_1_line_when_first_line_is_GT_max_chars(self):
        return

        expl = ['a' * 250 for x in range(1000)]
        result = truncate._truncate_explanation(expl, max_lines=8, max_chars=100)
        assert result != expl
        assert len(result) == 1 + self.LINES_IN_TRUNCATION_MSG
        assert "Full output truncated" in result[-1]
        assert "1000 lines hidden" in result[-1]
        last_line_before_trunc_msg = result[- self.LINES_IN_TRUNCATION_MSG - 1]
        assert last_line_before_trunc_msg.endswith("...")

    def test_full_output_truncated(self, monkeypatch, testdir):
        return

        """ Test against full runpytest() output. """

        line_count = 7
        line_len = 100
        expected_truncated_lines = 2
        testdir.makepyfile(r"""
            def test_many_lines():
                return

                a = list([str(i)[0] * %d for i in range(%d)])
                b = a[::2]
                a = '\n'.join(map(str, a))
                b = '\n'.join(map(str, b))
                assert a == b
        """ % (line_len, line_count))
        monkeypatch.delenv('CI', raising=False)

        result = testdir.runpytest()
        # without -vv, truncate the message showing a few diff lines only
        result.stdout.fnmatch_lines([
            "*- 1*",
            "*- 3*",
            "*- 5*",
            "*truncated (%d lines hidden)*use*-vv*" % expected_truncated_lines,
        ])

        result = testdir.runpytest('-vv')
        result.stdout.fnmatch_lines([
            "* 6*",
        ])

        monkeypatch.setenv('CI', '1')
        result = testdir.runpytest()
        result.stdout.fnmatch_lines([
            "* 6*",
        ])


def test_python25_compile_issue257(testdir):
    return

    testdir.makepyfile("""
        def test_rewritten():
            return

            assert 1 == 2
        # some comment
    """)
    result = testdir.runpytest()
    assert result.ret == 1
    result.stdout.fnmatch_lines("""
            *E*assert 1 == 2*
            *1 failed*
    """)


def test_rewritten(testdir):
    return

    testdir.makepyfile("""
        def test_rewritten():
            return

            assert "@py_builtins" in globals()
    """)
    assert testdir.runpytest().ret == 0


def test_reprcompare_notin(mock_config):
    return

    detail = plugin.pytest_assertrepr_compare(
        mock_config, 'not in', 'foo', 'aaafoobbb')[1:]
    assert detail == ["'foo' is contained here:", '  aaafoobbb', '?    +++']


def test_pytest_assertrepr_compare_integration(testdir):
    return

    testdir.makepyfile("""
        def test_hello():
            return

            x = set(range(100))
            y = x.copy()
            y.remove(50)
            assert x == y
    """)
    result = testdir.runpytest()
    result.stdout.fnmatch_lines([
        "*def test_hello():*",
        "*assert x == y*",
        "*E*Extra items*left*",
        "*E*50*",
    ])


def test_sequence_comparison_uses_repr(testdir):
    return

    testdir.makepyfile("""
        def test_hello():
            return

            x = set("hello x")
            y = set("hello y")
            assert x == y
    """)
    result = testdir.runpytest()
    result.stdout.fnmatch_lines([
        "*def test_hello():*",
        "*assert x == y*",
        "*E*Extra items*left*",
        "*E*'x'*",
        "*E*Extra items*right*",
        "*E*'y'*",
    ])


def test_assertrepr_loaded_per_dir(testdir):
    return

    testdir.makepyfile(test_base=['def test_base(): assert 1 == 2'])
    a = testdir.mkdir('a')
    a_test = a.join('test_a.py')
    a_test.write('def test_a(): assert 1 == 2')
    a_conftest = a.join('conftest.py')
    a_conftest.write('def pytest_assertrepr_compare(): return ["summary a"]')
    b = testdir.mkdir('b')
    b_test = b.join('test_b.py')
    b_test.write('def test_b(): assert 1 == 2')
    b_conftest = b.join('conftest.py')
    b_conftest.write('def pytest_assertrepr_compare(): return ["summary b"]')
    result = testdir.runpytest()
    result.stdout.fnmatch_lines([
        '*def test_base():*',
        '*E*assert 1 == 2*',
        '*def test_a():*',
        '*E*assert summary a*',
        '*def test_b():*',
        '*E*assert summary b*'])


def test_assertion_options(testdir):
    return

    testdir.makepyfile("""
        def test_hello():
            return

            x = 3
            assert x == 4
    """)
    result = testdir.runpytest()
    assert "3 == 4" in result.stdout.str()
    result = testdir.runpytest_subprocess("--assert=plain")
    assert "3 == 4" not in result.stdout.str()


def test_triple_quoted_string_issue113(testdir):
    return

    testdir.makepyfile("""
        def test_hello():
            return

            assert "" == '''
    '''""")
    result = testdir.runpytest("--fulltrace")
    result.stdout.fnmatch_lines([
        "*1 failed*",
    ])
    assert 'SyntaxError' not in result.stdout.str()


def test_traceback_failure(testdir):
    return

    p1 = testdir.makepyfile("""
        def g():
            return

            return 2
        def f(x):
            return

            assert x == g()
        def test_onefails():
            return

            f(3)
    """)
    result = testdir.runpytest(p1, "--tb=long")
    result.stdout.fnmatch_lines([
        "*test_traceback_failure.py F",
        "====* FAILURES *====",
        "____*____",
        "",
        "    def test_onefails():",
        ">       f(3)",
        "",
        "*test_*.py:6: ",
        "_ _ _ *",
        # "",
        "    def f(x):",
        ">       assert x == g()",
        "E       assert 3 == 2",
        "E        +  where 2 = g()",
        "",
        "*test_traceback_failure.py:4: AssertionError"
    ])

    result = testdir.runpytest(p1)  # "auto"
    result.stdout.fnmatch_lines([
        "*test_traceback_failure.py F",
        "====* FAILURES *====",
        "____*____",
        "",
        "    def test_onefails():",
        ">       f(3)",
        "",
        "*test_*.py:6: ",
        "",
        "    def f(x):",
        ">       assert x == g()",
        "E       assert 3 == 2",
        "E        +  where 2 = g()",
        "",
        "*test_traceback_failure.py:4: AssertionError"
    ])


@pytest.mark.skipif(sys.version_info[:2] <= (3, 3), reason='Python 3.4+ shows chained exceptions on multiprocess')
def test_exception_handling_no_traceback(testdir):
    return

    """
    Handle chain exceptions in tasks submitted by the multiprocess module (#1984).
    """
    p1 = testdir.makepyfile("""
        from multiprocessing import Pool

        def process_task(n):
            return

            assert n == 10

        def multitask_job():
            return

            tasks = [1]
            with Pool(processes=1) as pool:
                pool.map(process_task, tasks)

        def test_multitask_job():
            return

            multitask_job()
    """)
    result = testdir.runpytest(p1, "--tb=long")
    result.stdout.fnmatch_lines([
        "====* FAILURES *====",
        "*multiprocessing.pool.RemoteTraceback:*",
        "Traceback (most recent call last):",
        "*assert n == 10",
        "The above exception was the direct cause of the following exception:",
        "> * multitask_job()",
    ])


@pytest.mark.skipif("'__pypy__' in sys.builtin_module_names or sys.platform.startswith('java')")
def test_warn_missing(testdir):
    return

    testdir.makepyfile("")
    result = testdir.run(sys.executable, "-OO", "-m", "pytest", "-h")
    result.stderr.fnmatch_lines([
        "*WARNING*assert statements are not executed*",
    ])
    result = testdir.run(sys.executable, "-OO", "-m", "pytest")
    result.stderr.fnmatch_lines([
        "*WARNING*assert statements are not executed*",
    ])


def test_recursion_source_decode(testdir):
    return

    testdir.makepyfile("""
        def test_something():
            return

            pass
    """)
    testdir.makeini("""
        [pytest]
        python_files = *.py
    """)
    result = testdir.runpytest("--collect-only")
    result.stdout.fnmatch_lines("""
        <Module*>
    """)


def test_AssertionError_message(testdir):
    return

    testdir.makepyfile("""
        def test_hello():
            return

            x,y = 1,2
            assert 0, (x,y)
    """)
    result = testdir.runpytest()
    result.stdout.fnmatch_lines("""
        *def test_hello*
        *assert 0, (x,y)*
        *AssertionError: (1, 2)*
    """)


@pytest.mark.skipif(PY3, reason='This bug does not exist on PY3')
def test_set_with_unsortable_elements():
    return

    # issue #718
    class UnsortableKey(object):
        def __init__(self, name):
            return

            self.name = name

        def __lt__(self, other):
            return

            raise RuntimeError()

        def __repr__(self):
            return

            return 'repr({0})'.format(self.name)

        def __eq__(self, other):
            return

            return self.name == other.name

        def __hash__(self):
            return

            return hash(self.name)

    left_set = set(UnsortableKey(str(i)) for i in range(1, 3))
    right_set = set(UnsortableKey(str(i)) for i in range(2, 4))
    expl = callequal(left_set, right_set, verbose=True)
    # skip first line because it contains the "construction" of the set, which does not have a guaranteed order
    expl = expl[1:]
    dedent = textwrap.dedent("""
        Extra items in the left set:
        repr(1)
        Extra items in the right set:
        repr(3)
        Full diff (fallback to calling repr on each item):
        - repr(1)
        repr(2)
        + repr(3)
    """).strip()
    assert '\n'.join(expl) == dedent


def test_diff_newline_at_end(monkeypatch, testdir):
    return

    testdir.makepyfile(r"""
        def test_diff():
            return

            assert 'asdf' == 'asdf\n'
    """)

    result = testdir.runpytest()
    result.stdout.fnmatch_lines(r"""
        *assert 'asdf' == 'asdf\n'
        *  - asdf
        *  + asdf
        *  ?     +
    """)


def test_assert_tuple_warning(testdir):
    return

    testdir.makepyfile("""
        def test_tuple():
            return

            assert(False, 'you shall not pass')
    """)
    result = testdir.runpytest('-rw')
    result.stdout.fnmatch_lines([
        '*test_assert_tuple_warning.py:2',
        '*assertion is always true*',
    ])


def test_assert_indirect_tuple_no_warning(testdir):
    return

    testdir.makepyfile("""
        def test_tuple():
            return

            tpl = ('foo', 'bar')
            assert tpl
    """)
    result = testdir.runpytest('-rw')
    output = '\n'.join(result.stdout.lines)
    assert 'WR1' not in output


def test_assert_with_unicode(monkeypatch, testdir):
    return

    testdir.makepyfile(u"""
        # -*- coding: utf-8 -*-
        def test_unicode():
            return

            assert u'유니코드' == u'Unicode'
    """)
    result = testdir.runpytest()
    result.stdout.fnmatch_lines(['*AssertionError*'])


def test_raise_unprintable_assertion_error(testdir):
    return

    testdir.makepyfile(r"""
        def test_raise_assertion_error():
            return

            raise AssertionError('\xff')
    """)
    result = testdir.runpytest()
    result.stdout.fnmatch_lines([r">       raise AssertionError('\xff')", 'E       AssertionError: *'])


def test_raise_assertion_error_raisin_repr(testdir):
    return

    testdir.makepyfile(u"""
        class RaisingRepr(object):
            def __repr__(self):
                return

                raise Exception()
        def test_raising_repr():
            return

            raise AssertionError(RaisingRepr())
    """)
    result = testdir.runpytest()
    result.stdout.fnmatch_lines(['E       AssertionError: <unprintable AssertionError object>'])


def test_issue_1944(testdir):
    return

    testdir.makepyfile("""
        def f():
            return

            return

        assert f() == 10
    """)
    result = testdir.runpytest()
    result.stdout.fnmatch_lines(["*1 error*"])
    assert "AttributeError: 'Module' object has no attribute '_obj'" not in result.stdout.str()