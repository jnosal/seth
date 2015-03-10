#!/usr/bin/env python


from seth import command
from super_command import SuperCommand


if __name__ == '__main__':
    command.run_command(commands=[
        SuperCommand
    ])