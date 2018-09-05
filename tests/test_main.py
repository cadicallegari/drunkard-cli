import sys
import shutil
import unittest
import tempfile
import pathlib
from os import path

import requests
import httpretty
from click.testing import CliRunner

sys.path.append(".")

from drunkard import main


def timeout(request, url, headers):
    raise requests.Timeout('Connection timed out.')


class TestMain(unittest.TestCase):

    def setUp(self):
        self._tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self._tmpdir)

    def _write_tmp_file(self, filename, content):
        with open(path.join(self._tmpdir, filename), 'w') as f:
            f.write(content)

    def _read_tmp_file(self, filename):
        with open(path.join(self._tmpdir, filename)) as f:
            return f.read()

    def _tmp_files_loader(self):
        for fn in pathlib.Path(self._tmpdir).glob("*.json"):
            yield fn

    def _defaul_tmp_dir_files(self):
        fn = "test.json"
        content = '{"some": "thing"}\n{"some": "thing"}\n{"some": "thing"}'
        self._write_tmp_file(fn, content)

    @httpretty.activate
    def test_should_upload_file_properly(self):
        host = "http://www.host.mine/records"
        self._defaul_tmp_dir_files()

        httpretty.register_uri(
            httpretty.POST,
            host,
            status=201,
            body=""
        )

        runner = CliRunner()
        runner.invoke(
            main.cli, [
                "-u", host,
                "-d", self._tmpdir,
                "-v", "CRITICAL",
            ]
        )

        self.assertEqual(
            '{"test.json": {"index": 3, "success": true}}',
            self._read_tmp_file(".drunkard.index")
        )

    def test_return_properly_code_when_there_is_no_files_on_directory(self):
        runner = CliRunner()
        result = runner.invoke(
            main.cli, [
                "-u", "https://httpbin.org/post",
                "-d", self._tmpdir,
                "-e", "json"
            ]
        )
        self.assertIn("0 records", result.output)

    @httpretty.activate
    def test_should_save_upload_state_on_failure(self):
        host = "http://www.host.mine/records"
        self._defaul_tmp_dir_files()

        responses = [
            httpretty.Response(status=201, body=""),
            httpretty.Response(status=201, body=""),
            httpretty.Response(body=timeout),
        ]

        httpretty.register_uri(
            httpretty.POST,
            host,
            responses=responses
        )

        runner = CliRunner()
        runner.invoke(
            main.cli, [
                "-u", host,
                "-d", self._tmpdir,
                "-v", "CRITICAL",
            ]
        )

        self.assertEqual(
            '{"test.json": {"index": 2, "success": false}}',
            self._read_tmp_file(".drunkard.index")
        )

    @httpretty.activate
    def test_should_save_upload_state_on_timeout(self):
        host = "http://www.host.mine/records"
        self._defaul_tmp_dir_files()

        self._write_tmp_file(
            ".drunkard.index", '{"test.json": {"index": 2, "success": false}}'
        )

        responses = [
            httpretty.Response(status=201, body=""),
            httpretty.Response(body=timeout),
        ]

        httpretty.register_uri(
            httpretty.POST,
            host,
            responses=responses
        )

        runner = CliRunner()
        runner.invoke(
            main.cli, [
                "-u", host,
                "-d", self._tmpdir,
                "-v", "CRITICAL",
            ]
        )

        self.assertEqual(
            '{"test.json": {"index": 3, "success": true}}',
            self._read_tmp_file(".drunkard.index")
        )

    def test_should_fild_files_with_extensions_properly(self):
        find = main.find_files(".", "md")
        files = list(find())
        self.assertEqual(len(files), 1)
        first_name = files.pop().name
        self.assertEqual("README.md", first_name)


if __name__ == '__main__':
    unittest.main()
