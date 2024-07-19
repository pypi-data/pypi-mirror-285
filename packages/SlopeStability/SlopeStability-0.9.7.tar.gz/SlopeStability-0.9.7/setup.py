from setuptools import setup, find_packages

with open("README.md","r") as f:
    description = f.read() 

setup(
    name='SlopeStability',
    version='0.9.7',
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
    long_description=description,
    long_description_content_type="text/markdown",
)
