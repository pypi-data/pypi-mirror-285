# gone
_Make stuff disappear_

[![PyPI - Version](https://img.shields.io/pypi/v/gone.svg)](https://pypi.org/project/gone)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/gone.svg)](https://pypi.org/project/gone)

-----

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Installation

```console
pip install gone
```

## Usage

The `gone` module provides three decorators to manipulate function input and output:

1. `args`: Absorbs all input arguments and calls the decorated function without them.
2. `result`: Discards the result of the decorated function.
3. `inout`: Absorbs all input arguments and discards the result of the decorated function.

### Usage Example

```python
import gone

@gone.args
def greet():
    return "Hello World"

greet(1, 2, key=3)  # Result: Hello, world!

@gone.result
def add(a, b):
    return a + b

print(add(1, 2))  # Output: None


@gone.inout
def display_message():
    print("This will print, but inputs and outputs are ignored.")
    return "ignored"

display_message("ignored input")  # Output: This will print, but inputs and outputs are ignored; Returns: None
```

## License

`gone` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
