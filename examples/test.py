import os
os.environ['SHIFTVAL_SKIP_DEFAULT'] = 'true'

from shiftval.validators import collected_validators
from shiftval.helpers import validator
from shiftval.errors import LintError
from shiftval.cli import main


@validator('Pod')
def pod_true_check(yml: object):
    """
    A description that gets displayed when a lint error happens.
    """
    if not yml.get('metadata', None):
        raise LintError('Metadata missing')


main()
