from setuptools import setup, find_packages

setup(
    name="bittest",
    version="0.0.3",
    license="MIT",
    author="Nikoloz Shubladze",
    author_email="shubnika1@gmail.com",
    description="Extract results from Jupyter notebooks",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/elnika1/bittest",
    packages=find_packages(include=["bittest"]),
    include_package_data=True
)
