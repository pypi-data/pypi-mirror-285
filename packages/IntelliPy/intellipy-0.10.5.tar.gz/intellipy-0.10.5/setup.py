# setup.py
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="IntelliPy",
    version="0.10.5",
    author="Nicolas Ruffini",
    author_email="n.ruffini@gmx.de",
    description="Automatic IntelliCage data analysis using Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NiRuff/IntelliPy",
    packages=["intellipy"],
    install_requires=["numpy>=2.0.0", "pandas>=2.2.2", "xlsxwriter>=3.2.0", "matplotlib>=3.9.1", "seaborn>=0.13.2"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)
