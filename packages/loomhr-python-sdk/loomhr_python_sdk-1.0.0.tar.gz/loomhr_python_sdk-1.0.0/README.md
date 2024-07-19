``` 
 _____                         _______ ______
|     |_.-----.-----.--------.|   |   |   __ \
|       |  _  |  _  |        ||       |      <
|_______|_____|_____|__|__|__||___|___|___|__|
           
        Copyright (C) 2024 LoomHR, Inc.
             All rights reserved.
```

# LoomhHR Python SDK Library

This project provides a Python SDK library designed for LoomHR specialist developers. The library includes:

- Request and Response Classes: Python classes for handling API interactions efficiently.
- Abstract Helper Classes: Simplify asynchronous logic processing.
- REST Utility Methods: Offer helpful functions for working with REST APIs.

## Installation

```bash
pip install loomhr-python-sdk
```

## Usage

- Test Sections: Review the test sections in the documentation to understand how to implement and use the library's
  features.
- Examples: Visit the examples section on the [LoomHR website](https://loomh.ai) for practical use cases and
  demonstrations.

## Usage

- Test Sections: Review the test sections in the documentation to understand how to implement and use the library's
  features.
- Examples: Visit the examples section on the [LoomHR website](https://loomh.ai) for practical use cases and
  demonstrations.

## Library Release

- `rm -rf dist/*`
- `pip list --format=freeze > requirements.txt`
- `python setup.py sdist bdist_wheel`
- `twine upload --repository testpypi dist/*` or `twine upload --repository pypi dist/*`

<br />
<img src="https://loomhr.ai/images/logo_64x64.png" alt="LoomHR Logo">