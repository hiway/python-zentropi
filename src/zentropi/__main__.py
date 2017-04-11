# coding=utf-8
"""
Entrypoint module, in case you use `python -mzentropi`.


Why does this file exist, and why __main__? For more info, read:

- https://www.python.org/dev/peps/pep-0338/
- https://docs.python.org/2/using/cmdline.html#cmdoption-m
- https://docs.python.org/3/using/cmdline.html#cmdoption-m
"""  # pragma: no cover
from zentropi.cli import main  # pragma: no cover

if __name__ == "__main__":  # pragma: no cover
    main()
