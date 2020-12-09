import shellpipe.notation
import shellpipe.tokenizer

# Convenient shorthands

'A convenient shorthand name for the ShellPipe class'
sh = notation.ShellPipe

'''Raised on failure.

PipeError's string representation is the stderr data from the failure.
PipeError.command shows the command that was run
'''
PipeError = notation.PipeError

'''Raised when parsing a string into command tokens fails.
'''
TokenError = tokenizer.TokenError



# Demo
if __name__ == "__main__":
    # Pipe several things, and print their output
    mypipe = sh(["echo", "-e", "n\\ne\\ng"]) | sh("sort -h") | sh("tac")
    print(mypipe.run())

    # Notice the external parens
    # .print() must be called on the entire "pipe" evaluation,
    # not just the end item.
    ( sh(["echo", "-e", "1\\n2\\n3"]) | sh("tac") ).print()

    # It's fine if it is just one thing though.
    sh('ls .').print()

    try:
        print(sh('ls a "b c"').run())
    except PipeError as e:
        print(e)

    # output should then be
    #
    #   n
    #   g
    #   e
    #
    #   3
    #   2
    #   1
