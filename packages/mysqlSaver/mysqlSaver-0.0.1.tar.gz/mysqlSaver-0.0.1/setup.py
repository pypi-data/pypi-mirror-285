from setuptools import setup
from setuptools import find_packages

setup(
    name='mysqlSaver',
    version='0.0.1',
    author='Kasra Khaksar',
    author_email='kasrakhaksar17@gmail.com',
    description='This is mysql package that you can save dataframe as table, partision, update and primary key in mysql',
    packages=find_packages(),
    python_requires='>=3.9',
)