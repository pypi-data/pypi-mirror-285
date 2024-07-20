from setuptools import setup, find_packages

setup(
    name='py_currency_fetcher',
    version='0.8',
    packages=find_packages(),
    install_requires=[
        'pycountry>=20.7.3'
    ],
    author='Volodymyr Lekhman',
    author_email='volodya.l@yahoo.com',
    description='A simple package to fetch py_currency_fetcher by country code',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)
