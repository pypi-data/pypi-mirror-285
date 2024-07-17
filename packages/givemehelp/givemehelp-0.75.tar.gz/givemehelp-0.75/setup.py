from setuptools import setup, find_packages
from setuptools.command.install import install
import subprocess
import sys

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        subprocess.check_call([sys.executable, '-m', 'spacy', 'download', 'en_core_web_md'])

setup(
    name='givemehelp',
    version='0.75',
    packages=find_packages(),
    install_requires=[
        'openai',
        'boto3',
        'google-generativeai',
        'spacy',
        'jsonschema'
    ],
    entry_points={
        "console_scripts": [
            "givemehelp = givemehelp:retreiveSecretKey",
        ],
    },
    cmdclass={
        'install': PostInstallCommand,
    },
)
