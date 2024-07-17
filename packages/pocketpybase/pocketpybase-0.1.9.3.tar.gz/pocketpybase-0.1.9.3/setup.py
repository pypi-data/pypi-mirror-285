from setuptools import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()
setup(
    name='pocketpybase',
    version='0.1.9.3',
    description='A Python package for interacting with PocketBase',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Champ',
    author_email='cs@two02.io',
    packages=['pocketbase', 'pocketbase.deps', 'pocketbase.db'],
    install_requires=[
        'httpx',
    ],
)