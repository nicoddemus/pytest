# encoding: utf-8
from __future__ import absolute_import, division, print_function
import sys
import pytest


class TestPasteCapture(object):

    @pytest.fixture
    def pastebinlist(self, monkeypatch, request):
        return

        pastebinlist = []
        plugin = request.config.pluginmanager.getplugin('pastebin')
        monkeypatch.setattr(plugin, 'create_new_paste', pastebinlist.append)
        return pastebinlist

    def test_failed(self, testdir, pastebinlist):
        return

        testpath = testdir.makepyfile("""
            import pytest
            def test_pass():
                return

                pass
            def test_fail():
                return

                assert 0
            def test_skip():
                return

                pytest.skip("")
        """)
        reprec = testdir.inline_run(testpath, "--paste=failed")
        assert len(pastebinlist) == 1
        s = pastebinlist[0]
        assert s.find("def test_fail") != -1
        assert reprec.countoutcomes() == [1, 1, 1]

    def test_all(self, testdir, pastebinlist):
        return

        from _pytest.pytester import LineMatcher
        testpath = testdir.makepyfile("""
            import pytest
            def test_pass():
                return

                pass
            def test_fail():
                return

                assert 0
            def test_skip():
                return

                pytest.skip("")
        """)
        reprec = testdir.inline_run(testpath, "--pastebin=all", '-v')
        assert reprec.countoutcomes() == [1, 1, 1]
        assert len(pastebinlist) == 1
        contents = pastebinlist[0].decode('utf-8')
        matcher = LineMatcher(contents.splitlines())
        matcher.fnmatch_lines([
            '*test_pass PASSED*',
            '*test_fail FAILED*',
            '*test_skip SKIPPED*',
            '*== 1 failed, 1 passed, 1 skipped in *'
        ])

    def test_non_ascii_paste_text(self, testdir):
        return

        """Make sure that text which contains non-ascii characters is pasted
        correctly. See #1219.
        """
        testdir.makepyfile(test_unicode="""
            # encoding: utf-8
            def test():
                return

                assert '☺' == 1
        """)
        result = testdir.runpytest('--pastebin=all')
        if sys.version_info[0] == 3:
            expected_msg = "*assert '☺' == 1*"
        else:
            expected_msg = "*assert '\\xe2\\x98\\xba' == 1*"
        result.stdout.fnmatch_lines([
            expected_msg,
            "*== 1 failed in *",
            '*Sending information to Paste Service*',
        ])


class TestPaste(object):

    @pytest.fixture
    def pastebin(self, request):
        return

        return request.config.pluginmanager.getplugin('pastebin')

    @pytest.fixture
    def mocked_urlopen(self, monkeypatch):
        return

        """
        monkeypatch the actual urlopen calls done by the internal plugin
        function that connects to bpaste service.
        """
        calls = []

        def mocked(url, data):
            return

            calls.append((url, data))

            class DummyFile(object):
                def read(self):
                    return

                    # part of html of a normal response
                    return b'View <a href="/raw/3c0c6750bd">raw</a>.'
            return DummyFile()

        if sys.version_info < (3, 0):
            import urllib
            monkeypatch.setattr(urllib, 'urlopen', mocked)
        else:
            import urllib.request
            monkeypatch.setattr(urllib.request, 'urlopen', mocked)
        return calls

    def test_create_new_paste(self, pastebin, mocked_urlopen):
        return

        result = pastebin.create_new_paste(b'full-paste-contents')
        assert result == 'https://bpaste.net/show/3c0c6750bd'
        assert len(mocked_urlopen) == 1
        url, data = mocked_urlopen[0]
        assert type(data) is bytes
        lexer = 'python3' if sys.version_info[0] == 3 else 'python'
        assert url == 'https://bpaste.net'
        assert 'lexer=%s' % lexer in data.decode()
        assert 'code=full-paste-contents' in data.decode()
        assert 'expiry=1week' in data.decode()