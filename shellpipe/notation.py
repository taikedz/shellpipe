import subprocess
import re
import os

from shellpipe import tokenizer


class PipeError(OSError):
    """ Raised when a ShellPipe fails.

    Its string representation is the stderr output of the failure.

    Use PipeError.command to see what command was run.

    Use PipeError.returncode to find the return code of the failed command
    """
    def __init__(self, shellpipe, process):
        self.command = shellpipe.command_list
        self.returncode = process.returncode
        super().__init__(str(process.stderr.read(), 'utf-8'))


def _check_type(thing, target):
    """ Ensure a ShellPipe is being piped with another.
    """
    if not type(thing) is target:
        raise TypeError("Tried to pipe {} with a {}".format(target, type(thing)))


class ShellPipe:
    def __init__(self, command_list=None, stdin=None):
        self.command = None

        if type(command_list) is list:
            self.command = command_list

        elif type(command_list) is str:
            self.command = tokenizer.parse(command_list)

        elif command_list is None:
            pass

        else:
            raise TypeError("Cannot use {} as a command.".format(type()))

        self.stdin = stdin
        self.stdout = None
        self.stderr = None
        self.process = None

        if command_list:
            self.process = self()


    def __consume_channels(self):
        self.stdout,self.stderr = self.process.communicate()


    def __str__(self):
        if not self.stdout:
            self.__consume_channels()
        return str(self.stdout, os.getenv("PYTHONIOENCODING", 'utf-8'))


    def get_stderr(self):
        if not self.stderr:
            self.__consume_channels()
        return self.stderr


    def get_stdout(self):
        if not self.stdout:
            self.__consume_channels()
        return self.stdout


    def __or__(self, other):
        our_out = None
        if self.process:
            our_out = self.process.stdout

        if type(other) is str:
            other = ShellPipe(command_list=other, stdin=our_out)

        return other


    def __call__(self):
        if self.command is None:
            return None

        our_process = subprocess.Popen(self.command, stdin=self.stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        our_process.wait()

        if our_process.returncode > 0:
            raise PipeError(self, our_process)

        return our_process
