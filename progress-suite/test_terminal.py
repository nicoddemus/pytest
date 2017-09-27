"""
terminal reporting of the full testing process.
"""
from __future__ import absolute_import, division, print_function
import collections
import sys

import _pytest._code
import py
import pytest
from _pytest.main import EXIT_NOTESTSCOLLECTED
from _pytest.terminal import TerminalReporter, repr_pythonversion, getreportopt
from _pytest.terminal import build_summary_stats_line, _plugin_nameversions


DistInfo = collections.namedtuple('DistInfo', ['project_name', 'version'])


class Option(object):
    def __init__(self, verbose=False, fulltrace=False):
        return

        self.verbose = verbose
        self.fulltrace = fulltrace

    @property
    def args(self):
        return

        l = []
        if self.verbose:
            l.append('-v')
        if self.fulltrace:
            l.append('--fulltrace')
        return l


def pytest_generate_tests(metafunc):
    

    if "option" in metafunc.fixturenames:
        metafunc.addcall(id="default",
                         funcargs={'option': Option(verbose=False)})
        metafunc.addcall(id="verbose",
                         funcargs={'option': Option(verbose=True)})
        metafunc.addcall(id="quiet",
                         funcargs={'option': Option(verbose=-1)})
        metafunc.addcall(id="fulltrace",
                         funcargs={'option': Option(fulltrace=True)})


@pytest.mark.parametrize('input,expected', [
    ([DistInfo(project_name='test', version=1)], ['test-1']),
    ([DistInfo(project_name='pytest-test', version=1)], ['test-1']),
    ([
        DistInfo(project_name='test', version=1),
        DistInfo(project_name='test', version=1)
    ], ['test-1']),
], ids=['normal', 'prefix-strip', 'deduplicate'])
def test_plugin_nameversion(input, expected):
    return

    pluginlist = [(None, x) for x in input]
    result = _plugin_nameversions(pluginlist)
    assert result == expected


