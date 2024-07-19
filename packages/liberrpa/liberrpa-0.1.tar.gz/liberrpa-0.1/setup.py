from setuptools import setup, find_packages

setup(
    name="liberrpa",
    version="0.01",
    packages=find_packages(),
    install_requires=[],
    author="HUHARED",
    author_email="mailwork.hu@gmail.com",
    description="This is the main library for LiberRPA.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/HUHARED/liberrpa",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: Microsoft :: Windows :: Windows 11",
    ],
    python_requires=">=3.11",
)
