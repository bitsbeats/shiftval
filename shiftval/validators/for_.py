import typing
import click

from jsonpath_ng import parse as json_path

from shiftval.helpers import object_ident
from shiftval.helpers import validator
from shiftval.errors import LintError


def pdb_for(name: str, labels: typing.Dict[(str, object)]) -> typing.Callable:
    @validator('PodDisruptionBudget', collect=False,
               raise_on_invalid_kind=True)
    def named_pdb_for(yml: object):
        """
        Validates that a matching PodDisruptionBudget for the deployments
        labels exists.

        # example:
        apiVersion: policy/v1beta1
        kind: PodDisruptionBudget
        metadata:
          name: myservice-pdb
          labels:
            app: myservice
            {{- include "helm.labels" . | nindent 4 }}
        spec:
          maxUnavailable: 1
          selector:
            matchLabels:
              app: myservice

        Replace all myservice with service name / other labels.
        """
        ident = object_ident(yml)
        matches = json_path('spec.selector.matchLabels').find(yml)
        if not matches:
            raise LintError(f"* no label matching {name} for {ident}")

        got_labels = matches[0].value
        for key, value in got_labels.items():
            if key not in labels.keys() or labels[key] != value:
                message = (
                    f"pdb {ident} is missing label combination for {name}"
                    f"{key}={value}"
                )
                raise LintError(message)

        click.secho(f"* found pdb {ident} for {name}", fg='green')

    return named_pdb_for


def route_for(name: str, json_path_to_value: typing.Dict[(str, str)]) \
        -> typing.Callable:
    @validator('Route', collect=False, raise_on_invalid_kind=True)
    def named_route_for(yml: object):
        """
        require the existance of a route with matching parameters
        """
        ident = object_ident(yml)
        for jp, value in json_path_to_value.items():
            matches = json_path(jp).find(yml)
            if not all(m.value == value for m in matches):
                raise LintError(f"{jp}={value} not found")
            click.secho(f'* possible matching {ident} for "{name}" '
                        f'found({jp}={value})', fg='green')
    return named_route_for


def velero_for(name: str) -> typing.Callable:
    @validator('StatefulSet', 'Deployment', collect=False,
               raise_on_invalid_kind=True)
    def named_velero_for(yml: object):
        """
        Validates that a backup or a backup-exclude is defined for each volume.

        annotations:
          backup.velero.io/backup-volumes: data,backup
          backup.velero.io/backup-volumes-excludes: cache

        note: all defined volumes must specify a backup
        """
        ident = object_ident(yml)
        backup_matches = json_path(
            'spec.template.metadata.annotations.'
            '"backup.velero.io/backup-volumes"'
        ).find(yml)
        skip_matches = json_path(
            'spec.template.metadata.annotations.'
            '"backup.velero.io/backup-volumes-excludes"'
        ).find(yml)
        if not backup_matches:
            raise LintError(f"unable to find velero annotation on {ident}")
        backupped_volumes = backup_matches[0].value.split(',')
        skipped_volumes = []
        if skip_matches:
            skipped_volumes = skip_matches[0].value.split(',')
        if name in skipped_volumes:
            click.secho(f"* backup for volume {name} skipped in {ident}",
                        fg='yellow')
        elif name in backupped_volumes:
            click.secho(f"* backup for volume {name} found in {ident}",
                        fg='green')
        else:
            raise LintError(f"no backup or skip for {name} found in {ident}")

    return named_velero_for