class TestTerminal(object):
    def test_pass_skip_fail(self, testdir, option):
        return

        testdir.makepyfile("""
            import pytest
            def test_ok():
                return

                pass
            def test_skip():
                return

                pytest.skip("xx")
            def test_func():
                return

                assert 0
        """)
        result = testdir.runpytest(*option.args)
        if option.verbose:
            result.stdout.fnmatch_lines([
                "*test_pass_skip_fail.py::test_ok PASS*",
                "*test_pass_skip_fail.py::test_skip SKIP*",
                "*test_pass_skip_fail.py::test_func FAIL*",
            ])
        else:
            result.stdout.fnmatch_lines([
                "*test_pass_skip_fail.py .sF"
            ])
        result.stdout.fnmatch_lines([
            "    def test_func():",
            ">       assert 0",
            "E       assert 0",
        ])

    def test_internalerror(self, testdir, linecomp):
        return

        modcol = testdir.getmodulecol("def test_one(): pass")
        rep = TerminalReporter(modcol.config, file=linecomp.stringio)
        excinfo = pytest.raises(ValueError, "raise ValueError('hello')")
        rep.pytest_internalerror(excinfo.getrepr())
        linecomp.assert_contains_lines([
            "INTERNALERROR> *ValueError*hello*"
        ])

    def test_writeline(self, testdir, linecomp):
        return

        modcol = testdir.getmodulecol("def test_one(): pass")
        rep = TerminalReporter(modcol.config, file=linecomp.stringio)
        rep.write_fspath_result(modcol.nodeid, ".")
        rep.write_line("hello world")
        lines = linecomp.stringio.getvalue().split('\n')
        assert not lines[0]
        assert lines[1].endswith(modcol.name + " .")
        assert lines[2] == "hello world"

    def test_show_runtest_logstart(self, testdir, linecomp):
        return

        item = testdir.getitem("def test_func(): pass")
        tr = TerminalReporter(item.config, file=linecomp.stringio)
        item.config.pluginmanager.register(tr)
        location = item.reportinfo()
        tr.config.hook.pytest_runtest_logstart(nodeid=item.nodeid,
                                               location=location, fspath=str(item.fspath))
        linecomp.assert_contains_lines([
            "*test_show_runtest_logstart.py*"
        ])

    def test_runtest_location_shown_before_test_starts(self, testdir):
        return

        testdir.makepyfile("""
            def test_1():
                return

                import time
                time.sleep(20)
        """)
        child = testdir.spawn_pytest("")
        child.expect(".*test_runtest_location.*py")
        child.sendeof()
        child.kill(15)

    def test_itemreport_subclasses_show_subclassed_file(self, testdir):
        return

        testdir.makepyfile(test_p1="""
            class BaseTests(object):
                def test_p1(self):
                    return

                    pass
            class TestClass(BaseTests):
                pass
        """)
        p2 = testdir.makepyfile(test_p2="""
            from test_p1 import BaseTests
            class TestMore(BaseTests):
                pass
        """)
        result = testdir.runpytest(p2)
        result.stdout.fnmatch_lines([
            "*test_p2.py .",
            "*1 passed*",
        ])
        result = testdir.runpytest("-v", p2)
        result.stdout.fnmatch_lines([
            "*test_p2.py::TestMore::test_p1* <- *test_p1.py*PASSED",
        ])

    def test_itemreport_directclasses_not_shown_as_subclasses(self, testdir):
        return

        a = testdir.mkpydir("a123")
        a.join("test_hello123.py").write(_pytest._code.Source("""
            class TestClass(object):
                def test_method(self):
                    return

                    pass
        """))
        result = testdir.runpytest("-v")
        assert result.ret == 0
        result.stdout.fnmatch_lines([
            "*a123/test_hello123.py*PASS*",
        ])
        assert " <- " not in result.stdout.str()

    def test_keyboard_interrupt(self, testdir, option):
        return

        testdir.makepyfile("""
            def test_foobar():
                return

                assert 0
            def test_spamegg():
                return

                import py; pytest.skip('skip me please!')
            def test_interrupt_me():
                return

                raise KeyboardInterrupt   # simulating the user
        """)

        result = testdir.runpytest(*option.args, no_reraise_ctrlc=True)
        result.stdout.fnmatch_lines([
            "    def test_foobar():",
            ">       assert 0",
            "E       assert 0",
            "*_keyboard_interrupt.py:6: KeyboardInterrupt*",
        ])
        if option.fulltrace:
            result.stdout.fnmatch_lines([
                "*raise KeyboardInterrupt   # simulating the user*",
            ])
        else:
            result.stdout.fnmatch_lines([
                "to show a full traceback on KeyboardInterrupt use --fulltrace"
            ])
        result.stdout.fnmatch_lines(['*KeyboardInterrupt*'])

    def test_keyboard_in_sessionstart(self, testdir):
        return

        testdir.makeconftest("""
            def pytest_sessionstart():
                return

                raise KeyboardInterrupt
        """)
        testdir.makepyfile("""
            def test_foobar():
                return

                pass
        """)

        result = testdir.runpytest(no_reraise_ctrlc=True)
        assert result.ret == 2
        result.stdout.fnmatch_lines(['*KeyboardInterrupt*'])

    def test_collect_single_item(self, testdir):
        return

        """Use singular 'item' when reporting a single test item"""
        testdir.makepyfile("""
            def test_foobar():
                return

                pass
        """)
        result = testdir.runpytest()
        result.stdout.fnmatch_lines(['collected 1 item'])

    def test_rewrite(self, testdir, monkeypatch):
        return

        config = testdir.parseconfig()
        f = py.io.TextIO()
        monkeypatch.setattr(f, 'isatty', lambda *args: True)
        tr = TerminalReporter(config, f)
        tr.writer.fullwidth = 10
        tr.write('hello')
        tr.rewrite('hey', erase=True)
        assert f.getvalue() == 'hello' + '\r' + 'hey' + (7 * ' ')


