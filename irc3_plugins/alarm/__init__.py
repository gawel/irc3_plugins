# -*- coding: utf-8 -*-
import logging
from functools import partial
from irc3.plugins.command import command
from irc3.compat import asyncio
import irc3


class Item(dict):

    @classmethod
    def from_args(cls, nick, args):
        idle = args['<idle>'] or 180
        data = dict(
            name=args['<name>'],
            nick=nick,
            idle=int(idle),
            target=args['<target>'],
            crontab='%(<mn>)s %(<h>)s %(<dom>)s %(<m>)s %(<dow>)s' % args
        )
        return cls(data)

    def __getattr__(self, attr):
        return self.get(attr)

    @property
    def data(self):
        return dict(
            name=self.name,
            nick=self.nick,
            target=self.target,
            idle=self.idle,
            crontab=self.crontab)

    def __str__(self):
        return '%(name)s: %(target)s - %(crontab)s (%(idle)smn idle)' % self


@irc3.plugin
class Alarms(object):

    requires = ['irc3.plugins.command',
                'irc3.plugins.storage',
                'irc3.plugins.async',
                'irc3.plugins.cron']

    def __init__(self, bot):
        self.bot = bot
        self.log = bot.log
        self.key = __name__ + '.alarms'
        self.alarms = {}
        self.log = logging.getLogger('irc3.alarm')

    def __repr__(self):
        return '<Alarms>'

    def connection_made(self):
        self.start()

    @command(permission='admin')
    def alarm(self, mask=None, target=None, args=None):
        """Alarm

            %%alarm list
            %%alarm reload
            %%alarm (toogle|delete|test) <name>
            %%alarm set <name> <target> <mn> <h> <dom> <m> <dow> [<idle>]
        """
        db = self.bot.db
        alarms = db[self.key]

        name = args.get('<name>')
        if args.get('list'):
            for name in sorted(self.alarms):
                status = alarms[name] and ' [on]' or ' [off]'
                yield str(self.get(name)) + status
        if args.get('reload'):
            self.bot.reload(__name__)
        elif args.get('set'):
            if name in self.alarms:
                self.delete(name)
            item = Item.from_args(mask.nick, args)
            db['%s.%s' % (self.key, name)] = item.data
            alarms[name] = True
            db[self.key] = alarms
            yield str(self.get(name))
        elif args.get('toogle'):
            alarms[name] = not bool(alarms[name])
            db[self.key] = alarms
            yield 'alarm %s is %s' % (name, alarms[name] and 'on' or 'off')
        elif args.get('delete'):
            self.delete(name)
            yield 'alarm %s deleted' % name
        elif args.get('test'):
            self.ring(self.get(name))
            yield 'test for alarm %s sent' % name

    def get(self, name):
        if name not in self.alarms:
            alarm = self.bot.db['%s.%s' % (self.key, name)]
            if not alarm:
                raise LookupError(name)
            alarm = self.alarms[name] = Item(alarm)
            c = self.bot.add_cron(alarm.crontab,
                                  partial(self.async_cron, name))
            alarm.update(cron=c)
        alarm = self.alarms[name]
        alarm['enable'] = self.bot.db[self.key][name]
        return alarm

    def delete(self, name):
        self.stop()
        db = self.bot.db
        del self.bot.db['%s.%s' % (self.key, name)]
        alarms = db[self.key]
        del alarms[name]
        alarms = db[self.key] = alarms
        self.start()

    def start(self):
        for name in self.bot.db[self.key]:
            self.get(name)

    def stop(self):
        for name in self.bot.db[self.key]:
            alarm = self.get(name)
            if alarm.cron:
                self.bot.remove_cron(alarm.cron)
        self.alarms = {}

    def SIGINT(self):  # pragma: no cover
        self.stop()

    def async_cron(self, name):
        asyncio.async(self.whois(name))

    @asyncio.coroutine
    def whois(self, name):
        alarm = self.get(name)
        self.log.info('alarm %s launched', name)
        if alarm.enable:
            nick = alarm.nick
            nicknames = [nick] + [nick + c for c in '`_']
            result = yield from self.bot.async_ison(*nicknames)
            self.log.info('ison %r', result)
            if 'nicknames' in result:
                nick = result['nicknames'][0]
                result = yield from self.bot.async_whois(nick)
                self.log.info('whois %r', result)
                idle = result.get('idle')
                if idle:
                    idle = int(idle) / 60
                    if idle > alarm.idle:
                        dest = alarm['target']
                        dest, _ = dest.split(':', 1)[0]
                        coro = getattr(self, 'do_%s' % dest)
                        yield from coro(alarm)

    @asyncio.coroutine
    def do_irc(self, alarm):  # pragma: no cover
        self.log.info('%r', alarm)
        self.bot.privmsg(alarm['nick'], u'Time to %(name)s!' % alarm)

    @asyncio.coroutine
    def do_sip(self, alarm):  # pragma: no cover
        self.log.info('%r', alarm)
        cmd = 'xvfb-run -n 39 xterm -e linphonec -s ' + alarm.target
        yield from asyncio.create_subprocess_exec(*cmd.split())
        yield from asyncio.sleep(20)
        yield from asyncio.create_subprocess_shell('pkill -9 -f "Xvfb :39"')

    @classmethod
    def reload(cls, old):
        old.stop()
        new = cls(old.bot)
        new.start()
        return new
