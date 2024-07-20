import setuptools


setuptools.setup(
    name = "a2gpipelines",
    version = "0.0.14",
    author = "DaniloAraneda",
    author_email = "danilo@alert2gain.com",
    description = "short package description",
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir = {"": "src"},
    packages = setuptools.find_packages(where="src"),
    include_dirs=[],
    python_requires = ">=3.10.7",
    requires=[]
)