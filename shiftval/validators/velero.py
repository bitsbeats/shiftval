from jsonpath_ng import parse as json_path
from shiftval.helpers import validator
from shiftval.validators.for_ import velero_for

@validator('PersistentVolumeClaim')
def backup_pvc(yml: object):
    """Enforce backup annotations for PersistentVolumeClaims."""
    name = yml.get('metadata', {}).get('name')
    return ([], [velero_for(name)])
