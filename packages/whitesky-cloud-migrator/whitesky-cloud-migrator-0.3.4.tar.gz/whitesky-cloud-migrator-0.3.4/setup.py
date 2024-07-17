from setuptools import setup, find_packages
import subprocess

VERSION = subprocess.run(
    "cat VERSION || git describe --tags 2>/dev/null || \
    git branch | grep \\* | cut -d ' ' -f2",
    shell=True,
    stdout=subprocess.PIPE,
).stdout.decode("utf8")


setup(
    name='whitesky-cloud-migrator',
    version=VERSION,
    packages=find_packages(),
    py_modules=['wscm'],
    include_package_data=True,
    install_requires=[
        # This will read the dependencies from your requirements.txt file
        requirement.strip() for requirement in open('requirements.txt')
    ],
    entry_points={
        'console_scripts': [
            'wscm=wscm:main',
        ],
    },
    package_data={
        '': ['env.sh'],
    },
    author='Geert Audenaert',
    author_email='geert.audenaert@whitesky.cloud',
    description='A Python program to migrate servers to whitesky.cloud',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://whitesky.cloud',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
