# shiftval validates K8s and Openshift resources

## Default usage

You can go ahead and use the defaults we use and validate your projects:

 * `cat manifest.yml | shiftval` for normal *manifests*
 * `helm template [cart]` for *helm* charts
 * `kustomize build [path]` for k8s *kustomize*

## Custom usage

If you want to add some custom tests you can write your own python file:

```python
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
```

For colorful output, have a look at `click`.

To skip the default tests you can setup a env variable, i.e.:

```python
import os
os.environ['SHIFTVAL_SKIP_DEFAULT'] = 'true'
```

**Example**:

```bash
python test.py <<EOF
apiVersion: v1
kind: Pod
spec:
  containers:
    - image: busybox
	  command: sleep 3600
EOF
```

```
* Metadata missing
  | A description that gets displayed when a lint error happens.
```

## Installation

I like to use virtualenv to install python packages.

```sh
# use any directory you like
cd ~/Apps

# create virtualenv
python3 -m venv shiftval
. shiftval/bin/activate

# install shiftval
git clone https://github.com/bitsbeats/shiftval shiftval/repo
pip install -e shiftval/repo

# add alias to bashrc
echo "alias shiftval=\"$PWD/shiftval/bin/shiftval\"" >> ~/.bashrc
```

You can now use the package with the command `shiftval`.

## Update

```sh
cd ~/Apps/shiftval/repo
git pull
```
