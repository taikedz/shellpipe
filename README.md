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


You can use strings directly in a pipe chain. Sub-quoted strings can be used.

```python
print(  sh() | 'git status' | 'grep -i "working tree clean"'  )
```

Get stderr as an exception

```python
try:
    sh('ls non-existent-file')

except PipeError as e:
    print("Failed command: {}".format(e.command))
    print("Error code: {}".format(e.returncode))

    print(e) # e, coerced to string, contains the output from stderr
```


Get binary data output (don't judge this example... :-/) with `get_stdout()` and `get_stderr()`

```python
stuff = sh("cat binary-file").get_stdout()
```

## Caveats

In true shell pipes, the processes are executed simultaneously, writing directly to file descriptors.

In this implementation, each earlier command is run til termination, and its `subprocess.Popen.stdout` descriptor is passed to the next item in the pipe chain - the data may or may not be held in momory.

This means that it is likely heavily inefficient if:

* more than one step takes a long time to run
* any step generates a large amount of output

It is VERY unsuited for log monitoring, for example.

A multi-threaded version of this library would be needed to achieve the type of parallelism desired, and I have not yet gotten round to this.

## Thanks

This work was based off of [a comment by user `xtofl`](https://dev.to/xtofl/comment/14ihn) from my [dev.to blog](https://dev.to/taikedz), so props to them for the idea!

It essentially makes use of the conflation of the shell `|` pipe notation, Python's `|` bitwise `or` operator, and the fact that in Python, operators' behaviours can be self-defined per-class.

## License

(C) Tai Kedzierski, licensed under the terms of the GNU LGPLv3

Which generally means that you can link it in with proprietary code fine, but the library itself remains otherwise copyleft.
