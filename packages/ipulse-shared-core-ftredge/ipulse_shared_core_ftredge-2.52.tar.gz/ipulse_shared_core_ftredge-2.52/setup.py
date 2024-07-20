# pylint: disable=import-error
from setuptools import setup, find_packages

setup(
    name='ipulse_shared_core_ftredge',
    version='2.52',
    package_dir={'': 'src'},  # Specify the source directory
    packages=find_packages(where='src'),  # Look for packages in 'src'
    install_requires=[
        # List your dependencies here
        'pydantic[email]~=2.5',
        'python-dateutil~=2.8',
        'pytest~=7.1',
        'google-cloud-logging~=3.10.0',
        'google-cloud-error-reporting~=1.11.0',
        'google-cloud-bigquery~=3.24.0'
    ],
    author='Russlan Ramdowar',
    description='Shared Core models and Logger util for the Pulse platform project. Using AI for financial advisory and investment management.',
    url='https://github.com/TheFutureEdge/ipulse_shared_core',
)