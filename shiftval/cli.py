import sys
import typing
from contextlib import contextmanager

import click
import yaml

from shiftval.errors import LintError
from shiftval.validators import collected_validators


@click.command()
def main():
    with log_exception():
        run()


def run():
    """entrypoint"""
    ymls = yaml.safe_load_all(sys.stdin)
    ymls = [
        yml for yml in ymls
        if isinstance(yml, dict) and yml.get("kind", False)
    ]

    validators = collected_validators
    while validators:
        new_validators: typing.List[typing.Callable] = []
        must_validators: typing.List[typing.Callable] = []
        for yml in ymls:
            append, must_append = handle(yml, validators)
            new_validators += append
            must_validators += must_append

        for yml in ymls:
            for must_validator in must_validators[:]:
                try:
                    must_validator(yml)
                    must_validators.remove(must_validator)
                except LintError:
                    pass
        if must_validators:
            missing = [v.__doc__ or v.__name__ for v in must_validators]
            raise LintError(f'required validators are not provided: {missing}')
        validators = new_validators
    click.secho('-' * 40)
    click.secho('no critical issues.')


def handle(yml: dict, vals: typing.Dict[str, typing.Callable]) \
        -> typing.Dict[str, typing.Callable]:
    new_validators: typing.List[typing.Callable] = []
    new_must_validators: typing.List[typing.Callable] = []
    for val in vals:
        append, must_append = val(yml)
        new_validators += append
        new_must_validators += must_append
    return new_validators, new_must_validators


@contextmanager
def log_exception():
    try:
        yield
    except LintError as exc:
        click.secho('* %s' % exc, fg='red')
        if exc.description:
            click.secho('  | ' + '\n  | '.join(
                exc.description.splitlines()
            ), fg='blue')


if __name__ == '__main__':
    main()
