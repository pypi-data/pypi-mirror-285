from setuptools import setup, find_packages

with open("README.md","r") as f:
    description = f.read()

setup(
    name='venkat_int_methods',
    version='1.0',
    packages=find_packages(),
    install_requires = [],
    entry_points = {
        "console_scripts" : []
    },
    long_description= description,
    long_description_content_type = "text/markdown",

)