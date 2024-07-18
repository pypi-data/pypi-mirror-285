import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MariaDB-Context-Manager",
    version="0.1.7",
    author="Antony",
    author_email="antonygradillas@gmail.com",
    description="A context manager to use with Python to easily connect and run querries in MariaDB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://pypi.python.org/pypi/MariaDB-Context-Manager',
    project_urls={
        "Bug Tracker": "https://github.com/avgra3/MariaDB-Context-Manager/issues",
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
