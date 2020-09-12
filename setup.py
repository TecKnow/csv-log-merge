import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="csv-log-merge",
    version="0.0.1",
    author="David P. Perkins",
    author_email="david.perkins@grumbleware.com",
    description="A package for merging multiple CSV log files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TecKnow/csv-log-merge",
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
