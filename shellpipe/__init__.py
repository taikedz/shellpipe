import shellpipe.notation
import shellpipe.tokenizer

# Convenient shorthands

'A convenient shorthand name for the ShellPipe class'
sh = notation.ShellPipe

'A generic error for ShellPipe'
ShellPipeError = notation.ShellPipeError

'''Raised on failure.

PipeError's string representation is the stderr data from the failure.
PipeError.command shows the command that was run
'''
PipeError = notation.PipeError

'''A specified command itself cannot be found.

Commands must be executables, not shell native commands'''
CommandNotFoundError = notation.CommandNotFoundError


'''Raised when parsing a string into command tokens fails.
'''
TokenError = tokenizer.TokenError
