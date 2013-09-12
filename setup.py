from setuptools import setup, find_packages
import os

here = os.path.dirname(__file__)
readme = open(os.path.join(here, "README.rst")).read()

setup(
    name="kishimenpy",
    author="drillbits",
    author_email="neji@drillbits.jp",
    version="0.0.1",
    description="niconico downloader",
    long_description=readme,
    license="MIT License",
    package_dir={"": "src"},
    packages=find_packages("src"),
    install_requires=[
        "requests",
    ],
    tests_require=[],
    entry_points={
        "console_scripts": [
            "kishimenpy=kishimenpy.commands:main",
        ],
    },
)
