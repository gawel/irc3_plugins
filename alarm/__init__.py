# -*- coding: utf-8 -*-
from functools import partial

import irc3
from irc3.plugins.command import command

from chut import timeout
from chut import path
from chut import pkill
from chut import env

env.home = path('~/')


class Item(dict):

    @classmethod
    def from_args(cls, nick, args):
        idle = args['<idle>'] or 180
        data = dict(
            name=args['<name>'],
            nick=nick,
            idle=int(idle),
            sip=args['<sip>'],
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
            sip=self.sip,
            idle=self.idle,
            crontab=self.crontab)

    def __str__(self):
        return '%(name)s: sip:%(sip)s crontab:%(crontab)s' % self


@irc3.plugin
class Alarm(object):

    requires = ['irc3.plugins.command',
                'irc3.plugins.storage',
                'irc3.plugins.cron']

    def __init__(self, bot):
        self.bot = bot
        self.log = bot.log
        self.key = __name__ + '.alarms'
        self.alarms = {}

    def connection_made(self):
        self.start()

    @command(permission='admin')
    def alarm(self, mask=None, target=None, args=None):
        """Alarm

            %%alarm list
            %%alarm (toogle|delete|test) <name>
            %%alarm set <name> <sip> <mn> <h> <dom> <m> <dow> [<idle>]
        """
        db = self.bot.db
        alarms = db[self.key]

        name = args.get('<name>')
        if args.get('list'):
            for name in sorted(self.alarms):
                yield str(self.get_alarm(name))
        elif args.get('set'):
            if name in self.alarms:
                self.delete(name)
            item = Item.from_args(mask.nick, args)
            db['%s.%s' % (self.key, name)] = item.data
            alarms[name] = True
            db[self.key] = alarms
            yield str(self.get_alarm(name))
        elif args.get('toogle'):
            alarms[name] = not bool(alarms[name])
            db[self.key] = alarms
            yield 'alarm %s is %s' % (name, alarms[name] and 'on' or 'off')
        elif args.get('delete'):
            self.delete(name)
            yield 'alarm %s deleted' % name
        elif args.get('test'):
            self.ring(self.get_alarm(name))
            yield 'test for alarm %s sent' % name

    def get_alarm(self, name):
        if name not in self.alarms:
            alarm = self.bot.db['%s.%s' % (self.key, name)]
            if not alarm:
                raise LookupError(name)
            alarm = self.alarms[name] = Item(alarm)
            event = irc3.event(
                r':\S+ 317 \S+ %(nick)s (?P<idle>[0-9]+) .*' % alarm,
                partial(self.rpl_whois_idle, name))
            self.bot.attach_events(event)
            c = self.bot.add_cron(alarm.crontab,
                                  partial(self.whois, name))
            alarm.update(event=event, cron=c)
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
            self.get_alarm(name)

    def stop(self):
        for name in self.bot.db[self.key]:
            alarm = self.get_alarm(name)
            if alarm.cron:
                self.bot.remove_cron(alarm.cron)
            if alarm.event:
                self.bot.detach_events(alarm.event)
            if alarm.handle:  # pragma: no cover
                alarm.handle.cancel()
        self.alarms = {}

    def SIGINT(self):  # pragma: no cover
        self.stop()

    def whois(self, name):
        alarm = self.get_alarm(name)
        alarm['handle'] = self.bot.loop.call_later(60, self.bot.SIGINT)
        self.bot.send('WHOIS {nick} {nick}'.format(**alarm))

    def rpl_whois_idle(self, name, nick=None, idle=None):
        alarm = self.get_alarm(name)
        if nick == alarm.nick:
            if alarm.handle:  # pragma: no cover
                alarm.pop('handle').cancel()
            if alarm.enable:
                idle = int(idle) / 60
                if idle > alarm.idle:
                    self.ring(alarm)

    def ring(self, alarm):  # pragma: no cover
        self.log.info('Wakeup call (%s)', alarm.name)
        pkill('-u {USER} -9 Xvfb'.format(**env))()
        timeout('-k 15 15 xvfb-run xterm -e linphonec -s',
                '{sip}'.format(**alarm)).bg()
