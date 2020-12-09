# Shell Pipes in Python

This is a small project to allow using shell-like pipe notation inside python scripts.

Import the shellpipe notation, and write pipe-like syntax:

```python
from shellpipe import sh, PipeError


# Provide commands as token lists or strings
# Get the result as a string from run()

mypipe = sh(["echo", "-e", "a\\nb\\nc"]) | sh("tac")
print(mypipe.run() )



# Run directly (wrap the pipe in parentheses '( ... )' to avoid mis-piping to a None object)
# Sub-quoted strings can be used.

( sh('git status') | sh('grep -i "working tree clean"') ).print()



# Get stderr as an exception

try:
    sh('ls non-existent-file').run()
except PipeError as e:
    print(e) # e, as a string, contains the output from stderr



# Get binary data output
#  (don't judge this example... :-/)
stuff = sh("cat binary-file", string=False).run()

# Not needed when piping
#  String conversion only happens to final output
(sh("cat binary") | sh("sha1sum")).print()

```

## Thanks

This work was based off of [a comment by user `xtofl`](https://dev.to/xtofl/comment/14ihn) from my [dev.to blog](https://dev.to/taikedz), so props to them for the idea!

It essentially makes use of the conflation of the shell `|` pipe notation, Python's `|` bitwise or comparator, and the fact that in Python, comparators' behaviours can be self-defined per-class.

## Observations

* The `sh(...) | sh(...)` build a pipe definition, but the specified commands are not actually run until `.run()` or `.print()` are called
* Any pipe defined will be run as-new when `run()` is called.

If you pipe two items together, the latter will retain a reference to the item prior to it. Note that you can pipe two commands together as a preparation without actually executing them, and confuse readers. Be responsible with this.

```sh
reverse = sh("tac")

ls = sh("ls")

# This firmly sets a relationship of "reverse" being
#   always downstream from the defined "ls"
ls | reverse

# This will just print directory stuff
ls.print()

# But this will in fact reverse the ls output, since the relationship has been set
reverse.print()

# You need to orphan it (forget its parent),
#   or re-pipe it to another parent.
reverse.orphan()
```

## Caveats

In true shell pipes, the processes are executed simultaneously, writing directly to file descriptors.

In this implementation, each earlier command is run til termination, and its `subprocess.Popen.stdout` descriptor is passed to the next item in the pipe chain.

This means that it is likely heavily inefficient if:

* more than one step takes a long time to run
* any step generates a large amount of output

It is VERY unsuited for log monitoring, for example.

A multi-threaded version of this library would be needed to achieve the type of parallelism desired, and I have not yet gotten round to this.

## License

(C) Tai Kedzierski, licensed under the terms of the GNU LGPLv3

Which generally means that you can link it in with proprietary code fine, but the library itself remains otherwise copyleft.
