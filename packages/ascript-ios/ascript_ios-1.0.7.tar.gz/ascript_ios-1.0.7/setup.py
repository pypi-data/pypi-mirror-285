from setuptools import setup, find_packages
from pip._internal.req import req_file
from setuptools.glob import glob

VERSION = '1.0.7'
DESCRIPTION = 'ascript IOS python库'
is_tip = False
include_data = True
libname = "ascript-ios"
requirments = req_file.parse_requirements('requirements.txt', session='hack')
instll_requires = [req.requirement for req in requirments]

if is_tip:
    libname = libname+"-ios"
    instll_requires = []

setup(
    name=libname,
    version=VERSION,
    author="aojoy",
    author_email="aojoytec@163.com",
    description=DESCRIPTION,
    include_package_data=include_data,
    long_description_content_type="text/markdown",
    long_description=open('README.md', encoding="UTF8").read(),
    packages=find_packages(),
    keywords=['python', "ascript"],
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    url="https://airscript.cn/",
    install_requires=instll_requires,
)
