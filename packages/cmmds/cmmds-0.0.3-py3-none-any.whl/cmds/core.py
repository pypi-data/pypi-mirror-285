from typing import Literal, Generic, TypeVar, Optional, Any, Sequence, List, Mapping, Type
from argparse import ArgumentParser
from subprocess import run
from dataclasses import dataclass, fields
from sys import stderr, stdout
from pprint import pprint
import re
from itertools import chain
import sys
import os


# TODO: help message for both args and command
# TODO: helper function quickly create simple command, args, etc.
# Use genertics to limit command class's args class
# TODO: support literal args

@dataclass
class Arguments:
    range: str = ''

    def __post_init__(self):
        parser = ArgumentParser()
        for k in fields(self):
            k = k.name
            v = getattr(self, k)
            if k == 'range':    # TODO: handle literal class
                parser.add_argument(f'range', default=v, type=type(v))
            elif isinstance(v, bool):
                parser.add_argument(f'--{k}', default=int(v), type=int)
            else:
                parser.add_argument(f'--{k}', default=v, type=type(v))
        args = parser.parse_args()
        for k, v in args._get_kwargs():
            setattr(self, k, v)
        self.verify_range()

    def verify_range(self) -> bool:
        if self.range:
            single_range_pattern = '\d+(:\d+(:\d+)?)?'
            pattern = f'({single_range_pattern},)*{single_range_pattern},?'
            ret = re.match(pattern, self.range)
            if not ret:
                print("Invalid range! No steps run.", file=sys.stderr)
                return False
            return True
        else:
            return False

    @property
    def steps(self):
        if self.verify_range():
            ret = []
            for r in self.range.split(','):
                slce = r.split(':')
                slce = tuple(map(int, slce))
                if len(slce) == 1:
                    ret.append(range(slce[0], slce[0] + 1))
                else:
                    ret.append(range(*slce))
            return chain(*ret)
        else:
            return ()


# TODO: use abstract base class
@dataclass
class Command:
    args: Arguments

    def command(self) -> str | Sequence[str]:
        raise NotImplemented

    def env(self) -> Mapping[str, str] | None:
        """Override parent process's env vars."""
        return None

    def update_env(self) -> Mapping[str, str] | None:
        """Update parent process's env vars."""
        return None

    def run(self):
        if self.command():
            env_diff = self.update_env()
            new_env = self.env()
            assert not (env_diff and new_env), 'You can only implement one of `env` and `update_env`!'
            if env_diff:
                new_env = os.environ.copy()
                new_env.update(env_diff)
            cmd = self.command()
            cmd = ' '.join(cmd) if isinstance(cmd, list) else cmd
            print('+ ' + cmd)
            run(cmd, shell='bash', stdout=stdout, stderr=stderr, check=True, env=new_env)

    run_all = run

    def __repr__(self) -> str:
        if isinstance(self.command(), (tuple, list)):
            return '; '.join(self.command())
        else:
            return self.command()


# TODO: --help message for command group
@dataclass
class CommandGroup(Command):
    commands: Sequence[Type[Command]]

    def __post_init__(self):
        self._cmd_instances = [c(self.args) for c in self.commands]

    def run_all(self):
        for cmd in self._cmd_instances:
            cmd.run_all()

    def run(self):
        for i in self.args.steps:
            cmd = self._cmd_instances[i]
            cmd.run_all()

    def __repr__(self) -> str:
        ret = type(self).__name__ + ':\n  '
        ret += '\n  '.join(f'{i} {type(cmd).__name__}:  {cmd}' for i, cmd in enumerate(self._cmd_instances))
        ret += '\n'
        return ret


    def __str__(self) -> str:
        ret = type(self).__name__ + ':\n  '
        ret += '\n  '.join(f'{i} {type(cmd).__name__}' for i, cmd in enumerate(self._cmd_instances))
        ret += '\n'
        return ret

