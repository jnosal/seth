import sys
import argparse

from pyramid.paster import bootstrap


class Command(object):

    args = tuple()
    name = None

    def __init__(self, runner):
        self.runner = runner
        self.env = runner.bootstrap_application()
        self.settings = self.env['registry'].settings

    def run(self):
        raise NotImplementedError()


class CommandManager(object):

    def __init__(self, ini_file):
        self.ini_file = ini_file
        self.commands = {}

    def register_command(self, Cmd):
        if not Cmd.name:
            Cmd.name = Cmd.__name__.lower()

        if Cmd.name in self.commands:
            raise TypeError(u"Command already registered")

        self.commands[Cmd.name] = Cmd

    def bootstrap_application(self):
        return bootstrap(self.ini_file)

    def run(self, command, testing=False):
        if command not in self.commands:
            print u"No command found: {0}".format(command)
            return

        Cmd = self.commands[command]
        if not testing:
            args = self.parse_args(Cmd)
            Cmd(self).run(**vars(args))
        else:
            Cmd(self).run()

    def parse_args(self, command):
        parser = argparse.ArgumentParser(command.name)

        for a in command.args:
            if isinstance(a[0], (list, tuple)):
                names = a[0]
            else:
                names = (a[0],)
            parser.add_argument(*names, **a[1])

        return parser.parse_args(sys.argv[3:])