from setuptools import setup, find_packages

setup(
    name="custom-str",
    version="0.1.2",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
