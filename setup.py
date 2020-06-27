import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cperkins-CSV-log", # Replace with your own username
    version="0.0.1",
    author="Casey Perkins",
    author_email="perkinscc07@gmail.com",
    description="A package for managing multiple CSV log files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TecKnow/cperkins-csv-log",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)