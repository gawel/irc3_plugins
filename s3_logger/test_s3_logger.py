# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase, mock
from unittest import SkipTest
from unittest import skip
from freezegun import freeze_time
try:
    from moto import mock_s3
    import boto
except ImportError:
    mock_s3 = lambda x: x
    boto = None


@skip('broken')
class LoggerS3NullTestCase(BotTestCase):
    config = {
        "nick": "myircbot",
        "host": "irc.testing.net",
        "includes": [
            'irc3.plugins.logger',
            'irc3.plugins.userlist',
        ],
    }

    @mock.patch('s3_logger.boto', None)
    def test_no_boto(self):
        with self.assertRaises(ImportError):
            self.callFTU(
                **{'irc3.plugins.logger': dict(
                    handler='s3_logger.s3_handler',
                )}
            )


@skip('broken')
class LoggerS3TestCase(LoggerS3NullTestCase):
    def setUp(self):
        super(LoggerS3NullTestCase, self).setUp()
        if not boto:
            raise SkipTest("missing dependency: boto")

        self.bot = self.callFTU(
            **{'irc3.plugins.logger': dict(
                handler='s3_logger.s3_handler',
            )}
        )

    @mock_s3
    @freeze_time("2014-01-04")
    def test_message(self):
        self.bot.dispatch(':server 332 foo #foo :topic')
        conn = boto.connect_s3()
        bucket = conn.get_bucket("irc3-myircbot")
        key = bucket.get_key("irc.testing.net/#foo-2014-01-04.log")
        self.assertIn(
            'server has set topic to: topic\r\n',
            key.get_contents_as_string().decode('utf8')
        )
