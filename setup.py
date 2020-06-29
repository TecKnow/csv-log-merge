import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cperkins-CSV-log",
    version="0.0.1",
    author="Casey Perkins",
    author_email="perkinscc07@gmail.com",
    description="A package for managing multiple CSV log files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TecKnow/cperkins-csv-log",
    packages=setuptools.find_packages(where='src'),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha",
    ],
    python_requires='>=3.6',
    entry_points={
        "console_scripts": ["logmerge-csv=csvlog.command_line:main"],
    },
)
