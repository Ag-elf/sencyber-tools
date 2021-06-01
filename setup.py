# -*- coding: utf-8 -*-
# @Time     : 2021/6/1 10:23
# @Author   : Shigure_Hotaru
# @Email    : minjie96@sencyber.cn
# @File     : setup.py
# @Version  : Python 3.8.5 +

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sencyber-tools-minjie96",
    version="0.0.1",
    author="minjie96",
    author_email="minjie96@sencyber.cn",
    description="Sencyber Tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ag-elf/sencyber-tools",
    project_urls={
        "Bug Tracker": "https://github.com/Ag-elf/sencyber-tools/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
)