from setuptools import setup

setup(
    name='drunkard-cli',
    version='0.1.0',
    packages=['drunkard'],
    entry_points={
        'console_scripts': [
            'drunkard-cli=drunkard.main:cli'
        ]
    }
)
