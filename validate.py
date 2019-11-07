import re
import sys
import typing
import yaml
from contextlib import contextmanager
from jsonpath_ng import parse


Validator = typing.NamedTuple("Validator", [
    ('on', str),
    ('path', str),
    ('matcher', typing.Union[str, typing.Pattern, None]),
])


VALIDATORS = [
    Validator('Deployment', 'metadata.labels."thobits.com/git-sha"', re.compile(r'.{6,}')),
    Validator('StatefulSet', 'metadata.labels."thobits.com/git-sha"', re.compile(r'.{6,}')),
    Validator('Route', 'metadata.annotations."thobits.com/ormon-valid-statuscodes"',
              re.compile(r'.{6,}')),
]

def main():
    """entrypoint"""
    ymls = yaml.safe_load_all(sys.stdin)
    ymls = [
        yml for yml in ymls
        if isinstance(yml, dict) and yml.get("kind", False)
    ]

    validators = VALIDATORS
    while validators:
        new_validators: typing.List[Validator] = []
        for yml in ymls:
            append = handle(yml, validators)
            if append:
                new_validators += append
        validators = new_validators
        print(validators)


def handle(yml: dict, vals: typing.Dict[str, Validator]) \
        -> typing.List[Validator]:
    new_validators: typing.List[Validator] = []
    for val in vals:
        append = validate(yml, **val._asdict())
        new_validators += append
    return new_validators


def validate(yml: dict,
             on: str,
             path: str,
             matcher: typing.Union[str, typing.Pattern, None]) \
        -> typing.Optional[typing.Tuple[str, str]]:
    jpexp = parse(path)
    matches = jpexp.find(yml)

    broken = False
    if not matches:
        raise Exception(f'validator {matcher} on {path} did not match!')
    for match in matches:
        if isinstance(matcher, str):
            broken = match.value == matcher
        elif isinstance(matcher, re.Pattern):
            broken = bool(matcher.match(match.value))
        if broken:
            break
    if broken:
        print(on, 'broke')
    return []


@contextmanager
def log_exception():
    try:
        yield
    except Exception as exc:  # pylint: disable=broad-except
        print(exc)

if __name__ == '__main__':
    with log_exception():
        main()