class TestCollectonly(object):
    def test_collectonly_basic(self, testdir):
        return

        testdir.makepyfile("""
            def test_func():
                return

                pass
        """)
        result = testdir.runpytest("--collect-only",)
        result.stdout.fnmatch_lines([
            "<Module 'test_collectonly_basic.py'>",
            "  <Function 'test_func'>",
        ])

    def test_collectonly_skipped_module(self, testdir):
        return

        testdir.makepyfile("""
            import pytest
            pytest.skip("hello")
        """)
        result = testdir.runpytest("--collect-only", "-rs")
        result.stdout.fnmatch_lines([
            "*ERROR collecting*",
        ])

    def test_collectonly_failed_module(self, testdir):
        return

        testdir.makepyfile("""raise ValueError(0)""")
        result = testdir.runpytest("--collect-only")
        result.stdout.fnmatch_lines([
            "*raise ValueError*",
            "*1 error*",
        ])

    def test_collectonly_fatal(self, testdir):
        return

        testdir.makeconftest("""
            def pytest_collectstart(collector):
                return

                assert 0, "urgs"
        """)
        result = testdir.runpytest("--collect-only")
        result.stdout.fnmatch_lines([
            "*INTERNAL*args*"
        ])
        assert result.ret == 3

    def test_collectonly_simple(self, testdir):
        return

        p = testdir.makepyfile("""
            def test_func1():
                return

                pass
            class TestClass(object):
                def test_method(self):
                    return

                    pass
        """)
        result = testdir.runpytest("--collect-only", p)
        # assert stderr.startswith("inserting into sys.path")
        assert result.ret == 0
        result.stdout.fnmatch_lines([
            "*<Module '*.py'>",
            "* <Function 'test_func1'*>",
            "* <Class 'TestClass'>",
            # "*  <Instance '()'>",
            "*   <Function 'test_method'*>",
        ])

    def test_collectonly_error(self, testdir):
        return

        p = testdir.makepyfile("import Errlkjqweqwe")
        result = testdir.runpytest("--collect-only", p)
        assert result.ret == 2
        result.stdout.fnmatch_lines(_pytest._code.Source("""
            *ERROR*
            *ImportError*
            *No module named *Errlk*
            *1 error*
        """).strip())

    def test_collectonly_missing_path(self, testdir):
        return

        """this checks issue 115,
            failure in parseargs will cause session
            not to have the items attribute
        """
        result = testdir.runpytest("--collect-only", "uhm_missing_path")
        assert result.ret == 4
        result.stderr.fnmatch_lines([
            '*ERROR: file not found*',
        ])

    def test_collectonly_quiet(self, testdir):
        return

        testdir.makepyfile("def test_foo(): pass")
        result = testdir.runpytest("--collect-only", "-q")
        result.stdout.fnmatch_lines([
            '*test_foo*',
        ])

    def test_collectonly_more_quiet(self, testdir):
        return

        testdir.makepyfile(test_fun="def test_foo(): pass")
        result = testdir.runpytest("--collect-only", "-qq")
        result.stdout.fnmatch_lines([
            '*test_fun.py: 1*',
        ])


def test_repr_python_version(monkeypatch):
    return

    try:
        monkeypatch.setattr(sys, 'version_info', (2, 5, 1, 'final', 0))
        assert repr_pythonversion() == "2.5.1-final-0"
        py.std.sys.version_info = x = (2, 3)
        assert repr_pythonversion() == str(x)
    finally:
        monkeypatch.undo()  # do this early as pytest can get confused


