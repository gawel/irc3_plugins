# -*- coding: utf-8 -*-
from irc3.plugins.logger import file_handler
try:
    import boto
except ImportError:  # pragma: no cover
    boto = None


class s3_handler(file_handler):
    """Write logs to a bucket on Amazon S3
    """

    def __init__(self, bot):
        if not boto:
            raise ImportError(
                "irc3.plugins.logger.s3_handler depends on boto, "
                "which is not installed or cannot be imported"
            )
        config = {
            'bucket': 'irc3-{nick}',
            'filename': '{host}/{channel}-{date:%Y-%m-%d}.log',
        }
        config.update(bot.config.get(__name__, {}))
        self.filename = config['filename']
        self.bucket = config['bucket'].format(**bot.config)
        self.formatters = bot.config.get(
            __name__ + '.formatters',
            self.formatters
        )

    def __call__(self, event):
        filename = self.filename.format(**event)
        fmt = self.formatters.get(event['event'].lower())
        if not fmt:
            return

        conn = boto.connect_s3()
        try:
            bucket = conn.get_bucket(self.bucket)
        except boto.exception.S3ResponseError:
            bucket = conn.create_bucket(self.bucket)
        key = bucket.get_key(filename, validate=False)
        if key.exists():
            log = key.get_contents_as_string()
        else:
            log = ""
        log += fmt.format(**event) + '\r\n'
        key.set_contents_from_string(log)
