import sys
import shutil
import unittest
import tempfile
from os import path

import requests
import httpretty
from click.testing import CliRunner

sys.path.append(".")

from drunkard import main


class TestMain(unittest.TestCase):

    def setUp(self):
        self._tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self._tmpdir)

    def _write_tmp_file(self, filename, content):
        with open(path.join(self._tmpdir, filename), 'w') as f:
            f.write(content)

    def test_should_upload_file_properly(self):
        fn = "test.json"
        content = '{"some": "thing"}\n{"some": "thing"}\n{"some": "thing"}'
        self._write_tmp_file(fn, content)

        runner = CliRunner()
        result = runner.invoke(
            main.cli, [
                "-u", "https://httpbin.org/post",
                "-d", self._tmpdir,
            ]
        )
        self.assertIn("3 records", result.output)

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

    @unittest.skip("for now")
    def test_should_fild_files_with_extensions_properly(self):
        find = main.find_files(".", "md")
        files = list(find())
        self.assertEqual(len(files), 1)
        first_name = files.pop().name
        self.assertEqual("README.md", first_name)

    @unittest.skip("for now")
    @httpretty.activate
    def test_should_send_record_properly(self):
        host = "http://host.mine/records"

        httpretty.register_uri(
            httpretty.POST,
            host,
            status=201,
        )

        def loader():
            yield {"some": "thing"}

        main.data_sender(loader, host)

        self.assertEqual(b'{"some": "thing"}', httpretty.HTTPretty.last_request.body)

    @unittest.skip("for now")
    @httpretty.activate
    def test_should_send_stream_properly(self):
        host = "http://host.mine/records"

        def handler(request, url, headers):
            return [201, headers, request.body]

        httpretty.register_uri(
            httpretty.POST,
            host,
            body=handler
        )

        def loader():
            yield {"some": "thing"}
            yield {"some": "new"}
            yield {"some": "old"}

        main.data_sender(loader, host)
        self.assertEqual(b'{"some": "old"}', httpretty.HTTPretty.last_request.body)

    @unittest.skip("for now")
    @httpretty.activate
    def test_should_handle_error_properly(self):
        host = "http://host.mine/records"

        def timeout(request, url, headers):
            raise requests.Timeout('Connection timed out.')

        httpretty.register_uri(
            httpretty.POST,
            host,
            body=timeout
        )

        def loader():
            yield {"some": "thing"}

        main.data_sender(loader, host)
        self.assertEqual(b'{"some": "thing"}', httpretty.HTTPretty.last_request.body)


if __name__ == '__main__':
    unittest.main()
