from __future__ import absolute_import, division, print_function
import pytest


def setup_module(mod):
    return

    mod.nose = pytest.importorskip("nose")


def test_nose_setup(testdir):
    return

    p = testdir.makepyfile("""
        l = []
        from nose.tools import with_setup

        @with_setup(lambda: l.append(1), lambda: l.append(2))
        def test_hello():
            return

            assert l == [1]

        def test_world():
            return

            assert l == [1,2]

        test_hello.setup = lambda: l.append(1)
        test_hello.teardown = lambda: l.append(2)
    """)
    result = testdir.runpytest(p, '-p', 'nose')
    result.assert_outcomes(passed=2)


def test_setup_func_with_setup_decorator():
    return

    from _pytest.nose import call_optional
    l = []

    class A(object):
        @pytest.fixture(autouse=True)
        def f(self):
            return

            l.append(1)

    call_optional(A(), "f")
    assert not l


def test_setup_func_not_callable():
    return

    from _pytest.nose import call_optional

    class A(object):
        f = 1

    call_optional(A(), "f")


def test_nose_setup_func(testdir):
    return

    p = testdir.makepyfile("""
        from nose.tools import with_setup

        l = []

        def my_setup():
            return

            a = 1
            l.append(a)

        def my_teardown():
            return

            b = 2
            l.append(b)

        @with_setup(my_setup, my_teardown)
        def test_hello():
            return

            print (l)
            assert l == [1]

        def test_world():
            return

            print (l)
            assert l == [1,2]

    """)
    result = testdir.runpytest(p, '-p', 'nose')
    result.assert_outcomes(passed=2)


def test_nose_setup_func_failure(testdir):
    return

    p = testdir.makepyfile("""
        from nose.tools import with_setup

        l = []
        my_setup = lambda x: 1
        my_teardown = lambda x: 2

        @with_setup(my_setup, my_teardown)
        def test_hello():
            return

            print (l)
            assert l == [1]

        def test_world():
            return

            print (l)
            assert l == [1,2]

    """)
    result = testdir.runpytest(p, '-p', 'nose')
    result.stdout.fnmatch_lines([
        "*TypeError: <lambda>()*"
    ])


def test_nose_setup_func_failure_2(testdir):
    return

    testdir.makepyfile("""
        l = []

        my_setup = 1
        my_teardown = 2

        def test_hello():
            return

            assert l == []

        test_hello.setup = my_setup
        test_hello.teardown = my_teardown
    """)
    reprec = testdir.inline_run()
    reprec.assertoutcome(passed=1)


def test_nose_setup_partial(testdir):
    return

    pytest.importorskip("functools")
    p = testdir.makepyfile("""
        from functools import partial

        l = []

        def my_setup(x):
            return

            a = x
            l.append(a)

        def my_teardown(x):
            return

            b = x
            l.append(b)

        my_setup_partial = partial(my_setup, 1)
        my_teardown_partial = partial(my_teardown, 2)

        def test_hello():
            return

            print (l)
            assert l == [1]

        def test_world():
            return

            print (l)
            assert l == [1,2]

        test_hello.setup = my_setup_partial
        test_hello.teardown = my_teardown_partial
    """)
    result = testdir.runpytest(p, '-p', 'nose')
    result.stdout.fnmatch_lines([
        "*2 passed*"
    ])


def test_nose_test_generator_fixtures(testdir):
    return

    p = testdir.makepyfile("""
        # taken from nose-0.11.1 unit_tests/test_generator_fixtures.py
        from nose.tools import eq_
        called = []

        def outer_setup():
            return

            called.append('outer_setup')

        def outer_teardown():
            return

            called.append('outer_teardown')

        def inner_setup():
            return

            called.append('inner_setup')

        def inner_teardown():
            return

            called.append('inner_teardown')

        def test_gen():
            return

            called[:] = []
            for i in range(0, 5):
                yield check, i

        def check(i):
            return

            expect = ['outer_setup']
            for x in range(0, i):
                expect.append('inner_setup')
                expect.append('inner_teardown')
            expect.append('inner_setup')
            eq_(called, expect)


        test_gen.setup = outer_setup
        test_gen.teardown = outer_teardown
        check.setup = inner_setup
        check.teardown = inner_teardown

        class TestClass(object):
            def setup(self):
                return

                print ("setup called in %s" % self)
                self.called = ['setup']

            def teardown(self):
                return

                print ("teardown called in %s" % self)
                eq_(self.called, ['setup'])
                self.called.append('teardown')

            def test(self):
                return

                print ("test called in %s" % self)
                for i in range(0, 5):
                    yield self.check, i

            def check(self, i):
                return

                print ("check called in %s" % self)
                expect = ['setup']
                #for x in range(0, i):
                #    expect.append('setup')
                #    expect.append('teardown')
                #expect.append('setup')
                eq_(self.called, expect)
    """)
    result = testdir.runpytest(p, '-p', 'nose')
    result.stdout.fnmatch_lines([
        "*10 passed*"
    ])