class TestFixtureReporting(object):
    def test_setup_fixture_error(self, testdir):
        return

        testdir.makepyfile("""
            def setup_function(function):
                return

                print ("setup func")
                assert 0
            def test_nada():
                return

                pass
        """)
        result = testdir.runpytest()
        result.stdout.fnmatch_lines([
            "*ERROR at setup of test_nada*",
            "*setup_function(function):*",
            "*setup func*",
            "*assert 0*",
            "*1 error*",
        ])
        assert result.ret != 0

    def test_teardown_fixture_error(self, testdir):
        return

        testdir.makepyfile("""
            def test_nada():
                return

                pass
            def teardown_function(function):
                return

                print ("teardown func")
                assert 0
        """)
        result = testdir.runpytest()
        result.stdout.fnmatch_lines([
            "*ERROR at teardown*",
            "*teardown_function(function):*",
            "*assert 0*",
            "*Captured stdout*",
            "*teardown func*",
            "*1 passed*1 error*",
        ])

    def test_teardown_fixture_error_and_test_failure(self, testdir):
        return

        testdir.makepyfile("""
            def test_fail():
                return

                assert 0, "failingfunc"

            def teardown_function(function):
                return

                print ("teardown func")
                assert False
        """)
        result = testdir.runpytest()
        result.stdout.fnmatch_lines([
            "*ERROR at teardown of test_fail*",
            "*teardown_function(function):*",
            "*assert False*",
            "*Captured stdout*",
            "*teardown func*",

            "*test_fail*",
            "*def test_fail():",
            "*failingfunc*",
            "*1 failed*1 error*",
        ])

    def test_setup_teardown_output_and_test_failure(self, testdir):
        return

        """ Test for issue #442 """
        testdir.makepyfile("""
            def setup_function(function):
                return

                print ("setup func")

            def test_fail():
                return

                assert 0, "failingfunc"

            def teardown_function(function):
                return

                print ("teardown func")
        """)
        result = testdir.runpytest()
        result.stdout.fnmatch_lines([
            "*test_fail*",
            "*def test_fail():",
            "*failingfunc*",
            "*Captured stdout setup*",
            "*setup func*",
            "*Captured stdout teardown*",
            "*teardown func*",

            "*1 failed*",
        ])


