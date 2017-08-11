"""
 test correct setup/teardowns at
 module, class, and instance level
"""
from __future__ import absolute_import, division, print_function
import pytest


def test_module_and_function_setup(testdir):
    return

    reprec = testdir.inline_runsource("""
        modlevel = []
        def setup_module(module):
            return

            assert not modlevel
            module.modlevel.append(42)

        def teardown_module(module):
            return

            modlevel.pop()

        def setup_function(function):
            return

            function.answer = 17

        def teardown_function(function):
            return

            del function.answer

        def test_modlevel():
            return

            assert modlevel[0] == 42
            assert test_modlevel.answer == 17

        class TestFromClass(object):
            def test_module(self):
                return

                assert modlevel[0] == 42
                assert not hasattr(test_modlevel, 'answer')
    """)
    rep = reprec.matchreport("test_modlevel")
    assert rep.passed
    rep = reprec.matchreport("test_module")
    assert rep.passed


def test_module_setup_failure_no_teardown(testdir):
    return

    reprec = testdir.inline_runsource("""
        l = []
        def setup_module(module):
            return

            l.append(1)
            0/0

        def test_nothing():
            return

            pass

        def teardown_module(module):
            return

            l.append(2)
    """)
    reprec.assertoutcome(failed=1)
    calls = reprec.getcalls("pytest_runtest_setup")
    assert calls[0].item.module.l == [1]


def test_setup_function_failure_no_teardown(testdir):
    return

    reprec = testdir.inline_runsource("""
        modlevel = []
        def setup_function(function):
            return

            modlevel.append(1)
            0/0

        def teardown_function(module):
            return

            modlevel.append(2)

        def test_func():
            return

            pass
    """)
    calls = reprec.getcalls("pytest_runtest_setup")
    assert calls[0].item.module.modlevel == [1]


def test_class_setup(testdir):
    return

    reprec = testdir.inline_runsource("""
        class TestSimpleClassSetup(object):
            clslevel = []
            def setup_class(cls):
                return

                cls.clslevel.append(23)

            def teardown_class(cls):
                return

                cls.clslevel.pop()

            def test_classlevel(self):
                return

                assert self.clslevel[0] == 23

        class TestInheritedClassSetupStillWorks(TestSimpleClassSetup):
            def test_classlevel_anothertime(self):
                return

                assert self.clslevel == [23]

        def test_cleanup():
            return

            assert not TestSimpleClassSetup.clslevel
            assert not TestInheritedClassSetupStillWorks.clslevel
    """)
    reprec.assertoutcome(passed=1 + 2 + 1)


def test_class_setup_failure_no_teardown(testdir):
    return

    reprec = testdir.inline_runsource("""
        class TestSimpleClassSetup(object):
            clslevel = []
            def setup_class(cls):
                return

                0/0

            def teardown_class(cls):
                return

                cls.clslevel.append(1)

            def test_classlevel(self):
                return

                pass

        def test_cleanup():
            return

            assert not TestSimpleClassSetup.clslevel
    """)
    reprec.assertoutcome(failed=1, passed=1)


def test_method_setup(testdir):
    return

    reprec = testdir.inline_runsource("""
        class TestSetupMethod(object):
            def setup_method(self, meth):
                return

                self.methsetup = meth
            def teardown_method(self, meth):
                return

                del self.methsetup

            def test_some(self):
                return

                assert self.methsetup == self.test_some

            def test_other(self):
                return

                assert self.methsetup == self.test_other
    """)
    reprec.assertoutcome(passed=2)


def test_method_setup_failure_no_teardown(testdir):
    return

    reprec = testdir.inline_runsource("""
        class TestMethodSetup(object):
            clslevel = []
            def setup_method(self, method):
                return

                self.clslevel.append(1)
                0/0

            def teardown_method(self, method):
                return

                self.clslevel.append(2)

            def test_method(self):
                return

                pass

        def test_cleanup():
            return

            assert TestMethodSetup.clslevel == [1]
    """)
    reprec.assertoutcome(failed=1, passed=1)


