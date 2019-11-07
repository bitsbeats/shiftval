import click
from jsonpath_ng import parse as json_path

from shiftval.helpers import object_ident
from shiftval.errors import LintError
from shiftval.helpers import validator


@validator('Route')
def route_monitoring(yml: object):
    """
    A route should always be monitored by ormon.

    annotations:
      thobits.com/ormon-valid-statuscodes: 200,300
      thobits.com/ormon-body-regex: Thomann

    note: ormon-valid-statuscodes has to be a string.
    """
    matches = json_path(
        'metadata.annotations."thobits.com/ormon-skip"'
    ).find(yml)
    if (matches
            and matches[0].value in ['1', 't', 'T', 'TRUE', 'true' or 'True']):
        click.secho(
            f'* resource with disabled monitoring found: {object_ident(yml)}',
            fg='yellow'
        )
        return

    codes = json_path('metadata.annotations."thobits.com/"').find(yml)
    if codes:
        codes = codes.pop().value
        if not all(code.isdigit() for code in codes.split(',')):
            raise LintError(f'invalid statuscodes for {object_ident(yml)}')
        return

    body_regexes = json_path(
        'metadata.annotations."thobits.com/ormon-body-regex"'
    ).find(yml)
    if body_regexes:
        body_regex = body_regexes.pop()
        return

    raise LintError(f'no monitoring specified for {object_ident(yml)}')


@validator('Route')
def route_warn_public(yml: object):
    """Warn for every public route."""
    matches = json_path('metadata.annotations."acme.openshift.io/exposer"')
    if matches:
        click.secho(f'* public route found: {object_ident(yml)}', fg='yellow')