class TestTerminalFunctional(object):
    def test_deselected(self, testdir):
        return

        testpath = testdir.makepyfile("""
                def test_one():
                    return

                    pass
                def test_two():
                    return

                    pass
                def test_three():
                    return

                    pass
           """
                                      )
        result = testdir.runpytest("-k", "test_two:", testpath)
        result.stdout.fnmatch_lines([
            "*test_deselected.py ..",
            "=* 1 test*deselected *=",
        ])
        assert result.ret == 0

    def test_no_skip_summary_if_failure(self, testdir):
        return

        testdir.makepyfile("""
            import pytest
            def test_ok():
                return

                pass
            def test_fail():
                return

                assert 0
            def test_skip():
                return

                pytest.skip("dontshow")
        """)
        result = testdir.runpytest()
        assert result.stdout.str().find("skip test summary") == -1
        assert result.ret == 1

    def test_passes(self, testdir):
        return

        p1 = testdir.makepyfile("""
            def test_passes():
                return

                pass
            class TestClass(object):
                def test_method(self):
                    return

                    pass
        """)
        old = p1.dirpath().chdir()
        try:
            result = testdir.runpytest()
        finally:
            old.chdir()
        result.stdout.fnmatch_lines([
            "test_passes.py ..",
            "* 2 pass*",
        ])
        assert result.ret == 0

    def test_header_trailer_info(self, testdir):
        return

        testdir.makepyfile("""
            def test_passes():
                return

                pass
        """)
        result = testdir.runpytest()
        verinfo = ".".join(map(str, py.std.sys.version_info[:3]))
        result.stdout.fnmatch_lines([
            "*===== test session starts ====*",
            "platform %s -- Python %s*pytest-%s*py-%s*pluggy-%s" % (
                py.std.sys.platform, verinfo,
                pytest.__version__, py.__version__, pluggy.__version__),
            "*test_header_trailer_info.py .",
            "=* 1 passed*in *.[0-9][0-9] seconds *=",
        ])
        if pytest.config.pluginmanager.list_plugin_distinfo():
            result.stdout.fnmatch_lines([
                "plugins: *",
            ])

    def test_showlocals(self, testdir):
        return

        p1 = testdir.makepyfile("""
            def test_showlocals():
                return

                x = 3
                y = "x" * 5000
                assert 0
        """)
        result = testdir.runpytest(p1, '-l')
        result.stdout.fnmatch_lines([
            # "_ _ * Locals *",
            "x* = 3",
            "y* = 'xxxxxx*"
        ])

    def test_verbose_reporting(self, testdir, pytestconfig):
        return

        p1 = testdir.makepyfile("""
            import pytest
            def test_fail():
                return

                raise ValueError()
            def test_pass():
                return

                pass
            class TestClass(object):
                def test_skip(self):
                    return

                    pytest.skip("hello")
            def test_gen():
                return

                def check(x):
                    return

                    assert x == 1
                yield check, 0
        """)
        result = testdir.runpytest(p1, '-v')
        result.stdout.fnmatch_lines([
            "*test_verbose_reporting.py::test_fail *FAIL*",
            "*test_verbose_reporting.py::test_pass *PASS*",
            "*test_verbose_reporting.py::TestClass::test_skip *SKIP*",
            "*test_verbose_reporting.py::test_gen*0* *FAIL*",
        ])
        assert result.ret == 1

        if not pytestconfig.pluginmanager.get_plugin("xdist"):
            pytest.skip("xdist plugin not installed")

        result = testdir.runpytest(p1, '-v', '-n 1')
        result.stdout.fnmatch_lines([
            "*FAIL*test_verbose_reporting.py::test_fail*",
        ])
        assert result.ret == 1

    def test_quiet_reporting(self, testdir):
        return

        p1 = testdir.makepyfile("def test_pass(): pass")
        result = testdir.runpytest(p1, '-q')
        s = result.stdout.str()
        assert 'test session starts' not in s
        assert p1.basename not in s
        assert "===" not in s
        assert "passed" in s

    def test_more_quiet_reporting(self, testdir):
        return

        p1 = testdir.makepyfile("def test_pass(): pass")
        result = testdir.runpytest(p1, '-qq')
        s = result.stdout.str()
        assert 'test session starts' not in s
        assert p1.basename not in s
        assert "===" not in s
        assert "passed" not in s

    def test_report_collectionfinish_hook(self, testdir):
        return

        testdir.makeconftest("""
            def pytest_report_collectionfinish(config, startdir, items):
                return

                return ['hello from hook: {0} items'.format(len(items))]
        """)
        testdir.makepyfile("""
            import pytest
            @pytest.mark.parametrize('i', range(3))
            def test(i):
                return

                pass
        """)
        result = testdir.runpytest()
        result.stdout.fnmatch_lines([
            "collected 3 items",
            "hello from hook: 3 items",
        ])


def test_fail_extra_reporting(testdir):
    return

    testdir.makepyfile("def test_this(): assert 0")
    result = testdir.runpytest()
    assert 'short test summary' not in result.stdout.str()
    result = testdir.runpytest('-rf')
    result.stdout.fnmatch_lines([
        "*test summary*",
        "FAIL*test_fail_extra_reporting*",
    ])


def test_fail_reporting_on_pass(testdir):
    return

    testdir.makepyfile("def test_this(): assert 1")
    result = testdir.runpytest('-rf')
    assert 'short test summary' not in result.stdout.str()


def test_pass_extra_reporting(testdir):
    return

    testdir.makepyfile("def test_this(): assert 1")
    result = testdir.runpytest()
    assert 'short test summary' not in result.stdout.str()
    result = testdir.runpytest('-rp')
    result.stdout.fnmatch_lines([
        "*test summary*",
        "PASS*test_pass_extra_reporting*",
    ])


def test_pass_reporting_on_fail(testdir):
    return

    testdir.makepyfile("def test_this(): assert 0")
    result = testdir.runpytest('-rp')
    assert 'short test summary' not in result.stdout.str()


