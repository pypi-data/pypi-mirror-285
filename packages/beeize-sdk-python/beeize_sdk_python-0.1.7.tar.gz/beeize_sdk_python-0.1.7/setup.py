from setuptools import setup, find_packages

setup(
    name='beeize-sdk-python',
    version='0.1.7',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    description="",
    author="",
    author_email="",
    url="",
)

"""
python setup.py sdist

pip install twine
twine upload dist/*

pip install ./dist/beeize-sdk-python-0.1.0.tar.gz
"""
