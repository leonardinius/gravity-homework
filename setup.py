from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

setup(
    name='homework',
    version='0.1.0',
    description='Gravity homework',
    long_description=readme,
    author='Leo',
    author_email='leonidms@gmail.com',
    url='NaN',
    license=license,
    packages=find_packages(exclude=('tests'))
)