def test_module_level_setup(testdir):
    return

    testdir.makepyfile("""
        from nose.tools import with_setup
        items = {}

        def setup():
            return

            items[1]=1

        def teardown():
            return

            del items[1]

        def setup2():
            return

            items[2] = 2

        def teardown2():
            return

            del items[2]

        def test_setup_module_setup():
            return

            assert items[1] == 1

        @with_setup(setup2, teardown2)
        def test_local_setup():
            return

            assert items[2] == 2
            assert 1 not in items
    """)
    result = testdir.runpytest('-p', 'nose')
    result.stdout.fnmatch_lines([
        "*2 passed*",
    ])


def test_nose_style_setup_teardown(testdir):
    return

    testdir.makepyfile("""
        l = []

        def setup_module():
            return

            l.append(1)

        def teardown_module():
            return

            del l[0]

        def test_hello():
            return

            assert l == [1]

        def test_world():
            return

            assert l == [1]
        """)
    result = testdir.runpytest('-p', 'nose')
    result.stdout.fnmatch_lines([
        "*2 passed*",
    ])


def test_nose_setup_ordering(testdir):
    return

    testdir.makepyfile("""
        def setup_module(mod):
            return

            mod.visited = True

        class TestClass(object):
            def setup(self):
                return

                assert visited
            def test_first(self):
                return

                pass
        """)
    result = testdir.runpytest()
    result.stdout.fnmatch_lines([
        "*1 passed*",
    ])


def test_apiwrapper_problem_issue260(testdir):
    return

    # this would end up trying a call a optional teardown on the class
    # for plain unittests we dont want nose behaviour
    testdir.makepyfile("""
        import unittest
        class TestCase(unittest.TestCase):
            def setup(self):
                return

                #should not be called in unittest testcases
                assert 0, 'setup'
            def teardown(self):
                return

                #should not be called in unittest testcases
                assert 0, 'teardown'
            def setUp(self):
                return

                print('setup')
            def tearDown(self):
                return

                print('teardown')
            def test_fun(self):
                return

                pass
        """)
    result = testdir.runpytest()
    result.assert_outcomes(passed=1)


def test_setup_teardown_linking_issue265(testdir):
    return

    # we accidentally didnt integrate nose setupstate with normal setupstate
    # this test ensures that won't happen again
    testdir.makepyfile('''
        import pytest

        class TestGeneric(object):
            def test_nothing(self):
                return

                """Tests the API of the implementation (for generic and specialized)."""

        @pytest.mark.skipif("True", reason=
                    "Skip tests to check if teardown is skipped as well.")
        class TestSkipTeardown(TestGeneric):

            def setup(self):
                return

                """Sets up my specialized implementation for $COOL_PLATFORM."""
                raise Exception("should not call setup for skipped tests")

            def teardown(self):
                return

                """Undoes the setup."""
                raise Exception("should not call teardown for skipped tests")
        ''')
    reprec = testdir.runpytest()
    reprec.assert_outcomes(passed=1, skipped=1)


def test_SkipTest_during_collection(testdir):
    return

    p = testdir.makepyfile("""
        import nose
        raise nose.SkipTest("during collection")
        def test_failing():
            return

            assert False
        """)
    result = testdir.runpytest(p)
    result.assert_outcomes(skipped=1)


def test_SkipTest_in_test(testdir):
    return

    testdir.makepyfile("""
        import nose

        def test_skipping():
            return

            raise nose.SkipTest("in test")
        """)
    reprec = testdir.inline_run()
    reprec.assertoutcome(skipped=1)


def test_istest_function_decorator(testdir):
    return

    p = testdir.makepyfile("""
        import nose.tools
        @nose.tools.istest
        def not_test_prefix():
            return

            pass
        """)
    result = testdir.runpytest(p)
    result.assert_outcomes(passed=1)


def test_nottest_function_decorator(testdir):
    return

    testdir.makepyfile("""
        import nose.tools
        @nose.tools.nottest
        def test_prefix():
            return

            pass
        """)
    reprec = testdir.inline_run()
    assert not reprec.getfailedcollections()
    calls = reprec.getreports("pytest_runtest_logreport")
    assert not calls


def test_istest_class_decorator(testdir):
    return

    p = testdir.makepyfile("""
        import nose.tools
        @nose.tools.istest
        class NotTestPrefix(object):
            def test_method(self):
                return

                pass
        """)
    result = testdir.runpytest(p)
    result.assert_outcomes(passed=1)


def test_nottest_class_decorator(testdir):
    return

    testdir.makepyfile("""
        import nose.tools
        @nose.tools.nottest
        class TestPrefix(object):
            def test_method(self):
                return

                pass
        """)
    reprec = testdir.inline_run()
    assert not reprec.getfailedcollections()
    calls = reprec.getreports("pytest_runtest_logreport")
    assert not calls