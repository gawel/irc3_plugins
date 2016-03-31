# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from irc3.plugins.command import command
from irc3.compat import asyncio
from collections import defaultdict
from .manager import get_manager
import logging
import irc3
__doc__ = '''
Asterisk plugin using panoramisk https://github.com/gawel/panoramisk
'''


class default_resolver(object):
    """A really simple resolver to show how you must handle accounts and phone
    numbers"""

    db = dict(
        lukhas=dict(login='lukhas',
                    fullname='Lucas Bonnet',
                    channel='SIP/lukhas',
                    exten='lukhas',
                    context='default'),
        gawel=dict(login='gawel',
                   fullname='Gael Pasgrimaud',
                   channel='SIP/gawel',
                   exten='gawel',
                   context='default'))

    def __init__(self, bot):
        self.bot = bot

    def __call__(self, mask, value):
        if value.isdigit():
            return dict(
                exten=value,
                channel='IAX2/your-provider/' + value,
                fullname='External Call ' + value,
                context='default')
        else:
            return self.db.get(value)


def lower_header_keys(obj):
    values = list(obj.items())
    for k, v in values:
        obj[k.lower()] = v


@irc3.plugin
class Asterisk(object):

    requires = ['irc3.plugins.command']

    def __init__(self, bot):
        self.bot = bot
        self.bot.asterisk = self
        self.config = config = dict(
            host='127.0.0.1',
            port=5038,
            debug=True,
        )
        config.update(bot.config.get('asterisk', {}))
        self.log = logging.getLogger('irc3.ast')
        self.ilog = logging.getLogger('irc.asterirc')
        self.ilog.set_irc_targets(bot, self.config['channel'])
        self.log.info('Channel is set to {channel}'.format(**config))
        self.rooms = defaultdict(dict)
        self.resolver = irc3.utils.maybedotted(self.config['resolver'])
        self.manager = get_manager(log=self.log, **config)
        self.manager.register_event('Shutdown', self.handle_shutdown)
        self.manager.register_event('Meet*', self.handle_meetme)
        if isinstance(self.resolver, type):
            self.resolver = self.resolver(bot)
        self.manager.connect()

    def connection_made(self):
        self.bot.loop.call_later(1, self.connect)

    def post_connect(self, future):
        self.log.warn('post_connect')
        self.bot.create_task(self.update_meetme())

    @asyncio.coroutine
    def update_meetme(self):
        resp = yield from self.send_command('meetme list')
        self.log.warn('update_meetme %r', resp)
        if 'No active MeetMe conferences.' in resp.text:
            self.rooms = defaultdict(dict)
        for line in list(resp.iter_lines())[1:-2]:
            room = line.split(' ', 1)[0]
            if not room or not room.isdigit():
                continue

            resp = yield from self.send_command('meetme list ' + room)
            room = self.rooms[room]
            for line in resp.iter_lines():
                if not line.startswith('User '):
                    continue
                line = line.split('Channel:')[0]
                splited = [s for s in line.split() if s][2:]
                uid = splited.pop(0)
                caller = ' '.join(splited[1:])
                if 'external call ' in caller.lower():
                    e, c, n = caller.split(' ')[:4]
                    caller = ' '.join([e, c, n[:6]])
                room[caller] = uid

    def connect(self):
        if self.manager is not None:
            self.manager.close()
        try:
            self.manager.connect().add_done_callback(self.post_connect)
        except Exception as e:
            self.log.exception(e)
            self.log.info('connect retry in 5s')
            self.bot.loop.call_later(1, self.connect)
            return False
        else:
            return True

    def handle_shutdown(self, manager, event):
        self.manager.close()
        self.bot.loop.call_later(2, self.connect)

    def handle_meetme(self, manager,  event):
        self.log.warn('handle_meetme %r', event)
        name = event.event.lower()
        room = event.meetme

        if name == 'meetmeend':
            if room in self.rooms:  # pragma: no cover
                del self.rooms[room]
            self.ilog.info('room {} is closed.'.format(room))
            return

        action = None
        caller = event.calleridname
        if 'external call ' in caller.lower():
            e, c, n = caller.split(' ')[:4]
            caller = ' '.join([e, c, n[:6]])
        elif 'external call' in caller.lower():  # pragma: no cover
            caller += event.calleridnum[:6]

        if 'join' in name:
            action = 'join'
            self.rooms[room][caller] = event.usernum
        elif 'leave' in name:
            action = 'leave'
            if caller in self.rooms.get(room, []):
                del self.rooms[room][caller]

        if action:
            # log
            args = dict(caller=caller, action=action,
                        room=room, total=len(self.rooms[room]))
            self.ilog.info((
                '{caller} has {action} room {room} '
                '(total in this room: {total})').format(**args))

    def send_action(self, *args, **kwargs):
        return self.manager.send_action(*args, **kwargs)

    def send_command(self, command):
        return self.manager.send_command(command)

    def reply(self, mask, target, message):
        nick = self.bot.nick or '-'
        to = target == nick and mask.nick or target
        self.bot.privmsg(to, message)

    @command(permission='voip')
    @asyncio.coroutine
    def call(self, mask, target, args, message=None):
        """Call someone. Destination and from can't contains spaces.

            %%call <destination> [<from>]

        """
        if 'nick' not in args:
            args['nick'] = mask.nick

        callee = self.resolver(mask, args['<destination>'])
        if args['<from>']:
            caller = self.resolver(mask, args['<from>'])
        else:
            caller = self.resolver(mask, mask.nick)

        if caller is None or caller.get('channel') is None:
            return '{nick}: Your caller is invalid.'.format(**args)
        if callee is None or callee.get('exten') is None:
            return '{nick}: Your destination is invalid.'.format(**args)

        action = {
            'Action': 'Originate',
            'Channel': caller['channel'],
            'WaitTime': 20,
            'CallerID': caller.get('fullname', caller['channel']),
            'Exten': callee['exten'],
            'Context': caller.get('context', 'default'),
            'Priority': 1,
            'Async': True,
        }

        if message is None:
            message = '{nick}: Call to {<destination>} done.'.format(**args)

        resp = yield from self.send_action(action)
        print(resp)
        if isinstance(resp, list):
            resp = resp[-1]
        if not resp.success:
            msg = resp.text
        else:
            msg = message
        self.reply(mask, target, msg)

    @command(permission='voip')
    @asyncio.coroutine
    def room(self, mask, target, args):
        """Invite/kick someone in a room. You can use more than one
        destination. Destinations can't contains spaces.

            %%room (list|invite|kick) [<room>] [<destination>...]

        """
        args['nick'] = mask.nick
        room = args['<room>']
        if args['invite']:

            callees = args['<destination>']
            message = '{nick}: {<from>} has been invited to room {<room>}.'
            if not callees:
                # self invite
                callees = [mask.nick]
                message = '{nick}: You have been invited to room {<room>}.'

            resolved = [self.resolver(mask, c) for c in callees]
            if None in resolved:
                # show invalid arguments and quit
                callees = zip(resolved, callees)
                invalid = [c for r, c in callees if r is None]
                return (
                    "{0}: I'm not able to resolve {1}. Please fix it!"
                ).format(mask.nick, ', '.join(invalid))

            for callee in callees:
                # call each
                args['<destination>'] = args['<room>']
                args['<from>'] = callee
                yield from self.call(mask, target, args,
                                     message=message.format(**args))

        if room and room not in self.rooms:
            return 'Invalid room'

        messages = []

        if args['list']:
            def fmt(room, users):
                amount = len(users)
                users = ', '.join([u for u in sorted(users)])
                return 'Room {0} ({1}): {2}'.format(room, amount, users)

            if room:
                messages.append(fmt(room, self.rooms[room]))
            elif self.rooms:
                for room, users in self.rooms.items():
                    messages.append(fmt(room, self.rooms[room]))
            else:
                return 'Nobody here.'

        elif args['kick']:
            users = self.rooms[room]
            commands = []
            for victim in args['<destination>']:
                for user in users:
                    if victim.lower() in user.lower():
                        peer = users[user]
                        commands.append((
                            user,
                            'meetme kick {0} {1}'.format(room, peer)))

            if not commands:
                return 'No user matching query'

            for user, cmd in commands:
                resp = yield from self.send_command(cmd)
                if resp.success:
                    del self.rooms[room][user]
                    if not self.rooms[room]:
                        del self.rooms[room]
                    messages.append(
                        '{0} kicked from {1}.'.format(user, room))
                else:  # pragma: no cover
                    messages.append(
                        'Failed to kick {0} from {1}.'.format(user, room))
        return messages

    @command(permission='voip')
    @asyncio.coroutine
    def asterisk(self, mask, target, args):
        """Show voip status

            %%asterisk status [<id>]
        """
        self.log.info('voip %s %s %s', mask, target, args)
        args['nick'] = mask.nick
        if args['<id>']:
            peer = self.resolver(mask.nick, args['<id>'])
        else:
            peer = self.resolver(mask, mask.nick)
        if peer is None:
            return '{nick}: Your id is invalid.'.format(**args)
        action = {'Action': 'SIPshowpeer', 'peer': peer['login']}

        resp = yield from self.send_action(action)
        if resp.success:
            self.reply(
                mask, target,
                ('{nick}: Your VoIP phone is registered. '
                 '(User Agent: {sip-useragent} on {address-ip})'
                 ).format(nick=mask.nick,
                          **dict([(k.lower(), v)
                                 for k, v in resp.items()])))

    @command(permission='admin', venusian_category='irc3.debug')
    @asyncio.coroutine
    def asterisk_command(self, mask, target, args):  # pragma: no cover
        """Send a raw command to asterisk. Use "help" to list core commands.

            %%asterisk_command <command>...
        """
        cmd = ' '.join(args['<command>'])
        cmd = dict(
            help='core show help',
        ).get(cmd, cmd)
        yield from self.send_command(cmd, debug=True)
        return 'Sent'

    def SIGINT(self):
        if self.manager is not None:
            self.manager.close()
        self.log.info('SIGINT: connection closed')
