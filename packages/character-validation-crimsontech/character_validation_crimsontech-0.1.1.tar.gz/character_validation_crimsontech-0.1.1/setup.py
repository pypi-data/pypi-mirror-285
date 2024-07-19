from setuptools import setup, find_packages

setup(
    name='character_validation_crimsontech',
    version='0.1.1',
    packages=find_packages(exclude=['tests*', "debug_inputs"]),
    author="Crimson Tech",
    description="Character validation using morphological operations",
)