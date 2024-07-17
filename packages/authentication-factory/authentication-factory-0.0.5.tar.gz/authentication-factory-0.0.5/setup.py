#!/usr/bin/env python

"""
Prerequesites -
  Python Packages:
    * setuptools
    * GitPython
    * wheel
  System Packages:
    * make
    * Python 3
Commands: python setup.py [bdist_wheel / [sdist [--format=[gztar][,tar]]]
Ex:
  * python setup.py bdist_wheel
  * python setup.py sdist
  * python setup.py sdist --format=gztar
  * python setup.py sdist --format=tar
  * python setup.py sdist --format=gztar,tar
  * python setup.py sdist --format=gztar
  * python setup.py bdist_wheel sdist --format=gztar,tar
"""

"""
distutils/setuptools install script.
"""


from setuptools import setup, find_packages
import traceback
import shutil
import re
import os
__NAME__ = "authentication-factory"

ROOT = os.path.dirname(os.path.abspath(__file__))
VERSION_FILE = os.path.join(ROOT, __NAME__.replace("-", "_"), ".version")
VERSION_RE = re.compile(r'''__version__ = ['"]([0-9.]+)['"]''')

base = [
    # Python HTTP for Humans.
    "requests<=2.32.3",
    # The Microsoft Authentication Library (MSAL) for Python library by supporting authentication of users with Microsoft Azure Active Directory accounts (AAD) and Microsoft Accounts (MSA) using industry standard OAuth2 and OpenID Connect.
    "msal<=1.29.0",
    # JSON Web Token implementation in Python
    "PyJWT<=2.8.0",
    # Cryptography is a package which provides cryptographic recipes and primitives to Python developers.
    "cryptography<=42.0.8",
    # Python wrapper module around the OpenSSL library
    "pyopenssl<=24.1.0"
]

dependencies = [
    "certifi<=2024.7.4",
    "charset-normalizer<=3.3.2",
    "idna<=3.7",
    "urllib3<=2.2.2",
    "cffi<=1.16.0",
    "pycparser<=2.22"
]

setups = [
    "gitpython",
    "setuptools",
    "wheel"
]

ir = (base + dependencies)
requires = ir


def delete(path):
    if os.path.exists(path=path):
        try:
            if os.path.isfile(path=path):
                os.remove(path=path)
            else:
                shutil.rmtree(path=path)
        except:
            pass


def write_version(version, sha, filename):
    text = f"__version__ = '{version}'\n__REVESION__ = '{sha}'"
    with open(file=filename, mode="w") as file:
        file.write(text)


def get_version(filename):
    version = "1.0.0"  # Adding default version

    # This block is for reading the version from foundry distribution
    if os.path.exists(path=filename):
        contents = None
        with open(file=filename, mode="r") as file:
            contents = file.read()
            version = VERSION_RE.search(contents).group(1)
            return version

    # If file not found. Then may be local or want to get the version
    version_python_file = os.path.join(ROOT, "version.py")
    if os.path.exists(path=version_python_file):
        import version as ver
        version = ver.version

        sha = ""
        try:
            import git
            repo = git.Repo(path=".", search_parent_directories=True)
            sha = repo.head.commit.hexsha
            sha = repo.git.rev_parse(sha, short=6)
        except ImportError:
            print(f"Import error on git, can be ignored for build")
            pass
        except Exception as exception:
            print(str(exception))
            traceback.print_tb(exception.__traceback__)
            pass
        write_version(version=version, sha=sha, filename=filename)
    return version


with open("README.md", "r") as f:
    long_description = f.read()


def do_setup():
    setup(
        name=__NAME__,
        version=get_version(filename=VERSION_FILE),
        description='Implementation for Microsoft Oauth2 authentication',
        long_description=long_description,
        long_description_content_type="text/markdown",
        keywords=['streamlit', 'flask', 'microsoft', 'json web token', 'oauth2',
                  'authentication'],
        author='Ankit Shrivastava',
        url='https://github.com/shrivastava-v-ankit/authentication-factory',
        packages=find_packages(include=[__NAME__.replace("-", "_")]),
        include_package_data=True,
        setup_requires=setups,
        install_requires=requires,
        license="MIT",
        python_requires='>=3.9, <=3.12.4',
        platforms='any',
        project_urls={
            'Source': 'https://github.com/shrivastava-v-ankit/authentication-factory/',
            'Tracker': 'https://github.com/shrivastava-v-ankit/authentication-factory/issues',
        },
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Web Environment',
            'Framework :: Flask',
            'Intended Audience :: Developers',
            'Natural Language :: English',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Programming Language :: Python :: 3.11',
            'Programming Language :: Python :: 3.12',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Software Development :: Version Control :: Git',
        ],
    )


if __name__ == "__main__":
    import sys

    do_setup()

    if "sdist" in sys.argv or "bdist_wheel" in sys.argv:
        egg_info = os.path.join(ROOT, __NAME__.replace("-", "_") + '.egg-info')
        delete(path=egg_info)
        eggs = os.path.join(ROOT, ".eggs")
        delete(path=eggs)
        delete(path=VERSION_FILE)
        build_dir = os.path.join(ROOT, "build")
        delete(path=build_dir)
