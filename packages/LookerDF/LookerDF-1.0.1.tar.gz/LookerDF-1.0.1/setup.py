from setuptools import setup, find_packages

setup(
    name='LookerDF',
    version='1.0.1',
    description='Simple get data from Looker API into Pandas dataframe',
    author='Pongsakorn Nimphaya',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    python_requires='>=3.6',
)