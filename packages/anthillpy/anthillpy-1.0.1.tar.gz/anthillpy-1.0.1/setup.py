import pathlib
import re

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

here = pathlib.Path(__file__).parent.resolve()  # current path
long_description = (here / "README.md").read_text(encoding="utf-8")
with open(here / "requirements.txt") as fp:
    install_reqs = [r.rstrip() for r in fp.readlines() if not r.startswith("#")]


def get_version():
    file = here / "src/anthillpy/__init__.py"
    return re.search(
        r'^__version__ = [\'"]([^\'"]*)[\'"]', file.read_text(), re.M
    )[1]


setup(
    name="anthillpy",
    version=get_version(),
    description="Hollow anthillpy package to extend n0s1.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://spark1.us/n0s1",
    author="Spark 1",
    author_email="contact@spark1.us",
    classifiers=["Development Status :: 3 - Alpha",
                 "Intended Audience :: Developers",
                 "Intended Audience :: Information Technology",
                 "Operating System :: OS Independent",
                 "Topic :: Security",
                 "Topic :: Software Development",
                 "Topic :: System :: Monitoring",
                 "Topic :: Utilities",
                 "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
                 "Programming Language :: Python :: 3.9",
                 "Programming Language :: Python :: 3.10",
                 "Programming Language :: Python :: 3.11",
                 ],  # Classifiers help users find your project by categorizing it https://pypi.org/classifiers/
    keywords="n0s1",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.9, <4",

    # For an analysis of "install_requires" vs pip's requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=install_reqs,

    include_package_data=True,
    package_data={"anthillpy": ["mock.json"],
                  },

)
