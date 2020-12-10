import subprocess
import sys
import re
import os

from shellpipe import tokenizer

class ShellPipeError(Exception):
    pass


class CommandNotFoundError(FileNotFoundError):
    pass


class PipeError(OSError):
    """ Raised when a ShellPipe fails.

    Its string representation is the stderr output of the failure.

    Use PipeError.command to see what command was run.

    Use PipeError.returncode to find the return code of the failed command
    """
    def __init__(self, shellpipe, process):
        self.command = shellpipe.command
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


def to_str(bytes_data):
    return str(bytes_data, os.getenv("PYTHONIOENCODING", 'utf-8'))


class ShellPipe:
    def __init__(self, command_list=None, no_fail=False, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE):
        """ Provide a command token list to execute in a shell.

        @param command_list - the string tokens of a single command as a list, or a command as a string

        @param no_fail - whether or not to throw an exception if the return code is non-zero

        @param stdin - a file stream that will be fed to the comamnd's stdin

        @param stdout - the output stream that will connect to the command's stdout

        @param stderr - the output stream that will connect to the comamnd's stderr
        """
        self.command = None
        self.process = None
        self.no_fail = no_fail

        self.stdout = stdout
        self.stderr = stderr
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


    def __str__(self):
        return to_str(self.process.stdout.read())


    def get_stderr(self):
        """ Get the raw bytes from the stderr channel.
        """
        return self.process.stderr


    def get_stdout(self):
        """ Get the raw bytes from the stdout channel.
        """
        return self.process.stdout


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

        else:
            raise TypeError("Shell pipe: pipe: RHS must be string, list, tuple, or ShellPipe, but found {}".format(other))

        return other


    def __gt__(self, other):
        """You can redirect a ShellPipe's stdout to either sys.stdout or sys.stderr by using

        sh("command") > 1
        sh("command") > 2
        """
        if self.process:
            stream = self.process.stdout
            self.__write_out(other, stream)
        else:
            raise ShellPipeError("Redirect error: No process.")

        return self


    def __xor__(self, other):
        """You can redirect a ShellPipe's stderr to either sys.stdout or sys.stderr by using

        Note that if you are using multiple pipes, you MUST unify them in parentheses because '^' has precedence over '|'.

        (sh("cmd1") | "cmd2") ^ 2
        (sh("cmd1") | "cmd2") ^ 1
        """
        if self.process:
            stream = self.process.stderr
            self.__write_out(other, stream)
        else:
            raise ShellPipeError("Redirect error: No process.")

        return self



    def __write_out(self, other, stream):
        if other == 1:
            sys.stdout.write(to_str(stream.read()))

        elif other == 2:
            sys.stderr.write(to_str(stream.read()))

        else:
            raise TypeError("Shell pipe: write-out: RHS must be 1 to write to stdout or 2 to write to stderr")


    def __process(self):
        """ Actually execute the command.
        """
        if self.command is None:
            return None

        try:
            our_process = subprocess.Popen(self.command, stdin=self.stdin, stdout=self.stdout, stderr=self.stderr)
            our_process.wait()
        except FileNotFoundError as e:
            raise CommandNotFoundError(e)

        if not self.no_fail and our_process.returncode > 0:
            raise PipeError(self, our_process)

        self.process = our_process