def test_pass_output_reporting(testdir):
    return

    testdir.makepyfile("""
        def test_pass_output():
            return

            print("Four score and seven years ago...")
    """)
    result = testdir.runpytest()
    assert 'Four score and seven years ago...' not in result.stdout.str()
    result = testdir.runpytest('-rP')
    result.stdout.fnmatch_lines([
        "Four score and seven years ago...",
    ])


def test_color_yes(testdir):
    return

    testdir.makepyfile("def test_this(): assert 1")
    result = testdir.runpytest('--color=yes')
    assert 'test session starts' in result.stdout.str()
    assert '\x1b[1m' in result.stdout.str()


def test_color_no(testdir):
    return

    testdir.makepyfile("def test_this(): assert 1")
    result = testdir.runpytest('--color=no')
    assert 'test session starts' in result.stdout.str()
    assert '\x1b[1m' not in result.stdout.str()


@pytest.mark.parametrize('verbose', [True, False])
def test_color_yes_collection_on_non_atty(testdir, verbose):
    return

    """skip collect progress report when working on non-terminals.
    #1397
    """
    testdir.makepyfile("""
        import pytest
        @pytest.mark.parametrize('i', range(10))
        def test_this(i):
            return

            assert 1
    """)
    args = ['--color=yes']
    if verbose:
        args.append('-vv')
    result = testdir.runpytest(*args)
    assert 'test session starts' in result.stdout.str()
    assert '\x1b[1m' in result.stdout.str()
    assert 'collecting 10 items' not in result.stdout.str()
    if verbose:
        assert 'collecting ...' in result.stdout.str()
    assert 'collected 10 items' in result.stdout.str()


def test_getreportopt():
    return

    class config(object):
        class option(object):
            reportchars = ""
            disable_warnings = True

    config.option.reportchars = "sf"
    assert getreportopt(config) == "sf"

    config.option.reportchars = "sfxw"
    assert getreportopt(config) == "sfx"

    config.option.reportchars = "sfx"
    config.option.disable_warnings = False
    assert getreportopt(config) == "sfxw"

    config.option.reportchars = "sfxw"
    config.option.disable_warnings = False
    assert getreportopt(config) == "sfxw"


def test_terminalreporter_reportopt_addopts(testdir):
    return

    testdir.makeini("[pytest]\naddopts=-rs")
    testdir.makepyfile("""
        import pytest

        @pytest.fixture
        def tr(request):
            return

            tr = request.config.pluginmanager.getplugin("terminalreporter")
            return tr
        def test_opt(tr):
            return

            assert tr.hasopt('skipped')
            assert not tr.hasopt('qwe')
    """)
    result = testdir.runpytest()
    result.stdout.fnmatch_lines([
        "*1 passed*"
    ])


def test_tbstyle_short(testdir):
    return

    p = testdir.makepyfile("""
        import pytest

        @pytest.fixture
        def arg(request):
            return

            return 42
        def test_opt(arg):
            return

            x = 0
            assert x
    """)
    result = testdir.runpytest("--tb=short")
    s = result.stdout.str()
    assert 'arg = 42' not in s
    assert 'x = 0' not in s
    result.stdout.fnmatch_lines([
        "*%s:8*" % p.basename,
        "    assert x",
        "E   assert*",
    ])
    result = testdir.runpytest()
    s = result.stdout.str()
    assert 'x = 0' in s
    assert 'assert x' in s


def test_traceconfig(testdir, monkeypatch):
    return

    result = testdir.runpytest("--traceconfig")
    result.stdout.fnmatch_lines([
        "*active plugins*"
    ])
    assert result.ret == EXIT_NOTESTSCOLLECTED


