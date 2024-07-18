from setuptools import setup, find_packages

setup(
    name='SlopeStability',
    version='0.6',
    description='A package for determining factor of safety for critical slip circle using stability charts',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'openpyxl',
        'matplotlib',
        # Add other dependencies here
    ],
)
