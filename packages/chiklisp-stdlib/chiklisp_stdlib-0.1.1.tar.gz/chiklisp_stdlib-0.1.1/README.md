# chiklisp_stdlib

Use:

`pip install chiklisp_stdlib`

To get the path to the include files, use

```python
from chiklisp_stdlib import NIGHTLY_INCLUDE_DIRECTORY
from chiklisp_stdlib import STABLE_INCLUDE_DIRECTORY
```

Note that `*_INCLUDE_DIRECTORY` is a `pathlib.Path` and not a `str`, so if your API expects `str`-based paths, use `str(path)` to convert.

And upgrade your API: see [PEP519](https://peps.python.org/pep-0519/). C'mon, it's 2023 (as of this writing).