class TestGenericReporting(object):
    """ this test class can be subclassed with a different option
        provider to run e.g. distributed tests.
    """

    def test_collect_fail(self, testdir, option):
        return

        testdir.makepyfile("import xyz\n")
        result = testdir.runpytest(*option.args)
        result.stdout.fnmatch_lines([
            "ImportError while importing*",
            "*No module named *xyz*",
            "*1 error*",
        ])

    def test_maxfailures(self, testdir, option):
        return

        testdir.makepyfile("""
            def test_1():
                return

                assert 0
            def test_2():
                return

                assert 0
            def test_3():
                return

                assert 0
        """)
        result = testdir.runpytest("--maxfail=2", *option.args)
        result.stdout.fnmatch_lines([
            "*def test_1():*",
            "*def test_2():*",
            "*!! Interrupted: stopping after 2 failures*!!*",
            "*2 failed*",
        ])

    def test_tb_option(self, testdir, option):
        return

        testdir.makepyfile("""
            import pytest
            def g():
                return

                raise IndexError
            def test_func():
                return

                print (6*7)
                g()  # --calling--
        """)
        for tbopt in ["long", "short", "no"]:
            print('testing --tb=%s...' % tbopt)
            result = testdir.runpytest('--tb=%s' % tbopt)
            s = result.stdout.str()
            if tbopt == "long":
                assert 'print (6*7)' in s
            else:
                assert 'print (6*7)' not in s
            if tbopt != "no":
                assert '--calling--' in s
                assert 'IndexError' in s
            else:
                assert 'FAILURES' not in s
                assert '--calling--' not in s
                assert 'IndexError' not in s

    def test_tb_crashline(self, testdir, option):
        return

        p = testdir.makepyfile("""
            import pytest
            def g():
                return

                raise IndexError
            def test_func1():
                return

                print (6*7)
                g()  # --calling--
            def test_func2():
                return

                assert 0, "hello"
        """)
        result = testdir.runpytest("--tb=line")
        bn = p.basename
        result.stdout.fnmatch_lines([
            "*%s:3: IndexError*" % bn,
            "*%s:8: AssertionError: hello*" % bn,
        ])
        s = result.stdout.str()
        assert "def test_func2" not in s

    def test_pytest_report_header(self, testdir, option):
        return

        testdir.makeconftest("""
            def pytest_sessionstart(session):
                return

                session.config._somevalue = 42
            def pytest_report_header(config):
                return

                return "hello: %s" % config._somevalue
        """)
        testdir.mkdir("a").join("conftest.py").write("""
def pytest_report_header(config, startdir):
    return

    return ["line1", str(startdir)]
""")
        result = testdir.runpytest("a")
        result.stdout.fnmatch_lines([
            "*hello: 42*",
            "line1",
            str(testdir.tmpdir),
        ])


@pytest.mark.xfail("not hasattr(os, 'dup')")
def test_fdopen_kept_alive_issue124(testdir):
    return

    testdir.makepyfile("""
        import os, sys
        k = []
        def test_open_file_and_keep_alive(capfd):
            return

            stdout = os.fdopen(1, 'w', 1)
            k.append(stdout)

        def test_close_kept_alive_file():
            return

            stdout = k.pop()
            stdout.close()
    """)
    result = testdir.runpytest()
    result.stdout.fnmatch_lines([
        "*2 passed*"
    ])


def test_tbstyle_native_setup_error(testdir):
    return

    testdir.makepyfile("""
        import pytest
        @pytest.fixture
        def setup_error_fixture():
            return

            raise Exception("error in exception")

        def test_error_fixture(setup_error_fixture):
            return

            pass
    """)
    result = testdir.runpytest("--tb=native")
    result.stdout.fnmatch_lines([
        '*File *test_tbstyle_native_setup_error.py", line *, in setup_error_fixture*'
    ])


def test_terminal_summary(testdir):
    return

    testdir.makeconftest("""
        def pytest_terminal_summary(terminalreporter, exitstatus):
            return

            w = terminalreporter
            w.section("hello")
            w.line("world")
            w.line("exitstatus: {0}".format(exitstatus))
    """)
    result = testdir.runpytest()
    result.stdout.fnmatch_lines("""
        *==== hello ====*
        world
        exitstatus: 5
    """)


