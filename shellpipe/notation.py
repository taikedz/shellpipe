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


def _check_iterable(item_list):
    for item in item_list:
        if type(item) is not str:
            raise TypeError("{} contains non-str item".format(item_list))


class ShellPipe:
    def __init__(self, command_list=None, stdin=None):
        """ Provide a command token list to execute in a shell.

        @param command_list - the string tokens of a single command

        @param stdin - the stream from another shell. Internal.
        """
        self.command = None
        self.process = None
        self.stdout = None
        self.stderr = None
        self.stdin = stdin

        if type(command_list) in (list,tuple):
            _check_iterable(command_list)
            self.command = command_list

        elif type(command_list) is str:
            self.command = tokenizer.parse(command_list)

        elif command_list is None:
            pass

        else:
            raise TypeError("Cannot use {} as a command.".format(type()))

        if command_list:
            self.__process()


    def __consume_channels(self):
        self.stdout,self.stderr = self.process.communicate()


    def __str__(self):
        if not self.stdout:
            self.__consume_channels()
        return str(self.stdout, os.getenv("PYTHONIOENCODING", 'utf-8'))


    def get_stderr(self):
        """ Get the raw bytes from the stderr channel.
        """
        if not self.stderr:
            self.__consume_channels()
        return self.stderr


    def get_stdout(self):
        """ Get the raw bytes from the stdout channel.
        """
        if not self.stdout:
            self.__consume_channels()
        return self.stdout


    def __or__(self, other):
        """ Magic sauce to redefine the Python bitwise OR operator as a pipe
        """

        """ In a bitwise OR operation, the __or__() method of the Left Hand Side object is
        called with single argument the Right Hand Side object, and returns a result.

        If multiple bitwise OR operations are chained, the result of the comparison
        of the two becomes the new LHS for the third item.

        This implementation converts the RHS object into a ShellPipe and returns it, hence
        the need for an initial `sh()`, and the ability to thereafter use
        str, list or tuple.
        """
        our_out = None
        if self.process:
            our_out = self.process.stdout

        if type(other) in (str,list,tuple):
            other = ShellPipe(command_list=other, stdin=our_out)

        return other


    def __process(self):
        """ Actually execute the command.
        """
        if self.command is None:
            return None

        our_process = subprocess.Popen(self.command, stdin=self.stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        our_process.wait()

        if our_process.returncode > 0:
            raise PipeError(self, our_process)

        self.process = our_process
