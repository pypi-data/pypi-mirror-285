from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

requirements = ["itchat",] 

setup(
    name="itchat-helper",
    version="0.1.0",
    author="Tao Xiang",
    author_email="tao.xiang@tum.de",
    description="",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
  "Programming Language :: Python :: 3",
  "License :: OSI Approved :: MIT License",
    ],
)