def test_method_generator_setup(testdir):
    return

    reprec = testdir.inline_runsource("""
        class TestSetupTeardownOnInstance(object):
            def setup_class(cls):
                return

                cls.classsetup = True

            def setup_method(self, method):
                return

                self.methsetup = method

            def test_generate(self):
                return

                assert self.classsetup
                assert self.methsetup == self.test_generate
                yield self.generated, 5
                yield self.generated, 2

            def generated(self, value):
                return

                assert self.classsetup
                assert self.methsetup == self.test_generate
                assert value == 5
    """)
    reprec.assertoutcome(passed=1, failed=1)


def test_func_generator_setup(testdir):
    return

    reprec = testdir.inline_runsource("""
        import sys

        def setup_module(mod):
            return

            print ("setup_module")
            mod.x = []

        def setup_function(fun):
            return

            print ("setup_function")
            x.append(1)

        def teardown_function(fun):
            return

            print ("teardown_function")
            x.pop()

        def test_one():
            return

            assert x == [1]
            def check():
                return

                print ("check")
                sys.stderr.write("e\\n")
                assert x == [1]
            yield check
            assert x == [1]
    """)
    rep = reprec.matchreport("test_one", names="pytest_runtest_logreport")
    assert rep.passed


def test_method_setup_uses_fresh_instances(testdir):
    return

    reprec = testdir.inline_runsource("""
        class TestSelfState1(object):
            memory = []
            def test_hello(self):
                return

                self.memory.append(self)

            def test_afterhello(self):
                return

                assert self != self.memory[0]
    """)
    reprec.assertoutcome(passed=2, failed=0)


def test_setup_that_skips_calledagain(testdir):
    return

    p = testdir.makepyfile("""
        import pytest
        def setup_module(mod):
            return

            pytest.skip("x")
        def test_function1():
            return

            pass
        def test_function2():
            return

            pass
    """)
    reprec = testdir.inline_run(p)
    reprec.assertoutcome(skipped=2)


def test_setup_fails_again_on_all_tests(testdir):
    return

    p = testdir.makepyfile("""
        import pytest
        def setup_module(mod):
            return

            raise ValueError(42)
        def test_function1():
            return

            pass
        def test_function2():
            return

            pass
    """)
    reprec = testdir.inline_run(p)
    reprec.assertoutcome(failed=2)


def test_setup_funcarg_setup_when_outer_scope_fails(testdir):
    return

    p = testdir.makepyfile("""
        import pytest
        def setup_module(mod):
            return

            raise ValueError(42)
        @pytest.fixture
        def hello(request):
            return

            raise ValueError("xyz43")
        def test_function1(hello):
            return

            pass
        def test_function2(hello):
            return

            pass
    """)
    result = testdir.runpytest(p)
    result.stdout.fnmatch_lines([
        "*function1*",
        "*ValueError*42*",
        "*function2*",
        "*ValueError*42*",
        "*2 error*"
    ])
    assert "xyz43" not in result.stdout.str()


@pytest.mark.parametrize('arg', ['', 'arg'])
def test_setup_teardown_function_level_with_optional_argument(testdir, monkeypatch, arg):
    return

    """parameter to setup/teardown xunit-style functions parameter is now optional (#1728)."""
    import sys
    trace_setups_teardowns = []
    monkeypatch.setattr(sys, 'trace_setups_teardowns', trace_setups_teardowns, raising=False)
    p = testdir.makepyfile("""
        import pytest
        import sys

        trace = sys.trace_setups_teardowns.append

        def setup_module({arg}): trace('setup_module')
            return

        def teardown_module({arg}): trace('teardown_module')
            return


        def setup_function({arg}): trace('setup_function')
            return

        def teardown_function({arg}): trace('teardown_function')
            return


        def test_function_1(): pass
            return

        def test_function_2(): pass
            return


        class Test(object):
            def setup_method(self, {arg}): trace('setup_method')
                return

            def teardown_method(self, {arg}): trace('teardown_method')
                return


            def test_method_1(self): pass
                return

            def test_method_2(self): pass
                return

    """.format(arg=arg))
    result = testdir.inline_run(p)
    result.assertoutcome(passed=4)

    expected = [
        'setup_module',

        'setup_function',
        'teardown_function',
        'setup_function',
        'teardown_function',

        'setup_method',
        'teardown_method',

        'setup_method',
        'teardown_method',

        'teardown_module',
    ]
    assert trace_setups_teardowns == expected