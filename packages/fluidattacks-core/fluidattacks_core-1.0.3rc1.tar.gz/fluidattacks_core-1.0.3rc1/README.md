# Fluid Attacks Core Library


<p align="center">
  <img alt="logo" src="https://res.cloudinary.com/fluid-attacks/image/upload/f_auto,q_auto/v1/airs/menu/Logo?_a=AXAJYUZ0.webp" />
</p>

<div style="background-color: #EEE7B9; color: black; padding: 2px 16px; border-radius: 10px; border: 2px solid #BBB28A; margin-bottom: 1rem">

### Disclaimer

This library was developed for Fluid Attacks projects. That specific
context is reflected in some presets and configurations.

</div>

## Importing types

```python
from fluidattacks_core.{module}.types import (
    ...
)
```

where `{module}` is one of the following:

- authz

## Publishing a new version

1. Make any changes you want to the library.
1. Run the Python linter:
    ```bash
    m . /lintPython/dirOfModules/commonUtilsPypiFluidattackscore
    ```
1. Upgrade the library version in `pyproject.toml`.
    > Make sure to do this as it is required for your changes to be published.
1. Push your changes using the `common\` pipeline.
1. Once you reach production,
    the new version of the library should become available.



------------------------------------------------------------

# Core: Testing

### Motivation

Standardize test fundamentals for current and new projects in
any organization could be a hard task.
Also, thanks to pytest malleability, we find different solutions solving
the same problems and a harder test maintainability.

Using pytest, we find that developers tend to use a lot of features
(fixtures, patches, marks, etc.) without any standard but pytest is still a
very simple and powerful tool.

For this reason, we decided to create a pytest wrapper that includes some
presets and defines testing standards for us.

### Description

This library aims to provide a simple way to write
**unit and integration tests** for Python products using boto3 services and
other common packages.

Philosophy of this package is to be simple and include the most common
testing features in a standard way.

## Table of Contents

1. [Usage](#usage)
1. [Tagging](#tagging)
1. [Fakers](#fakers)
1. [Mocking](#mocking)

## Usage

```bash
fluidattacks_test --help

: '
usage: fluidattacks-test [-h] [--target [TARGET]] [--src [SRC]] [--scope SCOPE]

🏹 Python package for unit and integration testing through Fluid Attacks projects 🏹

options:
  -h, --help         show this help message and exit
  --target [TARGET]  Folder to start the tests. Default is current folder.
  --src [SRC]        Folder with the source code for coverage report. Default is src.
  --scope SCOPE      Type and module to test.
```

`target` is the main folder where test and coverage folders will be resolved.

`src` is the folder where the source code is located and by default it is `{target}/src`.

`scope`, the only required argument, is the test folder to run from `{target}/test/unit/src`.

An example of usage is:
```bash
fluidattacks_test --scope billing
```

## Tagging

You can use tags same as marks in pytest:

```python
from fluidattacks_test import tag

@tag.billing
def test_billing():
    ...

@tag.auth
def test_auth():
    ...
```

Recommendations:
- Tag every test in one file with the same tag: the folder name.
- Don't use special pytest tags like `slow`, `skip`, `only`, `xfail`, etc. If
you need any special tag for any reason, please contribute to this package
extension.

## Fakers

Some fakers are available to generate stub data for tests:

- `fake_vulnerability()`.
- `fake_finding()`.
- `fake_group()`.

## Mocking

Some utilities are available via dependency injection to test methods.
Mocking is one of them and it allows you to change the behavior and returns of
any method or class in your code.

### Functions

You can mock functions using `mocking`:

```python
from fluidattacks_test import tag
from fluidattacks_test.types import MockingFunction

import requests

@tag.billing
def test_billing(mocking: MockingFunction) -> None:
    mock_post = mocking(requests, "post", { "status_code": 200 })

    ...

    call_list = mock_post.calls()
    assert len(call_list) == 1
```

It changes the behavior of the `post` method from the `requests` module to
return always `{ "status_code": 200 }`. The `mock_post` object stores every call
running the tests to the method for assertion purposes.

Check the `.calls()` method for more information.



---

More instructions coming soon...