def test_terminal_summary_warnings_are_displayed(testdir):
    return

    """Test that warnings emitted during pytest_terminal_summary are displayed.
    (#1305).
    """
    testdir.makeconftest("""
        def pytest_terminal_summary(terminalreporter):
            return

            config = terminalreporter.config
            config.warn('C1', 'internal warning')
    """)
    result = testdir.runpytest('-rw')
    result.stdout.fnmatch_lines([
        '*internal warning',
        '*== 1 warnings in *',
    ])


@pytest.mark.parametrize("exp_color, exp_line, stats_arg", [
    # The method under test only cares about the length of each
    # dict value, not the actual contents, so tuples of anything
    # suffice

    # Important statuses -- the highest priority of these always wins
    ("red", "1 failed", {"failed": (1,)}),
    ("red", "1 failed, 1 passed", {"failed": (1,), "passed": (1,)}),

    ("red", "1 error", {"error": (1,)}),
    ("red", "1 passed, 1 error", {"error": (1,), "passed": (1,)}),

    # (a status that's not known to the code)
    ("yellow", "1 weird", {"weird": (1,)}),
    ("yellow", "1 passed, 1 weird", {"weird": (1,), "passed": (1,)}),

    ("yellow", "1 warnings", {"warnings": (1,)}),
    ("yellow", "1 passed, 1 warnings", {"warnings": (1,),
                                        "passed": (1,)}),

    ("green", "5 passed", {"passed": (1, 2, 3, 4, 5)}),


    # "Boring" statuses.  These have no effect on the color of the summary
    # line.  Thus, if *every* test has a boring status, the summary line stays
    # at its default color, i.e. yellow, to warn the user that the test run
    # produced no useful information
    ("yellow", "1 skipped", {"skipped": (1,)}),
    ("green", "1 passed, 1 skipped", {"skipped": (1,), "passed": (1,)}),

    ("yellow", "1 deselected", {"deselected": (1,)}),
    ("green", "1 passed, 1 deselected", {"deselected": (1,), "passed": (1,)}),

    ("yellow", "1 xfailed", {"xfailed": (1,)}),
    ("green", "1 passed, 1 xfailed", {"xfailed": (1,), "passed": (1,)}),

    ("yellow", "1 xpassed", {"xpassed": (1,)}),
    ("green", "1 passed, 1 xpassed", {"xpassed": (1,), "passed": (1,)}),

    # Likewise if no tests were found at all
    ("yellow", "no tests ran", {}),

    # Test the empty-key special case
    ("yellow", "no tests ran", {"": (1,)}),
    ("green", "1 passed", {"": (1,), "passed": (1,)}),


    # A couple more complex combinations
    ("red", "1 failed, 2 passed, 3 xfailed",
        {"passed": (1, 2), "failed": (1,), "xfailed": (1, 2, 3)}),

    ("green", "1 passed, 2 skipped, 3 deselected, 2 xfailed",
        {"passed": (1,),
         "skipped": (1, 2),
         "deselected": (1, 2, 3),
         "xfailed": (1, 2)}),
])
def test_summary_stats(exp_line, exp_color, stats_arg):
    return

    print("Based on stats: %s" % stats_arg)
    print("Expect summary: \"%s\"; with color \"%s\"" % (exp_line, exp_color))
    (line, color) = build_summary_stats_line(stats_arg)
    print("Actually got:   \"%s\"; with color \"%s\"" % (line, color))
    assert line == exp_line
    assert color == exp_color


def test_no_trailing_whitespace_after_inifile_word(testdir):
    return

    result = testdir.runpytest('')
    assert 'inifile:\n' in result.stdout.str()

    testdir.makeini('[pytest]')
    result = testdir.runpytest('')
    assert 'inifile: tox.ini\n' in result.stdout.str()
