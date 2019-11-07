import io

from setuptools import find_packages, setup

with io.open('README.md', 'rt', encoding='utf-8') as f:
    readme = f.read()

setup(
    name='shiftval',
    project_urls={
        'Code': 'https://github.com/bitsbeats/shiftval'
    },
    license='APACHE 2.0',
    author='foosinn',
    description='k8s resource validation',
    long_description=readme,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click>=7.0',
        'jsonpath-ng>=1.4',
        'pyyaml>=5.1',
    ],
    entry_points={
        "console_scripts": [
            'shiftval = shiftval.cli:main'
        ]
    }
)
