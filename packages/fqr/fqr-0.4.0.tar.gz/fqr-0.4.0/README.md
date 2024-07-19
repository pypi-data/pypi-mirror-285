# [![banner](https://1howardcapital.s3.amazonaws.com/images/fqr/banner.png)](https://fqr.readthedocs.io)

[![MinVersion](https://img.shields.io/python/required-version-toml?tomlFilePath=https://raw.githubusercontent.com/dan1hc/fqr/main/pyproject.toml&color=gold)](https://pypi.org/project/fqr)
[![PyVersions](https://img.shields.io/pypi/pyversions/fqr?color=brightgreen)](https://pypi.org/project/fqr)
[![readthedocs](https://readthedocs.org/projects/fqr/badge)](https://fqr.readthedocs.io)
[![CI](https://github.com/dan1hc/fqr/actions/workflows/main.yml/badge.svg?branch=main&event=push)](https://github.com/dan1hc/fqr/actions)
[![codeql](https://github.com/dan1hc/fqr/workflows/codeql/badge.svg)](https://github.com/dan1hc/fqr/actions/workflows/codeql.yml)
[![coverage](https://img.shields.io/badge/dynamic/toml?url=https://raw.githubusercontent.com/dan1hc/fqr/main/pyproject.toml&query=tool.coverage.report.fail_under&label=coverage&suffix=%25&color=brightgreen)](https://github.com/dan1hc/fqr/actions)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![PyPI](https://img.shields.io/pypi/v/fqr?color=blue)](https://pypi.org/project/fqr)
[![License](https://img.shields.io/pypi/l/fqr?color=blue)](https://www.gnu.org/licenses/lgpl-3.0)

# Overview

**Author:** dan@1howardcapital.com | daniel.dube@annalect.com

**Pronunciation:** _fʌkɚr `>` ɛf kj ɑːr_

**Summary:** Zero-dependency python framework for object oriented development.
Implement _once_, document _once_, in _one_ place.

> With fqr, you will quickly learn established best practice...
> or face the consequences of runtime errors that will break your code
> if you deviate from it.
>
> Experienced python engineers will find a framework
> that expects and rewards intuitive magic method usage,
> consistent type annotations, and robust docstrings.
>
> Implement _pythonically_ with fqr and you will only ever need to:
> implement _once_, document _once_, in _one_ place.

---

## Mission Statement

Ultimately, fqr seeks to capture and abstract all recurring patterns in
application development with known, optimal implementations, so engineers
can focus more on clever implementation of application-specific logic and good
documentation than on things like how to query X database most efficiently,
whether or not everything important is being logged correctly, where to
put what documentation, and how to implement an effective change management
scheme with git in the first place.

## Getting Started

### Installation

```bash
pip install fqr
```

### Basic Usage

```py
import fqr


class Pet(fqr.Object):
    """A pet."""

    id_: fqr.Field[int]
    name: fqr.Field[str]
    type_: fqr.Field[str] = {
        'default': 'dog',
        'enum': ['cat', 'dog'],
        'nullable': False,
        'required': True,
        }
    is_tail_wagging: fqr.Field[bool] = fqr.Field(
        default=True,
        enum=[True, False],
        nullable=False,
        required=True,
        )

```

## Best Practice - Guard Rails at a Bowling Alley

fqr has been designed from the outset to teach best practice to less
experienced python engineers, without compromising their ability to
make effective and timely contributions.

> To fqr, it is more important developers are able to make
> effective contributions while learning, rather than sacrifice
> any contribution at all until the developer fully understands
> why something that could be done many ways should only ever
> be done one way.

#### Exceptions

This is achieved primarily through the raising of exceptions.
In many cases, if a developer inadvertently deviaties from a known
best practice, fqr will raise a code-breaking error (informing
the developer of the violation) until the developer implements
the optimal solution.

#### Logging

fqr will commandeer your application's log.

* It will automatically redact sensitive data inadvertently introduced
to your log stream that would have made your application fail audits.
* It will intercept, warn once, and subsequently silence print statements,
debug statements, and other errant attempts at logging information in ways
certain to introduce a known anti-pattern, vulnerability, or otherwise
pollute your log stream.

> In short, if fqr raises an error or otherwise does not support
> the thing you are trying to do: it is because the way in which you
> are trying to do it contains at least one anti-pattern to a known,
> optimal solution.

## Example Usage

```py
import fqr


class Flea(fqr.Object):
    """A nuisance."""

    name: fqr.Field[str] = 'FLEA'


class Pet(fqr.Object):
    """A pet."""

    id_: fqr.Field[str]
    _alternate_id: fqr.Field[int]

    name: fqr.Field[str]
    type_: fqr.Field[str] = {
        'default': 'dog',
        'enum': ['cat', 'dog'],
        'nullable': False,
        'required': True,
        }

    in_: fqr.Field[str]
    is_tail_wagging: fqr.Field[bool] = fqr.Field(
        default=True,
        enum=[True, False],
        nullable=False,
        required=True,
        )

    fleas: fqr.Field[list[Flea]] = [
        Flea(name='flea1'),
        Flea(name='flea2')
        ]


# Automatic case handling.
request_body = {
    'id': 'abc123',
    'alternateId': 123,
    'name': 'Bob',
    'type': 'dog',
    'in': 'timeout',
    'isTailWagging': False
    }
pet = Pet(request_body)

assert pet.is_snake_case == Pet.is_snake_case is True
assert pet.is_camel_case == Pet.is_camel_case is False
assert pet['alternate_id'] == pet._alternate_id == request_body['alternateId']
assert dict(pet) == {k: v for k, v in pet.items()} == pet.to_dict()

# Automatic, mutation-safe "default factory".
dog = Pet(id='abc321', alternate_id=321, name='Fido')
assert pet.fleas[0] is not dog.fleas[0]

# Automatic memory optimization.
assert Flea().__sizeof__() == (len(Flea.__slots__) * 8) + 16 == 32

class Flet(Flea, Pet):
    ...

class Pea(Pet, Flea):
    ...

assert Flet().__sizeof__() == (len(Flet.__base__.__slots__) * 8) + 16 == 80
assert Pea().__sizeof__() == (len(Pea.__base__.__slots__) * 8) + 16 == 80
assert Flet().name == 'FLEA' != Pea().name

# Intuitive, database agnostic query generation.
assert isinstance(Pet.is_tail_wagging, fqr.Field)
assert isinstance(Pet.type_, fqr.Field)

assert dog.type_ == Pet.type_.default == 'dog'

query = (
    (
        (Pet.type_ == 'dog')
        & (Pet.name == 'Fido')
        )
    | Pet.name % ('fido', 0.75)
    )
query += 'name'
assert dict(query) == {
    'limit': None,
    'or': [
        {
            'and': [
                {
                    'eq': 'dog',
                    'field': 'type',
                    'limit': None,
                    'sorting': []
                    },
                {
                    'eq': 'Fido',
                    'field': 'name',
                    'limit': None,
                    'sorting': []
                    }
                ],
            'limit': None,
            'sorting': []
            },
        {
            'field': 'name',
            'like': 'fido',
            'limit': None,
            'sorting': [],
            'threshold': 0.75
            }
        ],
    'sorting': [
        {
            'direction': 'asc',
            'field': 'name'
            }
        ]
    }

```

### Local Logging
```py
import fqr


class AgentFlea(fqr.Object):
    """Still a nuisance."""

    name: fqr.Field[str] = 'FLEA'
    apiKey: fqr.Field[str] = '9ac868264f004600bdff50b7f5b3e8ad'
    awsAccessKeyId: fqr.Field[str] = 'falsePositive'
    sneaky: fqr.Field[str] = 'AKIARJFBAG3EGHFG2FPN'


# Automatic log configuration, cleansing, and redaction.

print(AgentFlea())
# >>>
# {
#   "level": WARNING,
#   "time": 2024-02-26 18:50:20.317 UTC,
#   "log": fqr.core.log,
#   "data":   {
#     "message": "Calls to print() will be silenced by fqr."
#   }
# }
# {
#   "apiKey": "[ REDACTED :: API KEY ]",
#   "awsAccessKeyId": "falsePositive",
#   "name": "FLEA",
#   "sneaky": "[ REDACTED :: AWS ACCESS KEY ID ]"
# }

print(AgentFlea())
# >>>
# {
#   "apiKey": "[ REDACTED :: API KEY ]",
#   "awsAccessKeyId": "falsePositive",
#   "name": "FLEA",
#   "sneaky": "[ REDACTED :: AWS ACCESS KEY ID ]"
# }

```

### Deployed Logging

```py
import os
os.environ['ENV'] = 'DEV'

import fqr

assert (
    fqr.core.constants.PackageConstants.ENV
    in {
        'dev', 'develop',
        'qa', 'test', 'testing',
        'uat', 'stg', 'stage', 'staging',
        'prod', 'production',
        }
    )


class AgentFlea(fqr.Object):
    """Still a nuisance."""

    name: fqr.Field[str] = 'FLEA'
    apiKey: fqr.Field[str] = '9ac868264f004600bdff50b7f5b3e8ad'
    awsAccessKeyId: fqr.Field[str] = 'falsePositive'
    sneaky: fqr.Field[str] = 'AKIARJFBAG3EGHFG2FPN'


print(AgentFlea())
# >>>
# {
#   "level": WARNING,
#   "time": 2024-02-26 19:02:29.020 UTC,
#   "log": fqr.core.log,
#   "data":   {
#     "message": "Call to print() silenced by fqr.",
#     "printed": "{\n  \"apiKey\": \"[ REDACTED :: API KEY ]\",\n  \"awsAccessKeyId\": \"falsePositive\",\n  \"name\": \"FLEA\",\n  \"sneaky\": \"[ REDACTED :: AWS ACCESS KEY ID ]\"\n}"
#   }
# }

print(AgentFlea())
# >>>

fqr.log.info(AgentFlea())
# >>>
# {
#   "level": INFO,
#   "time": 2024-02-26 19:13:21.726 UTC,
#   "log": fqr.core.log,
#   "data":   {
#     "AgentFlea": {
#       "apiKey": "[ REDACTED :: API KEY ]",
#       "awsAccessKeyId": "falsePositive",
#       "name": "FLEA",
#       "sneaky": "[ REDACTED :: AWS ACCESS KEY ID ]"
#     }
#   }
# }

```

## Planned Features

* #### RESTful Framework / OpenAPI Support
    * fqr should support all aspects of an OpenAPI specification and
    provide corresponding framework functionality for HTTP request
    handling.
* #### Template Packages
    * fqr should include a Pet shop style demo API and python package
    as a template for developers to copy / paste from.
* #### Database Parse & Sync
    * fqr should be able to generate a python package with fully enumerated
    and optimized `Objects` (and a corresponding fqr API package) when
    supplied with access to a database for which at least one schema may be
    inferred.
        * CLI commands like `$ fqr-api-from-sql ${api_name} ${sql_conn_string} .`
        should instantly output two ideally structured package repositories for a
        RESTful python API and corresponding object management package.
        * The package could use any supplied credentials to either query a database
        directly or make requests to a deployed API. This means the same package
        used to power the API can be distributed and pip installed across an
        organization so business intelligence, data science, and other technical
        team members can manipulate data for their needs, while leaning on
        the package to optimize queries and stay informed around permission
        boundaries and request limits.
* #### Repo Generation
    * fqr should be expanded to optionally wrap any generated packages
    in a repository pre-configured with essentials and CI that should:
        * implement an ideal [trunk-based branch strategy](https://trunkbaseddevelopment.com/),
        inline with current best practices for change management and
        developer collaboration
        * enforce python code style best practices through automated
        [linting and formatting](https://docs.astral.sh/ruff)
        * type-check python code and generate a report with [mypy](https://mypy.readthedocs.io/en/stable/index.html)
        * run tests automatically, generate reports, and prevent commits that break tests
        * automatically prevent commits that do not adhere to standardized commit
        message [conventions](https://www.conventionalcommits.org/en/v1.0.0/)
        * using those conventions, automatically [semantically version](https://python-semantic-release.readthedocs.io/en/stable/#getting-started)
        each successful PR and automatically generate and update a
        CHANGELOG.md file
        * automatically generate and publish secure wiki documentation
    * Generated repos may contain up to all of the following:
        * CHANGELOG.md
        * CODEOWNERS
        * CONTRIBUTING.md
        * .git
            * .git/hooks/
        * .github/workflows/
            * Support planned for gitlab and bamboo.
        * .gitignore
        * LICENSE
        * [.pre-commit-config.yaml](https://pre-commit.com/#intro)
        * pyproject.toml
        * README.md
        * /src
            * /package
            * /tests

## Acknowledgments

* #### @sol.courtney
    * Teaching me the difference between chicken-scratch, duct tape, and bubble
    gum versus actual engineering, and why it matters.
