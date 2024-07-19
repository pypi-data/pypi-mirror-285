from setuptools import setup, find_packages

# Read requirements.txt and store its contents in the 'requirements' variable
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# Read the content of REAMDE file.
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='AssayingAnomalies',
    version='2.0.5',
    author='Joshua Lawson',
    author_email='jlaws13@simon.rochester.edu',
    description='This library is a Python implementation of the MATLAB Toolkit that accompanies Novy-Marx and Velikov '
                '(2023) and is to be used for empirical academic asset pricing research, particularly focused on '
                'studying anomalies in the cross-section of stock returns.',
    packages=find_packages(),
    package_data={
        'AssayingAnomalies': ['Gibbs/*', 'High-frequency effective spreads/*'],
    },
    install_requires=requirements,
    # long_description='Package installed successfully. Please run \'setup_library\' to configure your settings and '
    #                  'begin using the toolkit'
    long_description=long_description,
    long_description_content_type="text/markdown"
)

