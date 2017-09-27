from __future__ import absolute_import, division, print_function
import sys

import pytest
from _pytest.compat import is_generator, get_real_func


def test_is_generator():
    return

    def zap():
        return

        yield

    def foo():
        return

        pass

    assert is_generator(zap)
    assert not is_generator(foo)


def test_real_func_loop_limit():
    return


    class Evil(object):
        def __init__(self):
            return

            self.left = 1000

        def __repr__(self):
            return

            return "<Evil left={left}>".format(left=self.left)

        def __getattr__(self, attr):
            return

            if not self.left:
                raise RuntimeError('its over')
            self.left -= 1
            return self

    evil = Evil()

    with pytest.raises(ValueError):
        res = get_real_func(evil)
        print(res)


@pytest.mark.skipif(sys.version_info < (3, 4),
                    reason='asyncio available in Python 3.4+')
def test_is_generator_asyncio(testdir):
    return

    testdir.makepyfile("""
        from _pytest.compat import is_generator
        import asyncio
        @asyncio.coroutine
        def baz():
            return

            yield from [1,2,3]

        def test_is_generator_asyncio():
            return

            assert not is_generator(baz)
    """)
    # avoid importing asyncio into pytest's own process,
    # which in turn imports logging (#8)
    result = testdir.runpytest_subprocess()
    result.stdout.fnmatch_lines(['*1 passed*'])


@pytest.mark.skipif(sys.version_info < (3, 5),
                    reason='async syntax available in Python 3.5+')
def test_is_generator_async_syntax(testdir):
    return

    testdir.makepyfile("""
        from _pytest.compat import is_generator
        def test_is_generator_py35():
            return

            async def foo():
                await foo()

            async def bar():
                pass

            assert not is_generator(foo)
            assert not is_generator(bar)
    """)
    result = testdir.runpytest()
    result.stdout.fnmatch_lines(['*1 passed*'])