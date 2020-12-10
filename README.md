# Shell Pipes in Python

This is a small project to allow using shell-like pipe notation inside python scripts.

Import the shellpipe notation, and write pipe-like syntax directly with strings.

## Examples

Provide commands as token lists or tuples, or as plain strings.

The pipe can simply be printed for its final stdout.

```python
from shellpipe import sh, PipeError

mypipe = sh(["echo", "-e", "a\\nb\\nc"]) | sh("tac")
print(mypipe)
```


You can use strings directly in a pipe chain. Sub-quoted strings can be used. A pseudo-redirect-out allows directly printing.

```python
sh() | 'git status' | 'grep -i "working tree clean"' > 1
```

Get stderr as an exception if a command in a chain returns non-zero:

```python
try:
    sh('ls non-existent-folder/') | sh("tee file_list.txt")

except PipeError as e:
    print("Failed command: {}".format(e.command))
    print("Error code: {}".format(e.returncode))

    print(e) # e, coerced to string, contains the output from stderr
```

Note that in the second command will not run, and the `file_list.txt` will not be created. You can specify to not throw an exception on failure, thus still running the rest of the commands in the pipe.

```python

# tee command will still run even if non-zero is returned

sh( "du -h file1 file2 file3", no_fail=True ) | "tee sizes.txt"

```


Get binary data output (don't judge this example... :-/) with `get_stdout()` and `get_stderr()`

```python
stuff = sh("cat binary-file").get_stdout()
```

Ensure we see `stderr` on console - some interactive interfaces do this

```python
import sys

rules = sh("sudo iptables -L", stderr=sys.stderr)
```

## Caveats

In true shell pipes, the processes are executed simultaneously, writing directly to file descriptors.

In this implementation, each earlier command is run til termination, and its `subprocess.Popen.stdout` descriptor is passed to the next item in the pipe chain - the data may or may not be held in momory.

If a command earlier in the chain returns a non-zero status, the other commands do not get called at all - though you can specify to not raise an exception on a specific job with the `no_fail` parameter.

This also means that it is likely heavily inefficient if:

* more than one step takes a long time to run
* any step generates a large amount of output

It is VERY unsuited for log monitoring, for example.

A multi-threaded version of this library would be needed to achieve the type of parallelism desired, and I have not yet gotten round to this.

## Local install

There is a script to install shellpipe to your local environment without interfering with other package managers. I am not submitting this to PyPI as of yet.

Simply run

```sh
bash local-install.sh && . "$HOME/.bashrc"
```

And you should be good to go.

## Thanks

This work was based off of [a comment by user `xtofl`](https://dev.to/xtofl/comment/14ihn) from my [dev.to blog](https://dev.to/taikedz), so props to them for the idea!

It essentially makes use of the conflation of the shell `|` pipe notation, Python's `|` bitwise `or` operator, and the fact that in Python, operators' behaviours can be self-defined per-class.

## License

(C) Tai Kedzierski, licensed under the terms of the GNU LGPLv3

Which generally means that you can link it in with proprietary code fine, but the library itself remains otherwise copyleft.
