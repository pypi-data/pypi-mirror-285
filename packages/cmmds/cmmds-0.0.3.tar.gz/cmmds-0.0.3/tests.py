#!/usr/bin/env python

from typing import List, Mapping, Sequence
from cmds import Arguments, Command, CommandGroup
from dataclasses import dataclass


@dataclass
class CustomArgs(Arguments):
    a: int = 0
    b: int = 1
    c: str = 'apple'
    d: bool = True

    new_text: str = 'replaced'


class Cmd0(Command):
    def command(self) -> str | Sequence[str]:
        return f'echo {self.args.a}'


class Cmd1(Command):
    def command(self) -> str | Sequence[str]:
        return f'echo {self.args.d}'


class Cmd2(Command):
    def command(self) -> str | Sequence[str]:
        return 'echo $XXX'

    def update_env(self) -> Mapping[str, str] | None:
        return dict(XXX=self.args.new_text)


def test_single():
    arg = CustomArgs()
    cmd0 = Cmd0(arg)
    cmd0.run()
    print('print result:')
    print(cmd0)


def test_single_env_update():
    arg = CustomArgs()
    cmd2 = Cmd2(arg)
    cmd2.run()
    print('print result:')
    print(cmd2)


def test_group():
    arg = CustomArgs()
    group = CommandGroup(arg, [Cmd0, Cmd1, Cmd2])
    print('print group result:')
    print(group)
    group.run()


if __name__ == '__main__':
    # TODO: support recursive command Group
    # TODO: --help message for command group
    # test_single()
    # test_single_env_update()
    test_group()
