from setuptools import setup
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

packages = \
['mysqlSaver']

package_data = \
{'': ['*']}


setup_kwargs = {
    'name' :'mysqlSaver',
    'version':'0.0.6',
    'author':'Kasra Khaksar',
    'author_email':'kasrakhaksar17@gmail.com',
    'description':'This is mysql package that you can save dataframe as table, partition, update and primarykey in mysql',
    "long_description" : long_description,
    "long_description_content_type" :'text/markdown',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9',
}


setup(**setup_kwargs)