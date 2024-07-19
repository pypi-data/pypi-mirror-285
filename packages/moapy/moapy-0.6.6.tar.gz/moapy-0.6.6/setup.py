from setuptools import setup, find_packages
import toml

def readme():
    with open('README_en.md', encoding='utf-8') as f:
        return f.read()

def parse_pipfile(filename):
    """Load requirements from a Pipfile."""
    with open(filename, 'r') as pipfile:
        pipfile_data = toml.load(pipfile)

    requirements = {
        'full': []
    }
    for package, details in pipfile_data.get('packages', {}).items():
        if isinstance(details, dict):
            version = details.get('version', '')
        else:
            version = details

        requirements['full'].append(f"{package}")

    return requirements

setup(
    name='moapy',
    version='0.6.6',
    packages=find_packages(),
    include_package_data=True,
    description='Midas Open API for Python',
    long_description=readme(),
    long_description_content_type='text/markdown',
    license='MIT',
    author='bschoi',
    url='https://github.com/MIDASIT-Co-Ltd/engineers-api-python',
    install_requires=['mdutils', "numpy", "matplotlib"],
    extras_require=parse_pipfile('Pipfile')
)
