from jsonpath_ng import parse as json_path

from shiftval.helpers import validator
from shiftval.validators.for_ import velero_for


@validator('StatefulSet')
def backup_stateful(yml: object):
    """Enforce backup annotations for StatefulSet volumeClaimTemplates."""
    matches = json_path('spec.volumeClaimTemplates.[*]').find(yml)
    must_validators = []
    for match in matches:
        name = match.value.get('metadata', {}).get('name')
        must_validators.append(velero_for(name))
    return ([], must_validators)
