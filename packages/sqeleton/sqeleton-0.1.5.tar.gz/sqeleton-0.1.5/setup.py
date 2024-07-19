# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sqeleton', 'sqeleton.abcs', 'sqeleton.databases', 'sqeleton.queries']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1', 'dsnparse', 'rich', 'runtype>=0.5.0', 'toml>=0.10.2']

extras_require = \
{'clickhouse': ['clickhouse-driver'],
 'duckdb': ['duckdb>=0.7.0'],
 'mysql': ['mysql-connector-python>=8.0.29'],
 'postgresql': ['psycopg2'],
 'presto': ['presto-python-client'],
 'snowflake': ['snowflake-connector-python>=2.7.2', 'cryptography'],
 'trino': ['trino>=0.314.0'],
 'tui': ['textual>=0.9.1',
         'textual-select',
         'pygments>=2.13.0',
         'prompt-toolkit>=3.0.36']}

entry_points = \
{'console_scripts': ['sqeleton = sqeleton.__main__:main']}

setup_kwargs = {
    'name': 'sqeleton',
    'version': '0.1.5',
    'description': 'Python library for querying SQL databases',
    'long_description': '# Sqeleton\n\nSqeleton is a Python library for querying SQL databases.\n\nIt consists of -\n\n- A fast and concise query builder, designed from scratch, but inspired by PyPika and SQLAlchemy\n\n- A modular database interface, with drivers for a long list of SQL databases.\n\nIt is comparable to other libraries such as SQLAlchemy or PyPika, in terms of API and intended audience. However, there are several notable ways in which it is different. \n\n## **Features:**\n\n🏃\u200d♂️**High-performance**: Sqeleton\'s API is designed to maximize performance using batch operations\n\n- No ORM! While ORMs are easy and familiar, their granular operations are far too slow.\n- Compiles queries 4 times faster than SQLAlchemy\n\n🙌**Parallel**: Seamless multi-threading and multi-processing support\n\n💖**Well-tested**: In addition to having an extensive test-suite, sqeleton is used as the core of [data-diff](https://github.com/datafold/data-diff).\n\n✅**Type-aware**: The schema is used for validation when building expressions, making sure the names are correct, and that the data-types align. (WIP)\n    \n- The schema can be queried at run-time, if the tables already exist in the database\n\n✨**Multi-database access**: Sqeleton is designed to work with several databases at the same time. Its API abstracts away as many implementation details as possible.\n\n_Databases we fully support_:\n\n- PostgreSQL >=10\n- MySQL\n- Snowflake\n- BigQuery\n- Redshift\n- Oracle\n- Presto\n- Databricks\n- Trino\n- Clickhouse\n- Vertica\n- DuckDB >=0.6\n- SQLite (coming soon)\n\n💻**Built-in SQL client**: Connect to any of the supported databases with just one line.\n\nExample usage: `sqeleton repl snowflake://...`\n\n- Has syntax-highlighting, and autocomplete\n- Use `*text` to find all tables like `%text%` (or just `*` to see all tables)\n- Use `?name` to see the schema of the table called `name`.\n\n## Documentation\n\n[Read the docs!](https://sqeleton.readthedocs.io)\n\nOr jump straight to the [introduction](https://sqeleton.readthedocs.io/en/latest/intro.html).\n\n### Install\n\nInstall using pip:\n\n```bash\npip install sqeleton\n```\n\nIt is recommended to install the driver dependencies using pip\'s `[]` syntax:\n\n```bash\npip install \'sqeleton[mysql, postgresql]\'\n```\n\nRead more in [install / getting started.](https://sqeleton.readthedocs.io/en/latest/install.html)\n\n### Example: Basic usage\n\nWe will create a table with the numbers 0..100, and then sum them up.\n\n```python\nfrom sqeleton import connect, table, this\n\n# Create a new database connection\nddb = connect("duckdb://:memory:")\n\n# Define a table with one int column\ntbl = table(\'my_list\', schema={\'item\': int})\n\n# Make a bunch of queries\nqueries = [\n    # Create table \'my_list\'\n    tbl.create(),\n\n    # Insert 100 numbers\n    tbl.insert_rows([x] for x in range(100)),\n\n    # Get the sum of the numbers\n    tbl.select(this.item.sum())\n]\n# Query in order, and return the last result as an int\nresult = ddb.query(queries, int)    \n\n# Prints: Total sum of 0..100 = 4950\nprint(f"Total sum of 0..100 = {result}")\n```\n\n### Example: Advanced usage\n\nWe will define a function that performs outer-join on any database, and adds two extra fields: `only_a` and `only_b`.\n\n```python\nfrom sqeleton.databases import Database\nfrom sqeleton.queries import ITable, leftjoin, rightjoin, outerjoin, and_, Expr\n\ndef my_outerjoin(\n        db: Database,\n        a: ITable, b: ITable,\n        keys1: List[str], keys2: List[str],\n        select_fields: Dict[str, Expr]\n    ) -> ITable:\n    """This function accepts two table expressions, and returns an outer-join query.\n    \n    The resulting rows will include two extra boolean fields:\n    "only_a", and "only_b", describing whether there was a match for that row \n    only in the first table, or only in the second table.\n\n    Parameters:\n        db - the database connection to use\n        a, b - the tables to outer-join\n        keys1, keys2 - the names of the columns to join on, for each table respectively\n        select_fields - A dictionary of {column_name: expression} to select as a result of the outer-join\n    """\n    # Predicates to join on\n    on = [a[k1] == b[k2] for k1, k2 in zip(keys1, keys2)]\n\n    # Define the new boolean fields\n    # If all keys are None, it means there was no match\n    # Compiles to "<k1> IS NULL AND <k2> IS NULL AND <k3> IS NULL..." etc.\n    only_a = and_(b[k] == None for k in keys2)\n    only_b = and_(a[k] == None for k in keys1)\n\n    if isinstance(db, MySQL):\n        # MySQL doesn\'t support "outer join"\n        # Instead, we union "left join" and "right join"\n        l = leftjoin(a, b).on(*on).select(\n                only_a=only_a,\n                only_b=False,\n                **select_fields\n            )\n        r = rightjoin(a, b).on(*on).select(\n                only_a=False,\n                only_b=only_b,\n                **select_fields\n            )\n        return l.union(r)\n\n    # Other databases\n    return outerjoin(a, b).on(*on).select(\n            only_a=only_a,\n            only_b=only_b,\n            **select_fields\n        )\n```\n\n\n\n# TODO\n\n- Transactions\n\n- Indexes\n\n- Date/time expressions\n\n- Window functions\n\n## Possible plans for the future (not determined yet)\n\n- Cache the compilation of repetitive queries for even faster query-building\n\n- Compile control flow, functions\n\n- Define tables using type-annotated classes (SQLModel style)\n\n## Alternatives\n\n- [SQLAlchemy](https://www.sqlalchemy.org/)\n- [PyPika](https://github.com/kayak/pypika)\n- [PonyORM](https://ponyorm.org/)\n- [peewee](https://github.com/coleifer/peewee)\n\n# Thanks\n\nThanks to Datafold for having sponsored Sqeleton in its initial stages. For reference, [the original repo](https://github.com/datafold/sqeleton/).',
    'author': 'Erez Shinan',
    'author_email': 'erezshin@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/erezsh/sqeleton',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
