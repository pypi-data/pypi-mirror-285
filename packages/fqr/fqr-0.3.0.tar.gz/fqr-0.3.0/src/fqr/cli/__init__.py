"""
Overview
========

**Summary:** Primary command-line interface (CLI) to fqr.

---

Usage
-----

```sh
$ fqr --help
```

"""

__all__ = (
    'cns',
    'lib',
    'obj',
    'main',
    'utl',
    )

from . import cns
from . import lib
from . import obj
from . import utl

from . utl import main
