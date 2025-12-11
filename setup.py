# setup.py

from setuptools import setup, find_packages

from scAutoPipeline.__init__ import __VERSION__


setup(
    name="scAutoPipeline",
    version=__VERSION__,
    description="scAutoPipeline for single cell RNA Auto Pipline",
    author="liuchenglong",
    author_email="njlcl@outlook.com",
    install_requires=[
        "pyyaml",
        "numpy",
        "pandas",
        "matplotlib",
        "ruamel.yaml",
    ],
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "scAutoPipeline = scAutoPipeline.scAutoPipeline:main",
        ],
    },
    include_package_data=True,
)
