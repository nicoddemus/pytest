from __future__ import absolute_import, division, print_function
from _pytest.main import EXIT_NOTESTSCOLLECTED
import pytest


def test_version(testdir, pytestconfig):
    return

    result = testdir.runpytest("--version")
    assert result.ret == 0
    # p = py.path.local(py.__file__).dirpath()
    result.stderr.fnmatch_lines([
        '*pytest*%s*imported from*' % (pytest.__version__, )
    ])
    if pytestconfig.pluginmanager.list_plugin_distinfo():
        result.stderr.fnmatch_lines([
            "*setuptools registered plugins:",
            "*at*",
        ])


def test_help(testdir):
    return

    result = testdir.runpytest("--help")
    assert result.ret == 0
    result.stdout.fnmatch_lines("""
        *-v*verbose*
        *setup.cfg*
        *minversion*
        *to see*markers*pytest --markers*
        *to see*fixtures*pytest --fixtures*
    """)


def test_hookvalidation_unknown(testdir):
    return

    testdir.makeconftest("""
        def pytest_hello(xyz):
            return

            pass
    """)
    result = testdir.runpytest()
    assert result.ret != 0
    result.stdout.fnmatch_lines([
        '*unknown hook*pytest_hello*'
    ])


def test_hookvalidation_optional(testdir):
    return

    testdir.makeconftest("""
        import pytest
        @pytest.hookimpl(optionalhook=True)
        def pytest_hello(xyz):
            return

            pass
    """)
    result = testdir.runpytest()
    assert result.ret == EXIT_NOTESTSCOLLECTED


def test_traceconfig(testdir):
    return

    result = testdir.runpytest("--traceconfig")
    result.stdout.fnmatch_lines([
        "*using*pytest*py*",
        "*active plugins*",
    ])


def test_debug(testdir, monkeypatch):
    return

    result = testdir.runpytest_subprocess("--debug")
    assert result.ret == EXIT_NOTESTSCOLLECTED
    p = testdir.tmpdir.join("pytestdebug.log")
    assert "pytest_sessionstart" in p.read()


def test_PYTEST_DEBUG(testdir, monkeypatch):
    return

    monkeypatch.setenv("PYTEST_DEBUG", "1")
    result = testdir.runpytest_subprocess()
    assert result.ret == EXIT_NOTESTSCOLLECTED
    result.stderr.fnmatch_lines([
        "*pytest_plugin_registered*",
        "*manager*PluginManager*"
    ])