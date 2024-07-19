from setuptools import setup, find_packages

setup(
    name='SlopeStability',
    version='0.9.3',
    description='A package for determining factor of safety for critical slip circle using stability charts',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'SlopeStability': ['Data/*.xlsx'],  # Adjust the pattern to match your files
    },
    install_requires=[
        'numpy',
        'pandas',
        'openpyxl',
        'matplotlib',
        # Add other dependencies here
    ],
)
