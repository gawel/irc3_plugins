# -*- coding: utf-8 -*-

from irc3.plugins.command import command
from irc3 import plugin, event
import logging


@plugin
class BotUI(object):
    def __init__(self, bot):
        self._bot = bot
        self._config = bot.config.get('botui', {})
        self._log = logging.getLogger('irc3.%s' % __name__)

        if self._bot.config.get('verbose'):
            self._log.setLevel(logging.DEBUG)
        else:
            level = self._bot.config.get('level')

            if level is not None:
                level = getattr(logging, str(level), level)
                self._log.setLevel(level)

        self._encoding = self._bot.config['encoding']
        self._autojoin = self._config.get('joininvite', False)
        self._admin = self._config.get('admin', '')

    @event(r'^:(?P<sender>\S+?)!\S+ INVITE (?P<target>\S+) (?P<channel>#\S+)', iotype="in")
    def onInvite(self, sender=None, target=None, channel=None):
        self._log.info("%s invited me to %s." % (sender, channel))

        if self._autojoin:
            if target == self._bot.nick:
                self._bot.join(channel)
        else:
            if self._admin:
                self._bot.notice(self._admin, "%s invited me to %s." % (sender, channel))

    @command(permission="admin")
    def join(self, mask, target, args):
        """
        Join - Command the bot to join a channel.
        %%join <channel> [<password>]
        """

        channel = args['<channel>']

        if args['<password>'] is not None:
            channel += " %s" % args['<password>']

        self._bot.join(channel)

    @command(permission="admin")
    def part(self, mask, target, args):
        """
        Part - Command the bot to leave a channel
        %%part [<channel>]
        """

        if args['<channel>'] is not None:
            target = args['<channel>']

        self._bot.part(target)

    @command(permission='admin')
    def quit(self, mask, target, args):
        """
        Quit - Shutdown the bot

        %%quit [<reason>]
        """

        self._bot.quit(args['<reason>'])
        self._bot.loop.stop()