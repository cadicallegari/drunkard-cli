import sys
import unittest

import requests
import httpretty

sys.path.append(".")

from drunkard import main


class TestMain(unittest.TestCase):

    def test_should_fild_files_with_extensions_properly(self):
        find = main.find_files(".", "md")
        files = list(find())
        self.assertEqual(len(files), 1)
        first_name = files.pop().name
        self.assertEqual("README.md", first_name)

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
