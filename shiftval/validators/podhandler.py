from jsonpath_ng import parse as json_path

from shiftval.helpers import object_ident, validator
from shiftval.errors import LintError
from shiftval.validators.for_ import pdb_for, velero_for, route_for


@validator('Deployment', 'StatefulSet')
def podhandler_git_sha(yml: object):
    """
    This resource requires a git-sha annotation to prevent issues on rolling
    updates with old configmap and secret versions. This annotation must be
    set on "spec.template.metadata.annotations".

    annotations:
      thobits.com/git-sha: 000000
    """
    ident = object_ident(yml)
    matches_bad = json_path(
        'metadata.annotations."thobits.com/git-sha"'
    ).find(yml)
    matches_good = json_path(
        'spec.template.metadata.annotations."thobits.com/git-sha"'
    ).find(yml)
    if matches_bad:
        raise LintError(f'move git-sha annotation to '
                        f'spec.template.metadata.annotations for {ident}')
    if not matches_good:
        raise LintError(f'git-sha missing on {ident}')


@validator('Deployment', 'StatefulSet')
def podhandler_pod_disruption_budget(yml: object):
    """require a podhandler for every deployment/statefulset."""
    matches = json_path('spec.template.metadata.labels').find(yml)
    must_validators = []
    for match in matches:
        must_validators.append(pdb_for(object_ident(yml), match.value))
    return ([], must_validators)


@validator('Deployment', 'StatefulSet')
def podhandler_oauth(yml: object):
    """require a route with reencrypt policy if oauth was found enabled."""
    matches = json_path('spec.template.spec.containers.[*]').find(yml)
    gatekeepers = [m for m in matches
                   if 'gatekeeper' in m.value.get('image', '')]
    must_validators = []
    if gatekeepers:
        must_validators.append(
            route_for('gatekeeper', {'spec.tls.termination': 'Reencrypt'})
        )
    return ([], must_validators)


@validator('StatefulSet')
def backup_stateful(yml: object):
    """Enforce backup annotations for StatefulSet volumeClaimTemplates."""
    matches = json_path('spec.volumeClaimTemplates.[*]').find(yml)
    must_validators = []
    for match in matches:
        name = match.value.get('metadata', {}).get('name')
        must_validators.append(velero_for(name))
    return ([], must_validators)
