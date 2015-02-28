=====================
Alarm plugin for irc3
=====================

Context
=======

I'm a remote developer working at home.

Since most of my workmates work remotely irc and voip are some of our
tools to communicate.

A few months ago I moved from Paris to a sweet place near the sea. And I threw
away lot of things before leaving. Including alarms clocks.

Then I started the irc3 project and decided to use it as an alarm.

I talked about that at @PyconFr 2014 and promised to release this code on day.
This day finally happened.

How it works
============

As usual with irc3 commands, you can get some help by using::

    !help alarm

You can set an alarm using the `!alarm set` command::

    #       <alarm name>   <sip account>       <crontab>     <idle>
    !alarm set matin sip:you@your.provid.er 0,10,15 9 * * 1-5 180

Then, when the crontad is due, the bot will whois you and get your idle time.
If it's >180mn then the bot will ring your phone using the sip account
provided.

This mean that if you wake up before the cron is due and say «matin» on irc
then alarm will not ring at all. Isn't that great ?

Requirements
============


You'll need to install:

- aiocron

- xvfb-run

- xterm

- linephonec


You'll also have to configure linephonec so it can be launched using::

    $ linephone -s sip:you@your.provid.er

Configuration
=============

Your irc3 config file must have the following::

    [bot]

    includes =
        irc3_plugins.alarm

    storage = json:///your.storage.file.json

Support
=======

You can find me on #irc3@freenode if you have question
