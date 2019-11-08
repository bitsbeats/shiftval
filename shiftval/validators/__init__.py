import os
import typing


collected_validators: typing.List[typing.Callable] = []


if not os.environ.get('SHIFTVAL_SKIP_DEFAULT', None):
    from shiftval.validators import for_
    from shiftval.validators import podhandler
    from shiftval.validators import route
    from shiftval.validators import statefulset
    from shiftval.validators import velero
