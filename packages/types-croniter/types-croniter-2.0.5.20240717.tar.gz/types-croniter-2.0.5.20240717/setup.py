from setuptools import setup

name = "types-croniter"
description = "Typing stubs for croniter"
long_description = '''
## Typing stubs for croniter

This is a [PEP 561](https://peps.python.org/pep-0561/)
type stub package for the [`croniter`](https://github.com/kiorky/croniter) package.
It can be used by type-checking tools like
[mypy](https://github.com/python/mypy/),
[pyright](https://github.com/microsoft/pyright),
[pytype](https://github.com/google/pytype/),
PyCharm, etc. to check code that uses
`croniter`.

This version of `types-croniter` aims to provide accurate annotations
for `croniter==2.0.5`.
The source for this package can be found at
https://github.com/python/typeshed/tree/main/stubs/croniter. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/main/README.md for more details.
This package was generated from typeshed commit
[`6d68b57d7419fd6a5d2924c6cc540ac0377c8d7c`](https://github.com/python/typeshed/commit/6d68b57d7419fd6a5d2924c6cc540ac0377c8d7c) and was tested
with mypy 1.10.1, pyright 1.1.371, and
pytype 2024.4.11.
'''.lstrip()

setup(name=name,
      version="2.0.5.20240717",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/croniter.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=[],
      packages=['croniter-stubs'],
      package_data={'croniter-stubs': ['__init__.pyi', 'croniter.pyi', 'METADATA.toml', 'py.typed']},
      license="Apache-2.0 license",
      python_requires=">=3.8",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
