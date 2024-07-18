from setuptools import setup, find_packages

# Read the README.md file
with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name = "dwainesqol",
    version= "0.2.1",
    packages = find_packages(),
    install_requires = [

    ],

    long_description=long_description,
    long_description_content_type="text/markdown",

    
)