import typing
from functools import wraps

from shiftval.errors import LintError
from shiftval.validators import collected_validators


def validator(*kinds: typing.List[str], collect=True,
              raise_on_invalid_kind=False) \
        -> typing.Callable:
    """
    decorator to generate validator functions.

    Expects LintError exceptions on invalid configurations.
    """
    def add(f: typing.Callable):
        @wraps(f)
        def wrapped(yml: object):
            kind = yml.get('kind')
            if kind not in kinds:
                if raise_on_invalid_kind:
                    raise LintError('invalid kind %s' % kind)
                return ([], [])
            try:
                res = f(yml)
            except LintError as e:
                e.set_desc(f.__doc__)
                raise

            if not res:
                return ([], [])
            if isinstance(res, list):
                return (res, [])
            return res

        if collect:
            collected_validators.append(wrapped)
        return wrapped
    return add


def object_ident(yml: object) -> str:
    """
    returns a k8s identifier based on kind and name.
    """
    kind = yml.get('kind')
    name = yml.get('metadata').get('name')
    return f"{kind}/{name}"
