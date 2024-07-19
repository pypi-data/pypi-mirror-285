from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open("LICENSE", "r") as fh:
    license_text = fh.read()

setup(
    name='PyGUIBuilder',
    version='1.3',
    packages=find_packages(),
    author='Artem Panov',
    author_email='panovartem690@gmail.com',
    description='A simple library for creating GUI applications',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/ArtemP36/PyGUIBuilder',
    python_requires='>=3.10',
    package_data={
        "PyGUIBuilder": ["PyGUIBuilder.dll"]
    },
    license=license_text
)