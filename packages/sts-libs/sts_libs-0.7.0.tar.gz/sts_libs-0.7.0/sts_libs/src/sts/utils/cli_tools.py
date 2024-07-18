"""cli_tools.py: Module to provide tools of wrapping command line tools for further usage."""

#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import annotations

import logging


class WrongCommandExceptionError(Exception):
    def __init__(self, cmd) -> None:  # noqa: ANN001
        self.command = cmd
        super().__init__()

    def __str__(self) -> str:
        return repr(WrongCommandExceptionError.__name__ + ', caused by ' + repr(self.command))


class WrongArgumentExceptionError(Exception):
    def __init__(self, arg, cmd=None, args=None) -> None:  # noqa: ANN001
        self.argument = arg
        self.command = cmd
        self.arguments = args
        super().__init__()

    def __str__(self) -> str:
        return repr(WrongArgumentExceptionError.__name__ + ', caused by ' + repr(self.argument))


class FailedCheckExceptionError(Exception):
    def __init__(self, arg=None) -> None:  # noqa: ANN001
        self.argument = arg
        super().__init__()

    def __str__(self) -> str:
        message = repr(FailedCheckExceptionError.__name__)
        if self.argument:
            message += ', caused by ' + repr(self.argument)
        return message


class Wrapper:
    def __init__(self, commands, arguments, disable_check) -> None:  # noqa: ANN001
        self.commands = commands
        self.arguments = arguments
        self.disable_check = disable_check

    def _add_command(self, cmd):  # noqa: ANN001, ANN202
        # Checks if given command is provided by CLI and returns its correct syntax
        if cmd in self.commands:
            return self.commands[cmd]
        raise WrongCommandExceptionError(cmd)

    def _get_arg(self, name):  # noqa: ANN001, ANN202
        if not self.disable_check:
            if name in self.arguments:
                return self.arguments[name][1]
            raise WrongArgumentExceptionError(name)
        return self.arguments[name][1]

    def _get_cmd(self, name):  # noqa: ANN001, ANN202
        if self.disable_check:
            return self.commands['all']
        if name in self.arguments:
            return self.arguments[name][0]
        raise WrongCommandExceptionError(name)

    @staticmethod
    def _get_value(string, command, return_type=str):  # noqa: ANN001, ANN205
        _value = string.split(command)[1].split()[0]
        try:
            value = return_type(_value)
        except ValueError as e:
            logging.warning(f'Got ValueError: {e}.')
            return None
        return value

    def _get_possible_arguments(self, command: str | None = None) -> list[str]:
        # Returns possible arguments for the specified command if provided
        if command:
            args = [key for key in self.arguments if self._get_cmd(key) == command]
        else:
            args = list(self.arguments.keys())
        return args

    @staticmethod
    def _add_value(value, command, argument):  # noqa: ANN001, ANN205
        if argument[-1:] in {'=', '&'}:
            if argument[-1:] == '&':
                argument = argument[:-1] + ' '
            if isinstance(value, list):
                # allows to use repeatable arguments as a list of values
                for val in value:
                    command += argument + "'" + str(val) + "'"
            else:
                command += argument + "'" + str(value) + "'"
        else:
            command += argument
        return command

    def _check_allowed_argument(self, arg, command):  # noqa: ANN001, ANN202
        if arg not in self.arguments and not self.disable_check:
            raise WrongArgumentExceptionError(arg)
        cmd = command.split()[0]
        args = self._get_possible_arguments(cmd)
        if arg not in args:
            raise WrongArgumentExceptionError(arg, cmd, args)

    def _add_argument(self, arg, value, command):  # noqa: ANN001, ANN202
        # Checks if given argument is allowed for given command and adds it to cmd string
        self._check_allowed_argument(arg, command)
        return self._add_value(value, command, self._get_arg(arg))

    def _add_arguments(self, cmd, **kwargs):  # noqa: ANN001, ANN003, ANN202
        command = cmd
        for kwarg in kwargs:
            # skip adding this argument if the value is False
            if kwargs[kwarg] is False:
                continue
            command = self._add_argument(kwarg, kwargs[kwarg], command)
        return command
