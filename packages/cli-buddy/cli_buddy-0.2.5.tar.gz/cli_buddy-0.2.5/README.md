
# The fastest, simplest way to create a CLI in Python

`cli-buddy` provides an ergonomic syntax for creating command-line interfaces in Python.

### With `cli-buddy`, 👇 this code snippet is all it takes to build a CLI.

```python
from cli_buddy import CLI

class MyCLI(CLI):
    arg: str
```

Under the hood, `cli-buddy` is a pydantic-flavored wrapper around the built-in `argparse` module.


## Requirements
* Python 3.11+

## Install

```bash
pip install cli-buddy
```

## Usage

### Use the `CLI` class to define your CLI's arguments and options.


This code snippet...

```python
# main.py
from cli_buddy import CLI

class TerminalTimer(CLI):
    seconds: int
    # boolean fields are automatically converted to flags
    show_time: bool
```

... will produce the following CLI:

```bash
$ python main.py --help
usage: main.py [-h] seconds

positional arguments:
  seconds

options:
  -h, --help  show this help message and exit
  --show_time
```

A CLI class alone won't run anything, obviously. We need to define our behavior first.

### Define your CLI's behavior

#### Either use your CLI instance however you like...


```python

# main.py
...

cli = TerminalTimer()

for _ in range(cli.seconds):
    print(_)
    time.sleep(1)
```

#### ... or just put your logic within the `__call__()` method of your CLI class...


```python
class TerminalTimer(CLI):
    seconds: int
    show_time: bool

    def __call__(self):
        for _ in range(self.seconds):
            print(_)
            time.sleep(1)

TerminalTimer()  # That's it!
```

### Give your arguments default values to convert arguments to flags.

The `CLI` class will automatically convert arguments to flags if:
* they are assigned a default value,
* *or if the field is a boolean*.

For example, this...
```python
class TerminalTimer(CLI):
    seconds: int = 1
    show_time: bool
```
... will produce the following CLI:
```bash
$ python main.py --help
usage: main.py [-h] [--seconds SECONDS] [--show_time]

options:
  -h, --help         show this help message and exit
  --seconds SECONDS  (default: 1)
  --show_time
```

### Use the `Argument` class to further configure your CLI's arguments.

The `Argument` function takes the same arguments as the built-in `argparse.ArgumentParser.add_argument` function.


For example, this...

```python
from cli_buddy import CLI, Argument


class TerminalTimer(CLI):
    seconds: int = Argument(help="Number of seconds to wait")
    show_time: bool = Argument("-t", help="Show seconds in terminal", action="store_true")
```

... will produce the following CLI:
```bash
$ python main.py --help
usage: main.py [-h] -t seconds

positional arguments:
  seconds          Number of seconds to wait

options:
  -h, --help       show this help message and exit
  -t, --show_time  Show seconds in terminal
```
