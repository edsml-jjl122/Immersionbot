from setuptools import setup, find_packages


def read_lines(text_doc: str):
    """Read lines from requirements.txt and return a list of packages"""
    with open(text_doc) as req:
        packages = []
        for line in req:
            packages.append(line.split("==")[0])
    return packages


setup(
    name="IMMERSIONBOT",
    packages=find_packages(),
    install_requires=read_lines("requirements.txt"),
)