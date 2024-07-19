from setuptools import setup, find_packages

setup(
    name='testTutor',
    version='1.0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'testTutor=testTutor.main:main',
        ],
    },
)
