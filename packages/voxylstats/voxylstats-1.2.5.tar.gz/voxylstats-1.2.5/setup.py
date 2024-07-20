from setuptools import setup, find_packages
import pathlib


HERE = pathlib.Path(__file__).parent
with open(f"{HERE}/README.md") as f:
    README = f.read()


setup(
    name="voxylstats",
    version="1.2.5",
    description="A simple python wrapper for the Voxyl API",
    long_description=README,
    author="_lightninq & firestarad",
    license="MIT",
    packages=["voxyl", "voxyl.models", "voxyl.models.games"],
)
