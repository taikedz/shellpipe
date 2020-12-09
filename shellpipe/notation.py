import subprocess
import re
import os

from shellpipe import tokenizer

class ChannelError(Exception):
    pass


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


def _check_type(thing):
    """ Ensure a ShellPipe is being piped with another.
    """
    if not type(thing) is ShellPipe:
        raise TypeError("Tried to pipe ShellPipe with a {}".format(type(thing)))


class ShellPipe:

    def __init__(self, command_list, **kwargs):
        """ Provide command_list as a list of string tokens, or as a single string that will be tokenized.

        **kwargs are keyword-based arguments that are directly passed to subprocess.Popen(...)
        """
        self.parent = None

        for channel in ["stdout", "stderr"]:
            setattr(self, channel, kwargs.get(channel))
            if getattr(self, channel):
                del kwargs[channel]

        self.process_args = kwargs

        if type(command_list) is str:
            command_list = tokenizer.parse(command_list)

        elif type(command_list) is not list:
            raise TypeError("ShellPipe command should be a single string or a list of strings.")

        self.command_list = command_list


    def _set_parent(self, parent_pipe):
        """ Set a parent pipe. Internal."""
        self.parent = parent_pipe


    def orphan(self):
        """ Forget the parent pipe.

        Returns the parent pipe that was removed.
        """
        parent = self.parent
        self.parent = None
        return parent


    def run(self, channel="stdout", string=True):
        """ Run a pipe chain, and return the output.

        By default, returns the stdout stream.

        Set channel="stderr" for the stderr stream instead.

        Set string=False to get the raw binary data instead of a converted string.
        """
        if channel not in ('stdout','stderr'):
            raise ChannelError("Invalid channel: {}. Must be 'stdout' or 'stderr'.".format(channel))

        subp = self()

        result = getattr(subp, channel).read()

        if string:
            result = str(result, os.getenv("PYTHONIOENCODING", 'utf-8'))

        return result


    def print(self, *args, **kwargs):
        """ Run the pipe chain and print its stdout

        All extra arguments passed directly to the native print(...) function.
        """
        print(self.run(), *args, **kwargs)


    def __call__(self, stdin=None):
        """ ShellPipe is callable.

        This will call the prior item in the chain that it was defined from, before calling itself.
        """
        if self.parent:
            _check_type(self.parent)
            # Parent must run first, call it, and get its context
            parent_process = self.parent(stdin)
            parent_out = parent_process.stdout
        else:
            parent_out = None

        # Call ourselves passing parent's out to our in
        our_process = subprocess.Popen(self.command_list, stdin=parent_out, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **self.process_args)
        our_process.wait() # Wait for it to terminate, for returncode

        if our_process.returncode > 0:
            raise PipeError(self, our_process)

        return our_process

    
    def __or__(self, other):
        """ Secret sauce allowing us to "ShellPipe() | ShellPipe()"
        """
        _check_type(other)

        other._set_parent(self)
        return other


    def __str__(self):
        return str(self.command_list)

