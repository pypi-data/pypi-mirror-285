# authentication-factory

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI](https://img.shields.io/pypi/v/authentication-factory.svg)](https://pypi.org/project/authentication-factory)


**Note: This is inital version of the factory with support of Microsoft OAuth2.0 only with Streamlit.**


authentication-factory is a simple python implementation of authentication using below listed authentication mechanism.

   * Microsoft OAuth2.0

This extension helps to implement authentication solutions and provides
login url, logout url and id token.
These can be used in python web application like Streamlit, Flask etc.

</br>
</br>

## Getting Started
-----

</br>

## Installation

```bash
pip install authentication-factory
```

</br>

### Usage
-----
   * [Streamlit](streamlit-example.md)


</br>
</br>

### Development Setup
-------
#### Using virtualenv

```bash
python3 -m venv venv
source env/bin/activate
pip install .
```
</br>
</br>

### Contributing
-----

1. Fork repo- https://github.com/shrivastava-v-ankit/authentication-factory.git
2. Create your feature branch - `git checkout -b feature/name`
3. Add Python test (pytest) and covrage report for new/changed feature.
4. Commit your changes - `git commit -am "Added name"`
5. Push to the branch - `git push origin feature/name`
6. Create a new pull request